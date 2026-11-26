--!strict
-- Config de las CLASES que se eligen en el lobby (se compran con Perlas).
-- Bonuses: los servicios leen estos valores; 0.4 = +40%, -0.2 = -20%.

export type ClassConfig = {
	Id: string,
	DisplayName: string,
	Description: string,
	PearlCost: number,
	Bonuses: { [string]: number },
}

local classes: { ClassConfig } = {
	{ Id = "Grumete", DisplayName = "Grumete", Description = "Equilibrado", PearlCost = 0, Bonuses = {} },
	{ Id = "Lumberjack", DisplayName = "Leñador", Description = "+40% madera", PearlCost = 150, Bonuses = { WoodGather = 0.4 } },
	{ Id = "Fisher", DisplayName = "Pescador", Description = "+40% peces y pesca rara", PearlCost = 150, Bonuses = { FishGather = 0.4, RareFishChance = 0.1 } },
	{ Id = "Carpenter", DisplayName = "Carpintero", Description = "Construcciones -20% de costo", PearlCost = 300, Bonuses = { BuildCost = -0.2 } },
	{ Id = "Gunner", DisplayName = "Cañonero", Description = "+50% daño de cañones", PearlCost = 300, Bonuses = { CannonDamage = 0.5 } },
	{ Id = "Medic", DisplayName = "Médico", Description = "Revive el doble de rápido y cura en área", PearlCost = 500, Bonuses = { ReviveSpeed = 1.0, AreaHeal = 1 } },
	{ Id = "Explorer", DisplayName = "Explorador", Description = "Ve cofres en el mapa", PearlCost = 500, Bonuses = { SeeChests = 1 } },
}

return {
	List = classes,
	DefaultClass = "Grumete",
}
