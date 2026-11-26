--!strict
-- Config de MONETIZACIÓN. ⚠️ Los Id están en 0: cuando crees cada gamepass/producto en el
-- Creator Hub (fase 11), copia aquí su número de Id. El precio real se pone en el Creator Hub;
-- PriceRobux aquí es solo de referencia para mostrarlo en la tienda.
-- Regla: nada que se compre con Robux es imposible de conseguir jugando (salvo cosméticos).

local gamepasses = {
	DoubleCoins = { Id = 0, DisplayName = "x2 Monedas", PriceRobux = 249, Description = "Duplica las Monedas que ganas (en grupo, solo tu parte)" },
	BigBackpack = { Id = 0, DisplayName = "Mochila Grande", PriceRobux = 99, Description = "Mochila de 20 a 40 espacios" },
	VIPCaptain = { Id = 0, DisplayName = "VIP Capitán", PriceRobux = 299, Description = "Etiqueta en el chat, +10% Perlas, timón dorado y sala VIP" },
	CollectorParrot = { Id = 0, DisplayName = "Loro Recolector", PriceRobux = 199, Description = "Mascota que junta recursos cercanos" },
	LegendaryBoats = { Id = 0, DisplayName = "Pack de Barcos Legendarios", PriceRobux = 149, Description = "Skins Fantasma, Dragón y Dorado (solo visuales)" },
	PirateEmotes = { Id = 0, DisplayName = "Emotes de Pirata", PriceRobux = 79, Description = "6 bailes/emotes" },
	DoublePearls = { Id = 0, DisplayName = "x2 Perlas", PriceRobux = 399, Description = "Duplica las Perlas" },
}

local products = {
	InstantRevive = { Id = 0, DisplayName = "Revivir al instante", PriceRobux = 25 },
	SupplyChest = { Id = 0, DisplayName = "Cofre de suministros", PriceRobux = 49 },
	PearlsSmall = { Id = 0, DisplayName = "Pack de Perlas S", PriceRobux = 49, Pearls = 100 },
	PearlsMedium = { Id = 0, DisplayName = "Pack de Perlas M", PriceRobux = 129, Pearls = 300 },
	PearlsLarge = { Id = 0, DisplayName = "Pack de Perlas L", PriceRobux = 349, Pearls = 1000 },
	StarterPack = { Id = 0, DisplayName = "Pack de Inicio", PriceRobux = 99, Pearls = 500, OneTimeOnly = true, GrantsClass = "Lumberjack" },
}

return {
	Gamepasses = gamepasses,
	Products = products,
	VIPPearlBonus = 0.10, -- +10% Perlas
	ShopOnlyInLobby = true, -- la tienda solo se abre en el lobby o con un botón, nunca en combate
}
