--!strict
-- Config de los DATOS PERMANENTES del jugador (lo que se guarda entre partidas).
-- ⚠️ Si cambias StoreName, todos los jugadores empiezan de cero. No lo cambies tras publicar.
-- Para añadir un dato nuevo: agrégalo al tipo y a Template. A los jugadores que ya existen
-- se les añade solo (ProfileStore hace "Reconcile" al cargar).

export type PlayerData = {
	DataVersion: number,
	Pearls: number, -- Perlas (moneda permanente)
	XP: number, -- experiencia de marinero
	SailorLevel: number, -- nivel de marinero
	SelectedClass: string, -- clase elegida en el lobby (Id de Config/Classes)
	OwnedClasses: { [string]: boolean },
	Blueprints: { [string]: boolean }, -- planos desbloqueados (Id de generador → true)
	Records: {
		FurthestIsland: number, -- isla más lejana alcanzada (1-6)
		FastestLeviathanSeconds: number, -- 0 = todavía no lo ha vencido
	},
	Stats: {
		ExpeditionsPlayed: number,
		ExpeditionsWon: number,
	},
}

local template: PlayerData = {
	DataVersion = 1,
	Pearls = 0,
	XP = 0,
	SailorLevel = 1,
	SelectedClass = "Grumete",
	OwnedClasses = { Grumete = true },
	Blueprints = {},
	Records = {
		FurthestIsland = 0,
		FastestLeviathanSeconds = 0,
	},
	Stats = {
		ExpeditionsPlayed = 0,
		ExpeditionsWon = 0,
	},
}

return {
	-- Nombre del DataStore. Es el mismo para el lobby y la expedición (comparten datos).
	StoreName = "PlayerData_v1",

	-- true = en Studio se usan datos de mentira que no tocan los datos reales. Útil para probar sin miedo.
	UseMockInStudio = false,

	-- Versión actual del formato de datos (para migraciones futuras).
	CurrentVersion = 1,

	-- Datos que el servidor copia como Attributes del jugador para que la UI los muestre.
	-- Solo valores simples (números o texto), no tablas.
	ReplicatedKeys = { "Pearls", "XP", "SailorLevel", "SelectedClass" },

	-- Tope de seguridad de Perlas.
	MaxPearls = 1_000_000_000,

	Template = template,
}
