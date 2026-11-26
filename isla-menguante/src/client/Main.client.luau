--!strict
-- Script principal del CLIENTE (tipo: LocalScript, en StarterPlayer/StarterPlayerScripts).
-- Carga todos los ModuleScripts de la carpeta Controllers y los arranca (Init y luego Start),
-- igual que hace el servidor con sus Services.

local controllersFolder = script.Parent:WaitForChild("Controllers")

local controllers: { [string]: any } = {}

for _, module in controllersFolder:GetChildren() do
	if module:IsA("ModuleScript") then
		local ok, result = pcall(require, module)
		if ok then
			controllers[module.Name] = result
		else
			warn(`[Cliente] ❌ No se pudo cargar {module.Name}: {result}`)
		end
	end
end

for name, controller in controllers do
	if typeof(controller) == "table" and typeof(controller.Init) == "function" then
		local ok, err = pcall(controller.Init, controller)
		if not ok then
			warn(`[Cliente] ❌ Error en {name}.Init: {err}`)
		end
	end
end

for name, controller in controllers do
	if typeof(controller) == "table" and typeof(controller.Start) == "function" then
		task.spawn(function()
			local ok, err = pcall(controller.Start, controller)
			if not ok then
				warn(`[Cliente] ❌ Error en {name}.Start: {err}`)
			end
		end)
	end
end
