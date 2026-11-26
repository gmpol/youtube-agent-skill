--!strict
-- Signal: un "evento" propio para que los módulos se avisen cosas entre sí
-- dentro del mismo lado (servidor con servidor, o cliente con cliente).
-- Ejemplo: DataService.DataLoaded:Connect(function(player, data) ... end)

export type Connection = {
	Connected: boolean,
	Disconnect: (self: Connection) -> (),
}

type SignalData = {
	_connections: { ConnectionImpl },
}

type ConnectionImpl = Connection & {
	_callback: (...any) -> (),
}

local Signal = {}
Signal.__index = Signal

export type Signal = typeof(setmetatable({} :: SignalData, Signal))

function Signal.new(): Signal
	return setmetatable({ _connections = {} }, Signal)
end

-- Conecta una función que se llamará cada vez que se dispare la señal.
function Signal.Connect(self: Signal, callback: (...any) -> ()): Connection
	local connection: ConnectionImpl
	connection = {
		Connected = true,
		_callback = callback,
		Disconnect = function(_self: Connection)
			if not connection.Connected then
				return
			end
			connection.Connected = false
			local index = table.find(self._connections, connection)
			if index then
				table.remove(self._connections, index)
			end
		end,
	}
	table.insert(self._connections, connection)
	return connection
end

-- Igual que Connect, pero solo se ejecuta la primera vez.
function Signal.Once(self: Signal, callback: (...any) -> ()): Connection
	local connection: Connection
	connection = self:Connect(function(...)
		connection:Disconnect()
		callback(...)
	end)
	return connection
end

-- Dispara la señal. Cada función conectada corre en su propio hilo,
-- así que si una falla, las demás siguen funcionando.
function Signal.Fire(self: Signal, ...: any)
	-- Copiamos la lista por si alguien se desconecta mientras recorremos.
	for _, connection in table.clone(self._connections) do
		if connection.Connected then
			task.spawn(connection._callback, ...)
		end
	end
end

-- Pausa el código hasta que la señal se dispare y devuelve sus valores.
function Signal.Wait(self: Signal): ...any
	local thread = coroutine.running()
	self:Once(function(...)
		task.spawn(thread, ...)
	end)
	return coroutine.yield()
end

function Signal.DisconnectAll(self: Signal)
	for _, connection in table.clone(self._connections) do
		connection:Disconnect()
	end
end

return Signal
