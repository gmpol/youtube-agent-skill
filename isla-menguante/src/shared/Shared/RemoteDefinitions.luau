--!strict
-- Lista de TODAS las RemoteEvents/RemoteFunctions del juego.
-- El servidor (NetService) las crea al arrancar dentro de ReplicatedStorage/Remotes.
-- Para añadir una nueva: agrégala aquí y luego conéctala en el servicio que la use.
--
-- Kind:
--   "Event"    → RemoteEvent (mensaje de ida, sin respuesta)
--   "Function" → RemoteFunction (el cliente pregunta y el servidor responde)
-- Direction:
--   "ToClient" → solo el servidor la dispara (el servidor ignora lo que mande el cliente)
--   "ToServer" → el cliente la dispara; el servidor la valida y aplica el RateLimit
-- RateLimit: cuántas veces (MaxCalls) por cada PerSeconds segundos puede usarla cada jugador.

export type RemoteDefinition = {
	Kind: "Event" | "Function",
	Direction: "ToClient" | "ToServer",
	RateLimit: { MaxCalls: number, PerSeconds: number }?,
}

-- Límite por defecto si una remota "ToServer" no define el suyo.
local DEFAULT_RATE_LIMIT = { MaxCalls = 10, PerSeconds = 1 }

local definitions: { [string]: RemoteDefinition } = {
	-- Servidor → Cliente: muestra un aviso en pantalla.
	Notify = { Kind = "Event", Direction = "ToClient" },

	-- Cliente → Servidor: botón de prueba para sumar Perlas. SOLO funciona dentro de Roblox Studio.
	DebugAddPearls = {
		Kind = "Event",
		Direction = "ToServer",
		RateLimit = { MaxCalls = 3, PerSeconds = 1 },
	},
}

return {
	Definitions = definitions,
	DefaultRateLimit = DEFAULT_RATE_LIMIT,
}
