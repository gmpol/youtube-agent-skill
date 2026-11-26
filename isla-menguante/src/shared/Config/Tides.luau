--!strict
-- Config de la MAREA y del ciclo día/noche de cada isla. Todo en segundos.

return {
	DayDuration = 180, -- Día: recolectar, abrir cofres y construir
	NightDuration = 120, -- Noche de tormenta: atacan las criaturas
	TidesPerIsland = 3, -- cuántas mareas hay en cada isla (1/3, 2/3, 3/3)

	WarningTime = 15, -- aviso previo: borde rojo, cuerno y "¡LA MAREA SUBE!"
	SinkDuration = 9, -- cuánto tarda en hundirse un sector (8 a 10 s)
	SinkDepth = 40, -- cuántos studs baja un sector al hundirse
	CameraShakeIntensity = 0.4, -- temblor de cámara suave al hundirse

	FinalBoardingTime = 60, -- última marea: sirena + 60 s para subir al barco

	-- Daño en el agua (frío o tiburones)
	SwimGraceTime = 10, -- segundos nadando sin recibir daño
	SwimDamagePerSecond = 8, -- PROVISIONAL: daño por segundo después de ese tiempo
	SharkFinsAfter = 5, -- PROVISIONAL: a los cuántos segundos aparecen aletas de tiburón cerca
}
