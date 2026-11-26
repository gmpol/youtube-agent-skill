--!strict
-- Config de las ISLAS (en orden). ModelName es el nombre del modelo que tendrás que
-- construir en ServerStorage/Islands (lo veremos en la fase 3).

export type IslandConfig = {
	Id: string,
	Order: number,
	DisplayName: string,
	ModelName: string,
	Resources: { string }, -- Ids de Config/Resources
	Creatures: { string }, -- Ids de Config/Enemies
	MiniBoss: string?, -- Id de Config/Enemies
	FinalBoss: string?,
	Palette: { Primary: Color3, Secondary: Color3, Accent: Color3 },
}

local islands: { IslandConfig } = {
	{
		Id = "TropicalReef",
		Order = 1,
		DisplayName = "Arrecife Tropical",
		ModelName = "TropicalReef",
		Resources = { "Wood", "Coconut", "Fish", "Fiber" },
		Creatures = { "Crab", "ThiefGull" },
		MiniBoss = "GiantHermitCrab",
		Palette = {
			Primary = Color3.fromRGB(42, 200, 205), -- turquesa
			Secondary = Color3.fromRGB(240, 210, 150), -- arena cálida
			Accent = Color3.fromRGB(150, 220, 60), -- verde lima
		},
	},
	{
		Id = "SunkenJungle",
		Order = 2,
		DisplayName = "Selva Hundida",
		ModelName = "SunkenJungle",
		Resources = { "Hardwood", "Vine", "Frog", "Fish" },
		Creatures = { "PoisonFrog", "LivingVine" },
		MiniBoss = "FrogQueen",
		Palette = {
			Primary = Color3.fromRGB(30, 110, 60), -- verde profundo
			Secondary = Color3.fromRGB(20, 70, 40),
			Accent = Color3.fromRGB(230, 40, 160), -- flores magenta
		},
	},
	{
		Id = "SmokingVolcano",
		Order = 3,
		DisplayName = "Volcán Humeante",
		ModelName = "SmokingVolcano",
		Resources = { "Stone", "Iron", "Obsidian" },
		Creatures = { "LavaLizard", "AshBat" },
		MiniBoss = "MagmaGolem",
		Palette = {
			Primary = Color3.fromRGB(35, 30, 30), -- negro carbón
			Secondary = Color3.fromRGB(255, 120, 20), -- naranja lava
			Accent = Color3.fromRGB(220, 30, 30), -- rojo
		},
	},
	{
		Id = "BrokenGlacier",
		Order = 4,
		DisplayName = "Glaciar Partido",
		ModelName = "BrokenGlacier",
		Resources = { "Ice", "Hide", "Crystal", "Stone" },
		Creatures = { "AngryWalrus", "SnowSpirit" },
		MiniBoss = "IceTuskWalrus",
		Palette = {
			Primary = Color3.fromRGB(245, 250, 255), -- blanco
			Secondary = Color3.fromRGB(140, 200, 255), -- azul hielo
			Accent = Color3.fromRGB(190, 160, 255), -- lila
		},
	},
	{
		Id = "CursedIsle",
		Order = 5,
		DisplayName = "Isla Maldita",
		ModelName = "CursedIsle",
		Resources = { "Bone", "CursedGold", "BlackPearl" },
		Creatures = { "DrownedSailor", "WillOWisp" },
		MiniBoss = "FacelessCaptain",
		Palette = {
			Primary = Color3.fromRGB(90, 40, 130), -- morado
			Secondary = Color3.fromRGB(120, 255, 170), -- verde fantasma
			Accent = Color3.fromRGB(130, 130, 140), -- gris
		},
	},
	{
		Id = "EyeOfTheOcean",
		Order = 6,
		DisplayName = "El Ojo del Océano",
		ModelName = "EyeOfTheOcean",
		Resources = {},
		Creatures = { "Crab", "PoisonFrog", "LavaLizard", "SnowSpirit", "DrownedSailor" }, -- oleadas mixtas
		FinalBoss = "Leviathan",
		Palette = {
			Primary = Color3.fromRGB(15, 25, 60), -- azul marino oscuro
			Secondary = Color3.fromRGB(60, 80, 120),
			Accent = Color3.fromRGB(255, 255, 255), -- relámpagos
		},
	},
}

-- Eventos aleatorios: sale uno al azar en cada isla.
-- OnlyIn = lista de islas donde puede salir (nil = en cualquiera).
local randomEvents = {
	{ Id = "Shipwreck", DisplayName = "Naufragio con botín" },
	{ Id = "GoldenFishSchool", DisplayName = "Banco de peces dorados" },
	{ Id = "DenseFog", DisplayName = "Niebla densa" },
	{ Id = "MeteorShower", DisplayName = "Lluvia de meteoritos", OnlyIn = { "SmokingVolcano" } },
	{ Id = "FloatingMerchant", DisplayName = "Mercader flotante" },
}

return {
	List = islands,
	RandomEvents = randomEvents,
}
