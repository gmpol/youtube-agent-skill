--!strict
-- RateLimiter: limita cuántas veces por segundo un jugador puede usar algo
-- (por ejemplo, disparar una RemoteEvent). Evita spam y exploits.
-- Funciona como un "cubo de fichas": cada uso gasta una ficha y las fichas se recargan con el tiempo.

type Bucket = {
	tokens: number,
	lastRefill: number,
}

type RateLimiterData = {
	_maxCalls: number,
	_refillPerSecond: number,
	_buckets: { [Player]: Bucket },
}

local RateLimiter = {}
RateLimiter.__index = RateLimiter

export type RateLimiter = typeof(setmetatable({} :: RateLimiterData, RateLimiter))

-- maxCalls: cuántos usos seguidos se permiten. perSeconds: en cuántos segundos se recargan todos.
function RateLimiter.new(maxCalls: number, perSeconds: number): RateLimiter
	assert(maxCalls > 0 and perSeconds > 0, "RateLimiter: los valores deben ser mayores que 0")
	return setmetatable({
		_maxCalls = maxCalls,
		_refillPerSecond = maxCalls / perSeconds,
		-- Tabla "débil": si el jugador se va, no se queda guardado en memoria.
		_buckets = setmetatable({}, { __mode = "k" }) :: any,
	}, RateLimiter)
end

-- Devuelve true si el jugador puede usarlo ahora (y gasta una ficha).
function RateLimiter.Check(self: RateLimiter, player: Player): boolean
	local now = os.clock()
	local bucket = self._buckets[player]
	if not bucket then
		bucket = { tokens = self._maxCalls, lastRefill = now }
		self._buckets[player] = bucket
	end

	local elapsed = now - bucket.lastRefill
	bucket.tokens = math.min(self._maxCalls, bucket.tokens + elapsed * self._refillPerSecond)
	bucket.lastRefill = now

	if bucket.tokens < 1 then
		return false
	end
	bucket.tokens -= 1
	return true
end

function RateLimiter.Remove(self: RateLimiter, player: Player)
	self._buckets[player] = nil
end

return RateLimiter
