--!strict
-- Config de las CRIATURAS y JEFES.
-- ⚠️ Health, Damage y Speed son PROVISIONALES: el diseño no los define. Los ajustamos en la fase 6.
-- Escalado: +35% vida y daño por isla, y +15% por cada jugador extra en la tripulación.

export type EnemyConfig = {
	DisplayName: string,
	Kind: "Creature" | "MiniBoss" | "FinalBoss",
	Health: number,
	Damage: number,
	Speed: number,
	Phases: number?,
	AttacksBoat: boolean, -- si también ataca al barco
}

local enemies: { [string]: EnemyConfig } = {
	-- Isla 1: Arrecife Tropical
	Crab = { DisplayName = "Cangrejo", Kind = "Creature", Health = 40, Damage = 6, Speed = 12, AttacksBoat = true },
	ThiefGull = { DisplayName = "Gaviota ladrona", Kind = "Creature", Health = 25, Damage = 4, Speed = 20, AttacksBoat = false },
	GiantHermitCrab = { DisplayName = "Cangrejo Ermitaño Gigante", Kind = "MiniBoss", Health = 1500, Damage = 20, Speed = 10, Phases = 2, AttacksBoat = true },

	-- Isla 2: Selva Hundida
	PoisonFrog = { DisplayName = "Rana venenosa", Kind = "Creature", Health = 35, Damage = 8, Speed = 16, AttacksBoat = false },
	LivingVine = { DisplayName = "Enredadera viva", Kind = "Creature", Health = 60, Damage = 7, Speed = 6, AttacksBoat = true },
	FrogQueen = { DisplayName = "Rana Reina", Kind = "MiniBoss", Health = 2000, Damage = 24, Speed = 14, Phases = 2, AttacksBoat = true },

	-- Isla 3: Volcán Humeante
	LavaLizard = { DisplayName = "Lagarto de lava", Kind = "Creature", Health = 55, Damage = 10, Speed = 15, AttacksBoat = true },
	AshBat = { DisplayName = "Murciélago de ceniza", Kind = "Creature", Health = 30, Damage = 7, Speed = 22, AttacksBoat = false },
	MagmaGolem = { DisplayName = "Golem de Magma", Kind = "MiniBoss", Health = 2600, Damage = 30, Speed = 8, Phases = 2, AttacksBoat = true },

	-- Isla 4: Glaciar Partido
	AngryWalrus = { DisplayName = "Morsa furiosa", Kind = "Creature", Health = 80, Damage = 12, Speed = 11, AttacksBoat = true },
	SnowSpirit = { DisplayName = "Espíritu de nieve", Kind = "Creature", Health = 40, Damage = 9, Speed = 18, AttacksBoat = false },
	IceTuskWalrus = { DisplayName = "Morsa Colmillo de Hielo", Kind = "MiniBoss", Health = 3200, Damage = 34, Speed = 10, Phases = 2, AttacksBoat = true },

	-- Isla 5: Isla Maldita
	DrownedSailor = { DisplayName = "Marinero ahogado", Kind = "Creature", Health = 70, Damage = 12, Speed = 13, AttacksBoat = true },
	WillOWisp = { DisplayName = "Fuego fatuo", Kind = "Creature", Health = 30, Damage = 10, Speed = 20, AttacksBoat = false },
	FacelessCaptain = { DisplayName = "Capitán Sin Rostro", Kind = "MiniBoss", Health = 4000, Damage = 38, Speed = 14, Phases = 2, AttacksBoat = true },

	-- Isla 6: El Ojo del Océano
	Leviathan = { DisplayName = "LEVIATÁN", Kind = "FinalBoss", Health = 25000, Damage = 50, Speed = 0, Phases = 3, AttacksBoat = true },
}

local SCALE_PER_ISLAND = 0.35
local SCALE_PER_EXTRA_PLAYER = 0.15

return {
	Enemies = enemies,
	ScalePerIsland = SCALE_PER_ISLAND,
	ScalePerExtraPlayer = SCALE_PER_EXTRA_PLAYER,
	MaxActiveEnemies = 25, -- máximo de criaturas vivas a la vez (rendimiento)

	-- Multiplicador de vida/daño. islandOrder empieza en 1; crewSize de 1 a 6.
	GetScale = function(islandOrder: number, crewSize: number): number
		local islandScale = 1 + SCALE_PER_ISLAND * (islandOrder - 1)
		local crewScale = 1 + SCALE_PER_EXTRA_PLAYER * math.max(crewSize - 1, 0)
		return islandScale * crewScale
	end,
}
