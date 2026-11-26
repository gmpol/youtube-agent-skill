--!strict
-- Config de las HERRAMIENTAS que se fabrican en el Banco de trabajo.
-- Cada nivel recolecta ×1.5 más rápido y hace más daño que el anterior.
-- Los costos de fabricación están PENDIENTES (no los define el diseño; los vemos en la fase 4).

local tiers = {
	{ Tier = 1, Id = "Wood", DisplayName = "Madera" },
	{ Tier = 2, Id = "Iron", DisplayName = "Hierro" },
	{ Tier = 3, Id = "Crystal", DisplayName = "Cristal" },
	{ Tier = 4, Id = "Cursed", DisplayName = "Maldita" },
}

local toolTypes = {
	Axe = { DisplayName = "Hacha", BaseGatherTime = 1.0, BaseDamage = 8 },
	Pickaxe = { DisplayName = "Pico", BaseGatherTime = 1.2, BaseDamage = 8 },
	FishingRod = { DisplayName = "Caña", BaseGatherTime = 3.0, BaseDamage = 2 },
	Sword = { DisplayName = "Espada", BaseGatherTime = 0, BaseDamage = 15 },
}

local TIER_MULTIPLIER = 1.5

return {
	Tiers = tiers,
	ToolTypes = toolTypes,
	TierMultiplier = TIER_MULTIPLIER,
	-- Multiplicador de velocidad y daño para un nivel: 1 → ×1, 2 → ×1.5, 3 → ×2.25, 4 → ×3.375
	GetTierMultiplier = function(tier: number): number
		return TIER_MULTIPLIER ^ (tier - 1)
	end,
	AttackCooldown = 0.5, -- segundos entre golpes
	MaxGatherDistance = 12, -- distancia máxima (studs) para recolectar, validada en el servidor
}
