--!strict
-- DataService (SERVIDOR): carga y guarda los datos permanentes de cada jugador con ProfileStore.
-- ProfileStore se encarga de:
--   • Reintentos si Roblox falla al guardar.
--   • "Session lock": el mismo jugador no puede tener sus datos abiertos en 2 servidores a la vez
--     (evita duplicar Perlas al teletransportarse entre lobby y expedición).
--   • Auto-guardado cada pocos minutos y guardado al salir y al cerrar el servidor.
--
-- El resto del juego NUNCA toca el DataStore directamente: siempre pasa por aquí.
--   DataService.AddPearls(player, 50, "BossReward")
--   DataService.SpendPearls(player, 150, "BuyClass")  → true/false
--   DataService.GetData(player)                       → tabla de datos o nil si no ha cargado

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local ServerScriptService = game:GetService("ServerScriptService")

local DataConfig = require(ReplicatedStorage.Config.Data)
local Signal = require(ReplicatedStorage.Shared.Signal)
local Validate = require(ReplicatedStorage.Shared.Validate)

export type PlayerData = DataConfig.PlayerData

local function loadProfileStore(): any
	local packages = ServerScriptService:FindFirstChild("Packages")
	local module = packages and packages:FindFirstChild("ProfileStore")
	if not module or not module:IsA("ModuleScript") then
		error(
			"[DataService] No encuentro ProfileStore. Descarga ProfileStore.luau y guárdalo en "
				.. "src/server/Packages/ProfileStore.luau (mira el paso 3 del README)."
		)
	end
	return require(module) :: any
end

local ProfileStore = loadProfileStore()

local DataService = {}

-- Señales para que otros servicios reaccionen.
DataService.DataLoaded = Signal.new() -- (player: Player, data: PlayerData)
DataService.PearlsChanged = Signal.new() -- (player: Player, newAmount: number, delta: number, reason: string)

local profiles: { [Player]: any } = {}

local playerStore = ProfileStore.New(DataConfig.StoreName, DataConfig.Template)
if RunService:IsStudio() and DataConfig.UseMockInStudio then
	playerStore = playerStore.Mock
	warn("[DataService] Usando datos de prueba (Mock). Nada se guarda de verdad.")
end

-- Migraciones: si algún día cambiamos el formato de los datos, aquí se actualizan los viejos.
local function migrate(data: PlayerData)
	-- Ejemplo para el futuro:
	-- if data.DataVersion < 2 then ... data.DataVersion = 2 end
	data.DataVersion = math.max(data.DataVersion, DataConfig.CurrentVersion)
end

-- Copia los datos simples como Attributes del jugador para que el cliente los vea.
-- (Los Attributes que pone el servidor no los puede cambiar el cliente.)
local function replicate(player: Player, data: PlayerData)
	local dictionary = data :: any
	for _, key in DataConfig.ReplicatedKeys do
		player:SetAttribute(key, dictionary[key])
	end
end

local function onPlayerAdded(player: Player)
	local profile = playerStore:StartSessionAsync(`Player_{player.UserId}`, {
		-- Si el jugador se va mientras carga, dejamos de intentarlo.
		Cancel = function()
			return player.Parent ~= Players
		end,
	})

	if profile == nil then
		-- Solo pasa si Roblox está caído o el jugador se fue mientras cargaba.
		if player.Parent == Players then
			player:Kick("No pudimos cargar tus datos. Vuelve a entrar en un momento, por favor. 🌊")
		end
		return
	end

	profile:AddUserId(player.UserId) -- requisito de Roblox (protección de datos / GDPR)
	profile:Reconcile() -- añade los campos nuevos de Template que le falten

	profile.OnSessionEnd:Connect(function()
		profiles[player] = nil
		if player.Parent == Players then
			player:Kick("Tu partida se abrió en otro servidor. Vuelve a entrar, por favor.")
		end
	end)

	if player.Parent ~= Players then
		-- Se fue justo mientras cargaba: cerramos la sesión para guardar y liberar el bloqueo.
		profile:EndSession()
		return
	end

	profiles[player] = profile
	migrate(profile.Data)
	replicate(player, profile.Data)
	player:SetAttribute("DataLoaded", true)
	DataService.DataLoaded:Fire(player, profile.Data)
	print(`[DataService] Datos cargados de {player.Name}: {profile.Data.Pearls} Perlas`)
end

local function onPlayerRemoving(player: Player)
	local profile = profiles[player]
	if profile then
		profile:EndSession() -- guarda y libera el bloqueo
	end
end

-- ===== API pública =====

function DataService.IsLoaded(player: Player): boolean
	return profiles[player] ~= nil
end

-- Devuelve los datos del jugador (o nil si todavía no cargan). Modifícalos solo desde el servidor.
function DataService.GetData(player: Player): PlayerData?
	local profile = profiles[player]
	return if profile then profile.Data else nil
end

-- Espera a que carguen los datos (máximo `timeout` segundos). Devuelve nil si no cargaron.
function DataService.WaitForData(player: Player, timeout: number?): PlayerData?
	local deadline = os.clock() + (timeout or 30)
	while not profiles[player] and player.Parent == Players and os.clock() < deadline do
		task.wait(0.1)
	end
	return DataService.GetData(player)
end

-- Para MonetizationService (fase 11): acceso al perfil completo (historial de compras).
function DataService.GetProfile(player: Player): any
	return profiles[player]
end

-- Suma Perlas. Devuelve true si se pudo.
function DataService.AddPearls(player: Player, amount: number, reason: string): boolean
	if not Validate.IsInteger(amount, 1, DataConfig.MaxPearls) then
		warn(`[DataService] AddPearls con cantidad inválida: {amount} ({reason})`)
		return false
	end
	local data = DataService.GetData(player)
	if not data then
		return false
	end
	data.Pearls = math.min(data.Pearls + amount, DataConfig.MaxPearls)
	player:SetAttribute("Pearls", data.Pearls)
	DataService.PearlsChanged:Fire(player, data.Pearls, amount, reason)
	return true
end

-- Gasta Perlas. Devuelve false si no tiene suficientes (y no le quita nada).
function DataService.SpendPearls(player: Player, amount: number, reason: string): boolean
	if not Validate.IsInteger(amount, 1, DataConfig.MaxPearls) then
		warn(`[DataService] SpendPearls con cantidad inválida: {amount} ({reason})`)
		return false
	end
	local data = DataService.GetData(player)
	if not data or data.Pearls < amount then
		return false
	end
	data.Pearls -= amount
	player:SetAttribute("Pearls", data.Pearls)
	DataService.PearlsChanged:Fire(player, data.Pearls, -amount, reason)
	return true
end

function DataService.Init()
	Players.PlayerAdded:Connect(onPlayerAdded)
	Players.PlayerRemoving:Connect(onPlayerRemoving)

	-- Por si algún jugador entró antes de que este script arrancara (pasa en Studio).
	for _, player in Players:GetPlayers() do
		task.spawn(onPlayerAdded, player)
	end

	-- Al cerrar el servidor, cerramos todas las sesiones para que se guarden.
	-- (ProfileStore también lo hace por su cuenta; esto es una segunda capa de seguridad.)
	game:BindToClose(function()
		for _, profile in profiles do
			if profile:IsActive() then
				profile:EndSession()
			end
		end
	end)
end

return DataService
