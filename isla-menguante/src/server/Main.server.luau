--!strict
-- Script principal del SERVIDOR (tipo: Script, en ServerScriptService).
-- Carga todos los ModuleScripts de la carpeta Services y los arranca en dos pasos:
--   1) Init(): preparar cosas (conectar eventos, crear carpetas). No debe esperar.
--   2) Start(): empezar a funcionar (bucles, lógica del juego). Corre en paralelo.

local ServerScriptService = game:GetService("ServerScriptService")

local servicesFolder = ServerScriptService:WaitForChild("Services")

local services: { [string]: any } = {}

-- 1. Cargar (require) cada servicio
for _, module in servicesFolder:GetChildren() do
	if module:IsA("ModuleScript") then
		local ok, result = pcall(require, module)
		if ok then
			services[module.Name] = result
		else
			warn(`[Main] ❌ No se pudo cargar el servicio {module.Name}: {result}`)
		end
	end
end

-- 2. Init de todos
for name, service in services do
	if typeof(service) == "table" and typeof(service.Init) == "function" then
		local ok, err = pcall(service.Init, service)
		if not ok then
			warn(`[Main] ❌ Error en {name}.Init: {err}`)
		end
	end
end

-- 3. Start de todos (cada uno en su propio hilo)
for name, service in services do
	if typeof(service) == "table" and typeof(service.Start) == "function" then
		task.spawn(function()
			local ok, err = pcall(service.Start, service)
			if not ok then
				warn(`[Main] ❌ Error en {name}.Start: {err}`)
			end
		end)
	end
end

local placeInfo = require(game:GetService("ReplicatedStorage"):WaitForChild("PlaceInfo") :: ModuleScript)
print(`[Main] ✅ Servidor listo ({placeInfo.PlaceType}). Servicios cargados: {#servicesFolder:GetChildren()}`)
