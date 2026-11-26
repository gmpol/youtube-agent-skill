--!strict
-- NetService (SERVIDOR): crea y protege todas las RemoteEvents/RemoteFunctions.
-- Cada remota "ToServer" pasa por:
--   1) Rate limit (si un jugador la spamea, se ignora)
--   2) Validación de argumentos (la función validate que le pases)
--   3) pcall: si tu código falla, el servidor no se rompe
--
-- Uso en otros servicios:
--   NetService.OnEvent("Nombre", function(player, a, b) ... end, function(a, b)
--       return Validate.IsInteger(a, 1, 100)   -- true = argumentos válidos
--   end)
--   NetService.FireClient("Notify", player, "¡Hola!")

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local RemoteDefinitions = require(ReplicatedStorage.Shared.RemoteDefinitions)
local RateLimiter = require(ReplicatedStorage.Shared.RateLimiter)

type Validator = (...any) -> boolean

local NetService = {}

local events: { [string]: RemoteEvent } = {}
local functions: { [string]: RemoteFunction } = {}
local limiters: { [string]: RateLimiter.RateLimiter } = {}
local connected: { [string]: boolean } = {}

-- Crear la carpeta Remotes desde cero (así nunca quedan remotas viejas o puestas a mano).
local existing = ReplicatedStorage:FindFirstChild("Remotes")
if existing then
	warn("[NetService] Ya había una carpeta Remotes en ReplicatedStorage; la reemplazo por la oficial.")
	existing:Destroy()
end

local remotesFolder = Instance.new("Folder")
remotesFolder.Name = "Remotes"

for name, definition in RemoteDefinitions.Definitions do
	if definition.Kind == "Event" then
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = remotesFolder
		events[name] = remote
	else
		local remote = Instance.new("RemoteFunction")
		remote.Name = name
		remote.Parent = remotesFolder
		functions[name] = remote
	end

	if definition.Direction == "ToServer" then
		local limit = definition.RateLimit or RemoteDefinitions.DefaultRateLimit
		limiters[name] = RateLimiter.new(limit.MaxCalls, limit.PerSeconds)
	end
end

remotesFolder.Parent = ReplicatedStorage

-- Avisos de jugadores sospechosos, sin llenar la consola (máximo 1 cada 5 s por jugador y remota).
local lastWarn: { [string]: number } = {}
local function suspicious(player: Player, remoteName: string, reason: string)
	local key = `{player.UserId}:{remoteName}`
	local now = os.clock()
	if lastWarn[key] and now - lastWarn[key] < 5 then
		return
	end
	lastWarn[key] = now
	warn(`[NetService] ⚠️ {player.Name} → {remoteName}: {reason}`)
end

local function getDefinition(name: string, expectedKind: "Event" | "Function")
	local definition = RemoteDefinitions.Definitions[name]
	assert(definition, `[NetService] La remota "{name}" no existe en RemoteDefinitions`)
	assert(definition.Kind == expectedKind, `[NetService] "{name}" no es de tipo {expectedKind}`)
	return definition
end

-- Escuchar una RemoteEvent que manda el cliente.
function NetService.OnEvent(name: string, handler: (player: Player, ...any) -> (), validate: Validator?)
	local definition = getDefinition(name, "Event")
	assert(definition.Direction == "ToServer", `[NetService] "{name}" es ToClient; el cliente no debería dispararla`)
	assert(not connected[name], `[NetService] "{name}" ya tiene un handler conectado`)
	connected[name] = true

	local limiter = limiters[name]
	events[name].OnServerEvent:Connect(function(player: Player, ...: any)
		if not limiter:Check(player) then
			suspicious(player, name, "superó el límite de uso (rate limit)")
			return
		end
		if validate then
			local okValidate, isValid = pcall(validate, ...)
			if not okValidate or not isValid then
				suspicious(player, name, "mandó argumentos inválidos")
				return
			end
		end
		local ok, err = pcall(handler, player, ...)
		if not ok then
			warn(`[NetService] ❌ Error procesando {name} de {player.Name}: {err}`)
		end
	end)
end

-- Responder a una RemoteFunction que invoca el cliente. Si algo falla, el cliente recibe nil.
function NetService.OnInvoke(name: string, handler: (player: Player, ...any) -> ...any, validate: Validator?)
	local definition = getDefinition(name, "Function")
	assert(definition.Direction == "ToServer", `[NetService] "{name}" debe ser ToServer`)
	assert(not connected[name], `[NetService] "{name}" ya tiene un handler conectado`)
	connected[name] = true

	local limiter = limiters[name]
	functions[name].OnServerInvoke = function(player: Player, ...: any): ...any
		if not limiter:Check(player) then
			suspicious(player, name, "superó el límite de uso (rate limit)")
			return nil
		end
		if validate then
			local okValidate, isValid = pcall(validate, ...)
			if not okValidate or not isValid then
				suspicious(player, name, "mandó argumentos inválidos")
				return nil
			end
		end
		local results = table.pack(pcall(handler, player, ...))
		if not results[1] then
			warn(`[NetService] ❌ Error procesando {name} de {player.Name}: {results[2]}`)
			return nil
		end
		return table.unpack(results, 2, results.n)
	end
end

-- Mandar un mensaje a un jugador.
function NetService.FireClient(name: string, player: Player, ...: any)
	getDefinition(name, "Event")
	events[name]:FireClient(player, ...)
end

-- Mandar un mensaje a todos los jugadores.
function NetService.FireAllClients(name: string, ...: any)
	getDefinition(name, "Event")
	events[name]:FireAllClients(...)
end

-- Mandar un mensaje a una lista de jugadores (por ejemplo, la tripulación).
function NetService.FireClients(name: string, players: { Player }, ...: any)
	getDefinition(name, "Event")
	for _, player in players do
		if player.Parent == Players then
			events[name]:FireClient(player, ...)
		end
	end
end

function NetService.Init()
	-- Las remotas que solo van al cliente: si un tramposo las dispara hacia el servidor, las ignoramos
	-- (conectar un handler vacío evita que Roblox acumule esos mensajes en cola).
	for name, definition in RemoteDefinitions.Definitions do
		if definition.Direction == "ToClient" then
			if definition.Kind == "Event" then
				events[name].OnServerEvent:Connect(function() end)
			else
				functions[name].OnServerInvoke = function()
					return nil
				end
			end
		end
	end

	Players.PlayerRemoving:Connect(function(player)
		for _, limiter in limiters do
			limiter:Remove(player)
		end
	end)
end

return NetService
