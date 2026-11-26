--!strict
-- UIController (CLIENTE): crea el HUD principal.
--   • Contador de Perlas arriba a la izquierda (con animación al subir).
--   • Avisos ("toasts") arriba al centro cuando el servidor manda "Notify".
--   • Botón de prueba "+10 Perlas" que SOLO aparece en Roblox Studio.
-- La interfaz se crea por código para que Rojo la sincronice; más adelante la pasaremos a plantillas.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Net = require(Shared:WaitForChild("Net") :: ModuleScript)
local UIStyle = require(Shared:WaitForChild("UIStyle") :: ModuleScript)

local player = Players.LocalPlayer

local UIController = {}

local screenGui: ScreenGui
local pearlsLabel: TextLabel
local pearlsFrame: Frame
local toastLabel: TextLabel
local toastToken = 0

local function formatNumber(n: number): string
	-- 12345 → "12.345"
	local text = tostring(math.floor(n))
	local formatted = text:reverse():gsub("(%d%d%d)", "%1."):reverse()
	if formatted:sub(1, 1) == "." then
		formatted = formatted:sub(2)
	end
	return formatted
end

local function buildPearlCounter()
	pearlsFrame = Instance.new("Frame")
	pearlsFrame.Name = "Pearls"
	pearlsFrame.AnchorPoint = Vector2.new(0, 0)
	pearlsFrame.Position = UDim2.new(0, 16, 0, 16)
	pearlsFrame.Size = UDim2.new(0, 190, 0, 56)
	pearlsFrame.BackgroundColor3 = UIStyle.Colors.Turquoise
	UIStyle.Round(pearlsFrame, 18)
	UIStyle.Outline(pearlsFrame, 4)
	pearlsFrame.Parent = screenGui

	-- Icono de perla: un círculo con degradado (no necesitamos imágenes todavía).
	local icon = Instance.new("Frame")
	icon.Name = "Icon"
	icon.AnchorPoint = Vector2.new(0, 0.5)
	icon.Position = UDim2.new(0, 10, 0.5, 0)
	icon.Size = UDim2.new(0, 38, 0, 38)
	icon.BackgroundColor3 = UIStyle.Colors.Pearl
	UIStyle.Circle(icon)
	UIStyle.Outline(icon, 3)
	local gradient = Instance.new("UIGradient")
	gradient.Color = ColorSequence.new(Color3.fromRGB(255, 255, 255), Color3.fromRGB(200, 185, 255))
	gradient.Rotation = 45
	gradient.Parent = icon
	icon.Parent = pearlsFrame

	pearlsLabel = UIStyle.Label({
		Text = "…",
		Position = UDim2.new(0, 56, 0, 6),
		Size = UDim2.new(1, -66, 1, -12),
		Parent = pearlsFrame,
	})
	pearlsLabel.Name = "Amount"
	pearlsLabel.TextXAlignment = Enum.TextXAlignment.Left
end

local lastPearls: number? = nil
local function updatePearls()
	local value = player:GetAttribute("Pearls")
	if typeof(value) ~= "number" then
		pearlsLabel.Text = "…"
		return
	end
	pearlsLabel.Text = formatNumber(value)

	-- Pequeño "salto" cuando suben las Perlas.
	if lastPearls and value > lastPearls then
		local scale = pearlsFrame:FindFirstChildOfClass("UIScale") or Instance.new("UIScale")
		scale.Parent = pearlsFrame
		scale.Scale = 1.15
		TweenService:Create(scale, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	end
	lastPearls = value
end

local function buildToast()
	toastLabel = UIStyle.Label({
		Text = "",
		Size = UDim2.new(0, 420, 0, 50),
		Position = UDim2.new(0.5, 0, 0, -80),
		Parent = screenGui,
	})
	toastLabel.Name = "Toast"
	toastLabel.AnchorPoint = Vector2.new(0.5, 0)
	toastLabel.BackgroundTransparency = 0
	toastLabel.BackgroundColor3 = UIStyle.Colors.Coral
	UIStyle.Round(toastLabel, 16)
	local padding = Instance.new("UIPadding")
	padding.PaddingTop = UDim.new(0, 8)
	padding.PaddingBottom = UDim.new(0, 8)
	padding.PaddingLeft = UDim.new(0, 16)
	padding.PaddingRight = UDim.new(0, 16)
	padding.Parent = toastLabel
	toastLabel.Visible = false
end

-- Muestra un aviso arriba de la pantalla durante unos segundos.
function UIController.ShowToast(text: string, duration: number?)
	toastToken += 1
	local myToken = toastToken
	toastLabel.Text = text
	toastLabel.Visible = true
	toastLabel.Position = UDim2.new(0.5, 0, 0, -80)
	TweenService:Create(toastLabel, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
		Position = UDim2.new(0.5, 0, 0, 16),
	}):Play()

	task.delay(duration or 2.5, function()
		if myToken ~= toastToken then
			return -- ya apareció otro aviso encima
		end
		local tween = TweenService:Create(toastLabel, TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
			Position = UDim2.new(0.5, 0, 0, -80),
		})
		tween:Play()
		tween.Completed:Wait()
		if myToken == toastToken then
			toastLabel.Visible = false
		end
	end)
end

local function buildDebugButton()
	local button = UIStyle.Button({
		Text = "+10 Perlas (prueba)",
		Size = UDim2.new(0, 220, 0, 60),
		Position = UDim2.new(1, -236, 1, -150),
		Color = UIStyle.Colors.Gold,
		Parent = screenGui,
	})
	button.Name = "DebugAddPearls"
	button.Activated:Connect(function()
		Net.Fire("DebugAddPearls", 10)
	end)
end

function UIController.Init()
	screenGui = Instance.new("ScreenGui")
	screenGui.Name = "HUD"
	screenGui.ResetOnSpawn = false -- no se borra al morir
	screenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	screenGui.Parent = player:WaitForChild("PlayerGui")

	buildPearlCounter()
	buildToast()
	if RunService:IsStudio() then
		buildDebugButton()
	end
end

function UIController.Start()
	player:GetAttributeChangedSignal("Pearls"):Connect(updatePearls)
	updatePearls()

	Net.On("Notify", function(text: any)
		if typeof(text) == "string" then
			UIController.ShowToast(text)
		end
	end)
end

return UIController
