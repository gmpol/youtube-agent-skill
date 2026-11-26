--!strict
-- DebugService (SERVIDOR): herramientas de prueba que SOLO funcionan dentro de Roblox Studio.
-- En el juego publicado no hacen nada, aunque un tramposo dispare la remota.

local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Validate = require(ReplicatedStorage.Shared.Validate)
local NetService = require(script.Parent.NetService)
local DataService = require(script.Parent.DataService)

local DebugService = {}

function DebugService.Init()
	NetService.OnEvent("DebugAddPearls", function(player: Player, amount: number)
		if not RunService:IsStudio() then
			return -- en el juego real, ignorar
		end
		if DataService.AddPearls(player, amount, "Debug") then
			NetService.FireClient("Notify", player, `+{amount} Perlas (prueba)`)
		end
	end, function(amount)
		return Validate.IsInteger(amount, 1, 1000)
	end)
end

return DebugService
