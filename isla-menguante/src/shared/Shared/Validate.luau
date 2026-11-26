--!strict
-- Validate: funciones para comprobar que lo que manda el cliente es válido.
-- REGLA DE ORO: el cliente puede mandar CUALQUIER cosa (un tramposo puede modificarlo),
-- así que el servidor revisa todo antes de usarlo.

local Validate = {}

-- Número normal (no NaN ni infinito). NaN es un truco típico para romper cálculos.
function Validate.IsFiniteNumber(value: any): boolean
	return typeof(value) == "number" and value == value and value ~= math.huge and value ~= -math.huge
end

-- Número entero dentro de un rango.
function Validate.IsInteger(value: any, min: number?, max: number?): boolean
	if not Validate.IsFiniteNumber(value) or value % 1 ~= 0 then
		return false
	end
	if min and value < min then
		return false
	end
	if max and value > max then
		return false
	end
	return true
end

-- Texto con un largo máximo.
function Validate.IsString(value: any, maxLength: number?): boolean
	if typeof(value) ~= "string" then
		return false
	end
	if maxLength and #value > maxLength then
		return false
	end
	return utf8.len(value) ~= nil -- descarta texto con bytes rotos
end

function Validate.IsVector3(value: any): boolean
	return typeof(value) == "Vector3"
		and Validate.IsFiniteNumber(value.X)
		and Validate.IsFiniteNumber(value.Y)
		and Validate.IsFiniteNumber(value.Z)
end

-- Comprueba que es una Instance de cierta clase y que sigue existiendo en el juego.
function Validate.IsInstanceOf(value: any, className: string): boolean
	return typeof(value) == "Instance" and value:IsA(className) and value:IsDescendantOf(game)
end

-- Comprueba que el valor está en una lista permitida.
function Validate.IsOneOf(value: any, allowed: { any }): boolean
	return table.find(allowed, value) ~= nil
end

-- Devuelve la posición del jugador (su HumanoidRootPart), o nil si no tiene personaje vivo.
function Validate.GetPlayerPosition(player: Player): Vector3?
	local character = player.Character
	if not character then
		return nil
	end
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	local root = character:FindFirstChild("HumanoidRootPart")
	if not humanoid or humanoid.Health <= 0 or not root or not root:IsA("BasePart") then
		return nil
	end
	return root.Position
end

-- Verificación de distancia: ¿el jugador está realmente cerca de esa posición?
-- Úsala siempre que el cliente diga "estoy tocando/golpeando/recogiendo X".
function Validate.IsPlayerNear(player: Player, position: Vector3, maxDistance: number): boolean
	local playerPosition = Validate.GetPlayerPosition(player)
	if not playerPosition then
		return false
	end
	return (playerPosition - position).Magnitude <= maxDistance
end

return Validate
