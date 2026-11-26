--!strict
-- Net (lado CLIENTE): forma sencilla de usar las remotas desde LocalScripts.
--   Net.Fire("NombreRemota", ...)        → manda un mensaje al servidor
--   Net.On("NombreRemota", function(...) → escucha mensajes del servidor
--   Net.Invoke("NombreRemota", ...)      → pregunta al servidor y espera respuesta
-- Los nombres válidos están en Shared/RemoteDefinitions.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local RemoteDefinitions = require(script.Parent.RemoteDefinitions)

assert(RunService:IsClient(), "Net solo se usa en el cliente. En el servidor usa NetService.")

local WAIT_TIMEOUT = 15

local Net = {}

local remotesFolder: Instance? = nil

local function getRemote(name: string): Instance
	local definition = RemoteDefinitions.Definitions[name]
	if not definition then
		error(`[Net] La remota "{name}" no existe en RemoteDefinitions (¿está bien escrito el nombre?)`)
	end
	if not remotesFolder then
		remotesFolder = ReplicatedStorage:WaitForChild("Remotes", WAIT_TIMEOUT)
	end
	local folder = remotesFolder
	if not folder then
		error("[Net] No llegó la carpeta Remotes del servidor. ¿Falló el script Main del servidor?")
	end
	local remote = folder:WaitForChild(name, WAIT_TIMEOUT)
	if not remote then
		error(`[Net] No encontré la remota "{name}" en ReplicatedStorage/Remotes`)
	end
	return remote
end

function Net.Fire(name: string, ...: any)
	local remote = getRemote(name)
	assert(remote:IsA("RemoteEvent"), `[Net] "{name}" no es un RemoteEvent`)
	remote:FireServer(...)
end

function Net.On(name: string, callback: (...any) -> ()): RBXScriptConnection
	local remote = getRemote(name)
	assert(remote:IsA("RemoteEvent"), `[Net] "{name}" no es un RemoteEvent`)
	return remote.OnClientEvent:Connect(callback)
end

function Net.Invoke(name: string, ...: any): ...any
	local remote = getRemote(name)
	assert(remote:IsA("RemoteFunction"), `[Net] "{name}" no es una RemoteFunction`)
	return remote:InvokeServer(...)
end

return Net
