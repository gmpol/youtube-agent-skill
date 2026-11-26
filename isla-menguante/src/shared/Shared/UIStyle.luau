--!strict
-- UIStyle: colores y ayudas para que toda la interfaz tenga el mismo estilo caricatura
-- (esquinas redondeadas, borde grueso oscuro, letra gordita). Se usa desde el cliente.

local UIStyle = {}

UIStyle.Font = Enum.Font.FredokaOne

UIStyle.Colors = {
	Outline = Color3.fromRGB(28, 36, 64), -- azul marino casi negro para los bordes
	Panel = Color3.fromRGB(255, 248, 230), -- crema (arena)
	Text = Color3.fromRGB(255, 255, 255),
	TextDark = Color3.fromRGB(28, 36, 64),
	Turquoise = Color3.fromRGB(42, 200, 205),
	Lime = Color3.fromRGB(150, 220, 60),
	Coral = Color3.fromRGB(255, 110, 90),
	Gold = Color3.fromRGB(255, 200, 50),
	Pearl = Color3.fromRGB(240, 235, 255),
}

-- Esquinas redondeadas. radius en píxeles (o usa 0.5 de escala para un círculo).
function UIStyle.Round(parent: GuiObject, radius: number?): UICorner
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, radius or 14)
	corner.Parent = parent
	return corner
end

function UIStyle.Circle(parent: GuiObject): UICorner
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(1, 0)
	corner.Parent = parent
	return corner
end

-- Borde grueso estilo caricatura.
function UIStyle.Outline(parent: GuiObject, thickness: number?): UIStroke
	local stroke = Instance.new("UIStroke")
	stroke.Color = UIStyle.Colors.Outline
	stroke.Thickness = thickness or 3
	stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	stroke.Parent = parent
	return stroke
end

-- Contorno para el texto (se lee bien sobre cualquier fondo).
function UIStyle.TextOutline(parent: TextLabel | TextButton, thickness: number?): UIStroke
	local stroke = Instance.new("UIStroke")
	stroke.Color = UIStyle.Colors.Outline
	stroke.Thickness = thickness or 2
	stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual
	stroke.Parent = parent
	return stroke
end

-- Crea un texto con el estilo del juego.
function UIStyle.Label(props: { Text: string, Size: UDim2, Position: UDim2?, TextSize: number?, Parent: Instance? }): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Font = UIStyle.Font
	label.Text = props.Text
	label.TextColor3 = UIStyle.Colors.Text
	label.TextSize = props.TextSize or 24
	label.TextScaled = props.TextSize == nil
	label.Size = props.Size
	label.Position = props.Position or UDim2.new()
	UIStyle.TextOutline(label)
	label.Parent = props.Parent
	return label
end

-- Botón grande y redondeado (pensado para dedos en celular).
function UIStyle.Button(props: { Text: string, Size: UDim2, Position: UDim2?, Color: Color3?, Parent: Instance? }): TextButton
	local button = Instance.new("TextButton")
	button.AutoButtonColor = true
	button.BackgroundColor3 = props.Color or UIStyle.Colors.Lime
	button.Font = UIStyle.Font
	button.Text = props.Text
	button.TextColor3 = UIStyle.Colors.Text
	button.TextScaled = true
	button.Size = props.Size
	button.Position = props.Position or UDim2.new()
	UIStyle.Round(button)
	UIStyle.Outline(button, 4)
	local padding = Instance.new("UIPadding")
	padding.PaddingTop = UDim.new(0, 8)
	padding.PaddingBottom = UDim.new(0, 8)
	padding.PaddingLeft = UDim.new(0, 12)
	padding.PaddingRight = UDim.new(0, 12)
	padding.Parent = button
	button.Parent = props.Parent
	return button
end

return UIStyle
