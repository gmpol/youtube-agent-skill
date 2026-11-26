--!strict
-- Config de los GENERADORES del barco (dan Monedas pasivas por segundo).
-- Cada generador se puede mejorar 3 veces: cada mejora da +50% de ingreso y cuesta ×2.
-- Interpretación propuesta: la mejora multiplica el ingreso actual (×1.5 cada vez) y el costo
-- de cada mejora es el doble del anterior (1ª mejora = Costo×2, 2ª = Costo×4, 3ª = Costo×8).

export type GeneratorConfig = {
	Id: string,
	DisplayName: string,
	Cost: number,
	IncomePerSecond: number,
	RequiredBoatLevel: number,
}

local generators: { GeneratorConfig } = {
	{ Id = "FishingNet", DisplayName = "Red de pesca", Cost = 100, IncomePerSecond = 5, RequiredBoatLevel = 1 },
	{ Id = "Sawmill", DisplayName = "Aserradero", Cost = 400, IncomePerSecond = 12, RequiredBoatLevel = 2 },
	{ Id = "Smokehouse", DisplayName = "Ahumadero", Cost = 1200, IncomePerSecond = 25, RequiredBoatLevel = 2 },
	{ Id = "Blacksmith", DisplayName = "Taller de herrero", Cost = 4000, IncomePerSecond = 50, RequiredBoatLevel = 3 },
	{ Id = "CrystalDistillery", DisplayName = "Destilería de cristal", Cost = 12000, IncomePerSecond = 100, RequiredBoatLevel = 4 },
	{ Id = "CursedTreasureChest", DisplayName = "Cofre del tesoro maldito", Cost = 35000, IncomePerSecond = 220, RequiredBoatLevel = 5 },
}

local MAX_UPGRADES = 3
local UPGRADE_INCOME_MULTIPLIER = 1.5
local UPGRADE_COST_MULTIPLIER = 2

return {
	List = generators,
	MaxUpgrades = MAX_UPGRADES,
	UpgradeIncomeMultiplier = UPGRADE_INCOME_MULTIPLIER,
	UpgradeCostMultiplier = UPGRADE_COST_MULTIPLIER,

	-- Ingreso por segundo con N mejoras (0 a 3).
	GetIncome = function(generator: GeneratorConfig, upgrades: number): number
		return generator.IncomePerSecond * UPGRADE_INCOME_MULTIPLIER ^ upgrades
	end,

	-- Costo de la siguiente mejora, sabiendo cuántas lleva (0 a 2).
	GetUpgradeCost = function(generator: GeneratorConfig, currentUpgrades: number): number
		return generator.Cost * UPGRADE_COST_MULTIPLIER ^ (currentUpgrades + 1)
	end,
}
