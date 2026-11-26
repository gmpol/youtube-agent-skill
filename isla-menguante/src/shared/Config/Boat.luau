--!strict
-- Config del BARCO-TYCOON: niveles, defensas y animación de construir.

export type BoatLevel = {
	Level: number,
	Name: string,
	Slots: number, -- espacios de construcción
	MaxHealth: number,
	UpgradeCost: { Coins: number, Materials: { [string]: number } }?, -- costo para LLEGAR a este nivel
}

local levels: { BoatLevel } = {
	{ Level = 1, Name = "Balsa", Slots = 4, MaxHealth = 500 },
	{ Level = 2, Name = "Barquito", Slots = 7, MaxHealth = 1200, UpgradeCost = { Coins = 1500, Materials = { Wood = 50 } } },
	{ Level = 3, Name = "Velero", Slots = 10, MaxHealth = 2500, UpgradeCost = { Coins = 6000, Materials = { Iron = 40 } } },
	{ Level = 4, Name = "Galeón", Slots = 14, MaxHealth = 5000, UpgradeCost = { Coins = 20000, Materials = { Crystal = 30 } } },
	{
		Level = 5,
		Name = "Fortaleza Flotante",
		Slots = 18,
		MaxHealth = 10000,
		UpgradeCost = { Coins = 60000, Materials = { CursedGold = 20 } },
	},
}

-- Defensas y utilidad (se construyen en los espacios del barco).
local utilities = {
	Cannon = { DisplayName = "Cañón", Cost = 800 },
	Harpoon = { DisplayName = "Arpón", Cost = 1500 },
	ReinforcedSails = { DisplayName = "Velas reforzadas", Cost = 2000 },
	Infirmary = { DisplayName = "Enfermería", Cost = 1000 },
	Workbench = { DisplayName = "Banco de trabajo", Cost = 300 },
	Lighthouse = { DisplayName = "Faro", Cost = 2500 },
	ArmoredHull = { DisplayName = "Casco blindado", Cost = 5000, HealthBonus = 0.30 }, -- +30% de vida
}

return {
	Levels = levels,
	Utilities = utilities,

	-- Animación al construir: la pieza cae desde arriba con rebote.
	BuildDropHeight = 15, -- studs
	BuildDropTime = 0.7, -- segundos

	MaxBuildDistance = 15, -- distancia máxima al pad para comprar (validada en el servidor)
}
