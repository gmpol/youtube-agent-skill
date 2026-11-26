--!strict
-- Config de los RECURSOS que se recolectan en las islas.
-- Tool = herramienta necesaria ("Hand" = con la mano).
-- MinToolTier = nivel mínimo de herramienta (1 Madera, 2 Hierro, 3 Cristal, 4 Maldita).
-- CoinValue = Monedas que da cada unidad al depositarla en el barco. ⚠️ PROVISIONAL (lo ajustamos en la fase 3).

export type ResourceConfig = {
	DisplayName: string,
	Tool: "Axe" | "Pickaxe" | "FishingRod" | "Hand",
	MinToolTier: number,
	CoinValue: number,
}

local resources: { [string]: ResourceConfig } = {
	Wood = { DisplayName = "Madera", Tool = "Axe", MinToolTier = 1, CoinValue = 2 },
	Coconut = { DisplayName = "Coco", Tool = "Hand", MinToolTier = 1, CoinValue = 3 },
	Fish = { DisplayName = "Pez", Tool = "FishingRod", MinToolTier = 1, CoinValue = 4 },
	Fiber = { DisplayName = "Fibra", Tool = "Hand", MinToolTier = 1, CoinValue = 1 },
	Hardwood = { DisplayName = "Madera dura", Tool = "Axe", MinToolTier = 1, CoinValue = 5 },
	Vine = { DisplayName = "Liana", Tool = "Hand", MinToolTier = 1, CoinValue = 3 },
	Frog = { DisplayName = "Rana", Tool = "Hand", MinToolTier = 1, CoinValue = 6 },
	Stone = { DisplayName = "Piedra", Tool = "Pickaxe", MinToolTier = 1, CoinValue = 4 },
	Iron = { DisplayName = "Hierro", Tool = "Pickaxe", MinToolTier = 1, CoinValue = 10 },
	Obsidian = { DisplayName = "Obsidiana", Tool = "Pickaxe", MinToolTier = 2, CoinValue = 18 },
	Ice = { DisplayName = "Hielo", Tool = "Pickaxe", MinToolTier = 1, CoinValue = 8 },
	Hide = { DisplayName = "Piel", Tool = "Hand", MinToolTier = 1, CoinValue = 12 },
	Crystal = { DisplayName = "Cristal", Tool = "Pickaxe", MinToolTier = 2, CoinValue = 25 },
	Bone = { DisplayName = "Hueso", Tool = "Hand", MinToolTier = 1, CoinValue = 15 },
	CursedGold = { DisplayName = "Oro maldito", Tool = "Pickaxe", MinToolTier = 3, CoinValue = 40 },
	BlackPearl = { DisplayName = "Perla negra", Tool = "Hand", MinToolTier = 1, CoinValue = 60 },
}

return {
	Resources = resources,
	BackpackSlots = 20, -- espacios de la mochila
	BackpackSlotsGamepass = 40, -- con el gamepass Mochila Grande
	RespawnTime = 60, -- PROVISIONAL: segundos para que reaparezca un recurso
}
