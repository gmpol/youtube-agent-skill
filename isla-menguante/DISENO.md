# 🌊 ISLA MENGUANTE — Documento de diseño + instrucciones para Claude Code

> **Cómo usar este archivo:** guárdalo en la carpeta de tu proyecto con el nombre `DISENO.md` (o pégalo completo en Claude Code). Primero lee la sección 0, que va dirigida a Claude Code.

---

## 0. INSTRUCCIONES PARA CLAUDE CODE (léelas primero)

Vas a construir conmigo un juego de Roblox llamado **Isla Menguante**. Todo el diseño está en este documento. Síguelo, y si algo no está definido, propón una opción y pregúntame antes de seguir.

**Sobre mí:**
- Ya usé Roblox Studio con las herramientas de construir, pero **nunca he programado**. Explícame en español cada paso: dónde va cada script (ServerScriptService, ReplicatedStorage, StarterPlayerScripts, StarterGui, etc.), qué tipo de script es (Script, LocalScript o ModuleScript) y cómo probarlo.
- No me importa si tarda. Quiero que quede un juegazo, pulido y sin bugs.

**Cómo trabajar:**
1. **Configuración:** ayúdame a instalar y conectar **Rojo** (VS Code/terminal + plugin de Studio) para que tú edites archivos `.luau` y se sincronicen con Studio. Si no se puede, dame cada script completo para copiar y pegar, y dime exactamente dónde va.
2. **Por fases:** sigue el orden de la sección 13. No pases a la siguiente fase hasta que yo confirme que la anterior funciona.
3. **Al terminar cada fase:** dime qué probar en Studio (Play / Start Server con 2+ jugadores) y qué debería pasar.
4. **Calidad del código:**
   - Luau con `--!strict` cuando se pueda, y nombres en inglés para el código con comentarios en español.
   - **El servidor manda.** Dinero, daño, compras y recolección se validan en el servidor. Nunca confíes en el cliente.
   - Toda la configuración (precios, tiempos, vida de enemigos, etc.) va en ModuleScripts de `ReplicatedStorage/Config`, para balancear sin tocar la lógica.
   - DataStore con reintentos, guardado al salir, `BindToClose` y protección contra pérdida de datos (usa ProfileStore/ProfileService si me ayudas a instalarlo).
   - Todas las RemoteEvents con validación, límite de uso (rate limit) y verificación de distancia.
5. **Lo visual** (modelos, mapa) lo armo yo en Studio con tus indicaciones. Dime qué partes construir, cómo nombrarlas y en qué carpeta ponerlas para que los scripts las encuentren.

---

## 1. Concepto

**En una frase:** sobrevive con tus amigos en islas que se hunden por sectores. Recolecta, mejora tu **barco-base** como tycoon y zarpa a la siguiente isla antes de que el mar se lo trague todo.

**Qué lo hace diferente:**
- **El tycoon es el barco.** No hay una base fija: tu base viaja contigo y crece isla tras isla.
- **El mapa cambia.** Cada isla es un bioma nuevo, con cinemáticas de hundimiento y de navegación entre islas.
- **La presión es la marea.** No solo hay que aguantar noches: el terreno se te va acabando.

**Inspiración:** la tensión de sobrevivir en equipo de los juegos tipo "noches en el bosque", **pero sin copiar** nombres, mapas, mecánicas exactas ni modelos. Nada de fogatas centrales ni bosques; aquí todo gira alrededor del mar y el barco.

**Público:** jugadores de 10 a 16 años que juegan con amigos. Partidas de 25 a 45 minutos.

---

## 2. Ciclo de juego

```
LOBBY → crear/unirse a tripulación → ZARPAR
  ↓
ISLA (bioma N)
  Día: recolectar, abrir cofres, construir mejoras del barco
  Marea sube → un sector de la isla se hunde
  Noche de tormenta: criaturas atacan la isla y el barco
  (se repite 3 veces)
  Última marea: sirena + 60 s para subir al barco
  ↓
CINEMÁTICA: isla hundiéndose → barco navegando → llegada a la nueva isla
  ↓
ISLA N+1 (más difícil) ... → ISLA FINAL → JEFE FINAL
  ↓
FIN DE EXPEDICIÓN: recompensas permanentes (Perlas, XP) → vuelta al LOBBY
```

**Si todos mueren o el barco se hunde:** la expedición termina. Se conservan las Perlas y la XP ganadas hasta ese momento.

---

## 3. Multijugador

- **Lobby:** un place con el muelle, la tienda, el menú de clases y la personalización del barco.
- **Expedición:** un place aparte, al que se llega por `TeleportService` con **servidores reservados**. Tripulación de **1 a 6 jugadores**.
- **Formar tripulación:** el líder crea el grupo en el muelle y los demás se suben a la pasarela. Si el grupo no se llena, hay botón de "Zarpar solos".
- **El barco y las Monedas son compartidos** por toda la tripulación (el tycoon es de equipo). Cada jugador tiene su inventario.
- **Si alguien se desconecta,** sus aportes se quedan en el barco.
- **Revivir:** un compañero cercano puede levantarte manteniendo presionada la tecla E durante 5 s. Si no, reapareces en el barco al amanecer.

---

## 4. Islas y biomas

Cada isla está dividida en **sectores en anillos** (de afuera hacia adentro). Cada marea hunde un anillo. En el centro está la zona más rica, pero quedarse ahí al final es lo más peligroso.

| # | Isla | Recursos clave | Criaturas | Mini-jefe |
|---|------|----------------|-----------|-----------|
| 1 | **Arrecife Tropical** | Madera, cocos, peces | Cangrejos, gaviotas ladronas | Cangrejo Ermitaño Gigante |
| 2 | **Selva Hundida** | Madera dura, lianas, ranas | Ranas venenosas, enredaderas vivas | Rana Reina |
| 3 | **Volcán Humeante** | Piedra, hierro, obsidiana | Lagartos de lava, murciélagos de ceniza | Golem de Magma |
| 4 | **Glaciar Partido** | Hielo, pieles, cristal | Morsas furiosas, espíritus de nieve | Morsa Colmillo de Hielo |
| 5 | **Isla Maldita** | Huesos, oro maldito, perlas negras | Marineros ahogados, fuegos fatuos | Capitán Sin Rostro |
| 6 | **El Ojo del Océano** (final) | — | Oleadas mixtas | **LEVIATÁN** (jefe final) |

**Tiempos por isla (ajustables en Config):**
- Día: 180 s → Noche de tormenta: 120 s → (×3 mareas)
- Última marea: sirena + 60 s para abordar
- Total aproximado por isla: 7 a 8 minutos

**Eventos aleatorios** (uno por isla, al azar): naufragio con botín, banco de peces dorados, niebla densa, lluvia de meteoritos (en el volcán), mercader flotante.

---

## 5. Sistema de marea (lo más importante)

- `TideService` (servidor) controla el nivel del agua y qué sectores se hunden.
- **Hundimiento animado:** cada sector baja con `TweenService` durante 8 a 10 s, con temblor de cámara suave, partículas de espuma y sonido de crujido. Los objetos que había encima se caen al agua.
- **Aviso previo:** 15 s antes, el borde del sector se ilumina en rojo, suena un cuerno y aparece en pantalla "¡LA MAREA SUBE!".
- **El agua hace daño** si estás nadando más de 10 s sin estar en el barco (frío o tiburones), y se van mostrando tiburones (aletas) cerca.
- **UI de marea:** barra arriba de la pantalla con el tiempo y el número de marea (1/3, 2/3, 3/3).

---

## 6. Recursos y recolección

| Recurso | Cómo se consigue | Herramienta |
|---------|------------------|-------------|
| Madera | Talar árboles | Hacha |
| Piedra / Hierro | Minar rocas | Pico |
| Peces | Pescar en la orilla | Caña |
| Fibra / Lianas | Arbustos | Mano |
| Cristal / Obsidiana | Rocas especiales | Pico mejorado |
| Cofres | Explorar (llaves en enemigos) | — |
| **Perlas** (permanente) | Jefes, cofres raros, completar islas | — |

- La **mochila** tiene un límite (20 espacios, mejorable). Hay que depositar en el barco para convertir en **Monedas** o en materiales de construcción.
- Los recursos reaparecen poco a poco, pero los sectores hundidos se pierden. Eso da urgencia.

---

## 7. El barco-tycoon

El barco tiene **espacios de construcción** (botones/pads estilo tycoon). Al pagar, la pieza aparece con una animación: cae desde arriba con rebote y partículas de "¡construido!".

### 7.1 Niveles del barco
| Nivel | Nombre | Espacios | Vida | Costo para mejorar |
|-------|--------|----------|------|--------------------|
| 1 | Balsa | 4 | 500 | — |
| 2 | Barquito | 7 | 1 200 | 1 500 Monedas + 50 madera |
| 3 | Velero | 10 | 2 500 | 6 000 + 40 hierro |
| 4 | Galeón | 14 | 5 000 | 20 000 + 30 cristal |
| 5 | Fortaleza Flotante | 18 | 10 000 | 60 000 + 20 oro maldito |

Al subir de nivel hay una cinemática corta: el barco se transforma con un destello. Ese momento es el que la gente va a grabar.

### 7.2 Generadores (dan Monedas pasivas)
| Generador | Costo | Ingreso | Requiere |
|-----------|-------|---------|----------|
| Red de pesca | 100 | 5 /s | — |
| Aserradero | 400 | 12 /s | Nivel 2 |
| Ahumadero | 1 200 | 25 /s | Nivel 2 |
| Taller de herrero | 4 000 | 50 /s | Nivel 3 |
| Destilería de cristal | 12 000 | 100 /s | Nivel 4 |
| Cofre del tesoro maldito | 35 000 | 220 /s | Nivel 5 |

Los generadores se pueden mejorar 3 veces: cada mejora da +50% de ingreso y cuesta ×2.

### 7.3 Defensas y utilidad
- **Cañón** (800): dispara a criaturas marinas. Lo puede manejar un jugador o se pone en automático con mejora.
- **Arpón** (1 500): mucho daño a un solo objetivo, ideal contra jefes.
- **Velas reforzadas** (2 000): viajes más rápidos y el barco recibe menos daño.
- **Enfermería** (1 000): cura a los jugadores que están en el barco.
- **Banco de trabajo** (300): fabricar herramientas mejores.
- **Faro** (2 500): ilumina la noche y revela cofres.
- **Casco blindado** (5 000): +30% de vida del barco.

### 7.4 Herramientas que se fabrican
Hacha / Pico / Caña / Espada en 4 niveles: **Madera → Hierro → Cristal → Maldita**. Cada nivel recolecta ×1.5 más rápido y hace más daño.

---

## 8. Combate y criaturas

- Combate sencillo: clic para atacar, con espada o lanza. Hay arco más adelante.
- Las criaturas salen **de noche desde el agua** y atacan a los jugadores **y al barco**.
- Si la vida del barco llega a 0, se pierde la expedición. Eso obliga a tener equipo de defensa.
- **Jefes:** con barra de vida grande arriba, dos fases y ataques que se avisan con un círculo rojo en el suelo.
- **Leviatán (final):** sale del mar alrededor del barco. Fase 1: tentáculos que hay que destruir. Fase 2: ataque con la cabeza (cañones y arpones). Fase 3: tormenta, con el barco moviéndose y esquivando olas.

**Escalado:** la vida y el daño de las criaturas aumentan +35% por isla y +15% por cada jugador extra.

---

## 9. Progresión permanente (se guarda en DataStore)

- **Perlas:** moneda permanente. Sirven para clases, cosméticos y planos.
- **Nivel de marinero (XP):** al subir de nivel se desbloquean títulos, emotes y skins.
- **Clases** (se elige una en el lobby):
  | Clase | Ventaja | Costo |
  |-------|---------|-------|
  | Grumete | Equilibrado | Gratis |
  | Leñador | +40% madera | 150 Perlas |
  | Pescador | +40% peces y pesca rara | 150 Perlas |
  | Carpintero | Construcciones −20% de costo | 300 Perlas |
  | Cañonero | +50% daño de cañones | 300 Perlas |
  | Médico | Revive el doble de rápido y cura en área | 500 Perlas |
  | Explorador | Ve cofres en el mapa | 500 Perlas |
- **Planos:** desbloqueos permanentes que te dejan empezar la expedición con un generador ya construido.
- **Récords:** isla más lejana alcanzada y tiempo más rápido contra el Leviatán. Se muestran en tablas de líderes globales en el lobby.

---

## 10. Monetización (justa, sin pagar para ganar)

### 10.1 Gamepasses (se compran una vez)
| Gamepass | Qué da | Precio |
|----------|--------|--------|
| **x2 Monedas** | Duplica las Monedas que ganas (en grupo, solo tu parte) | **249 R$** |
| **Mochila Grande** | 20 → 40 espacios | **99 R$** |
| **VIP Capitán** | Etiqueta en el chat, +10% Perlas, timón dorado, sala VIP en el lobby | **299 R$** |
| **Loro Recolector** | Mascota que junta recursos cercanos | **199 R$** |
| **Pack de Barcos Legendarios** | 3 skins de barco (Fantasma, Dragón, Dorado), solo visuales | **149 R$** |
| **Emotes de Pirata** | 6 bailes/emotes | **79 R$** |
| **x2 Perlas** | Duplica las Perlas | **399 R$** |

### 10.2 Productos que se compran varias veces (Developer Products)
| Producto | Qué da | Precio |
|----------|--------|--------|
| Revivir al instante | Revives en el momento | **25 R$** |
| Cofre de suministros | Recursos para el equipo | **49 R$** |
| Pack de Perlas S / M / L | 100 / 300 / 1 000 Perlas | **49 / 129 / 349 R$** |
| **Pack de Inicio** (una sola vez) | 500 Perlas + clase Leñador + skin | **99 R$** |

**Reglas:** nada que se compre con Robux debe ser imposible de conseguir jugando, salvo cosméticos. La tienda solo se abre en el lobby o con un botón; nunca aparecen pop-ups a la mitad del combate. Las compras se procesan con `MarketplaceService.ProcessReceipt`, de forma segura y sin duplicados.

---

## 11. Estilo visual, animaciones y sonido

**Estilo:** caricatura low-poly. Formas simples y gorditas, sin texturas realistas, con colores planos y vivos.

**Paleta por bioma:**
- Tropical: turquesa, arena cálida y verde lima
- Selva: verdes profundos con flores magenta
- Volcán: negro carbón, naranja lava y rojo
- Glaciar: blanco, azul hielo y lila
- Maldita: morado, verde fantasma y gris
- Noche/tormenta: azul marino oscuro, niebla, relámpagos blancos

**Iluminación:** `Lighting` con `Future`, `Atmosphere` y `ColorCorrection` diferentes por bioma, y transición suave entre día y noche.

**Animaciones y cinemáticas (clave para que se sienta "juegazo"):**
1. **Intro de la expedición:** la cámara vuela sobre el barco saliendo del muelle y aparece el título.
2. **Llegada a una isla:** la cámara hace un paneo de la isla y se muestra su nombre con efecto de letra grande.
3. **Hundimiento de sector:** temblor, espuma, crujidos y los árboles que se inclinan.
4. **Zarpar:** la isla se hunde por completo detrás del barco y entra una transición de olas.
5. **Navegación:** 10 a 15 s con cámara cinemática, delfines o criaturas al fondo, y mientras tanto se carga la siguiente isla.
6. **Construcción tycoon:** la pieza cae con rebote, chispas y un sonido satisfactorio.
7. **Mejora del barco:** destello y transformación.
8. **Entrada de jefe:** se oscurece la pantalla, aparece el nombre del jefe y entra la música épica.
9. **Victoria final:** fuegos artificiales en el barco y pantalla de estadísticas.

Las cinemáticas se pueden saltar después de la primera vez (votación en grupo).

**UI:** botones grandes y redondeados con borde grueso estilo caricatura, que funcionen bien en celular (la mitad de los jugadores de Roblox juegan en celular). Iconos para las Monedas, las Perlas y la mochila.

**Sonido:** música relajada de día, tensa de noche y épica con los jefes. Efectos de olas, gaviotas, crujido de madera y "cha-ching" al cobrar. Usa solo audio libre de la biblioteca de Roblox.

---

## 12. Arquitectura técnica

```
ReplicatedStorage/
  Config/            (ModuleScripts: Islands, Tides, Boat, Generators, Enemies, Classes, Monetization)
  Shared/            (utilidades, tipos)
  Remotes/           (RemoteEvents / RemoteFunctions)
  Assets/            (efectos, UI templates)
ServerScriptService/
  Services/
    DataService        (ProfileStore, guardado)
    ExpeditionService  (flujo de islas, estados de la partida)
    TideService        (marea y hundimiento de sectores)
    IslandService      (cargar/descargar islas desde ServerStorage)
    ResourceService    (recolección validada)
    BoatService        (tycoon del barco, construcción, vida)
    EnemyService       (spawns, IA simple, jefes)
    CombatService      (daño validado)
    MonetizationService(gamepasses, ProcessReceipt)
    TeleportService    (lobby ↔ expedición)
ServerStorage/
  Islands/           (modelos de cada isla, con sectores nombrados Sector1..SectorN)
  Enemies/
  BoatParts/
StarterPlayer/StarterPlayerScripts/
  Controllers/       (CameraController, CinematicController, UIController, ToolController, SoundController)
StarterGui/
  (HUD, Tienda, Mochila, Marea, Jefe, Fin de partida)
```

**Estados de la expedición:** `Intro → IslandDay → TideWarning → TideSink → StormNight → ... → Boarding → Sailing → (siguiente isla) → BossFight → Victory/Defeat`.

**Cambio de mapa:** todo pasa dentro del mismo servidor. Mientras el barco navega, la isla vieja se destruye y la nueva se clona desde `ServerStorage` delante del barco. Usar `StreamingEnabled` para que no haya lag.

**Rendimiento:** pocos enemigos activos a la vez (máximo 25), pooling de objetos y nada de bucles pesados en el cliente.

---

## 13. Orden de construcción (fases)

1. **Configuración:** Rojo, estructura de carpetas, Config, Remotes y DataService con guardado de Perlas.
2. **Lobby básico:** muelle, crear tripulación y teletransporte a la expedición.
3. **Isla 1 jugable:** recolección con herramientas, mochila y depósito en el barco.
4. **Barco-tycoon:** espacios de construcción, Monedas, generadores y animación de construir.
5. **Marea:** sectores que se hunden, avisos, UI de marea y daño en el agua.
6. **Noche y criaturas:** spawns, combate básico, vida del barco, revivir.
7. **Viaje entre islas:** abordaje, cinemática de navegación y carga de la isla 2. → **Primera prueba completa con amigos.**
8. **Las 6 islas** con sus biomas, criaturas y mini-jefes.
9. **Leviatán** y pantalla de victoria.
10. **Progresión:** clases, XP, planos y tablas de líderes.
11. **Monetización:** gamepasses, productos y tienda.
12. **Pulido:** todas las cinemáticas, sonido, iluminación por bioma y UI para celular.
13. **Lanzamiento:** ícono, miniaturas, descripción, pruebas con 6 jugadores, arreglo de bugs y publicación.

**Después del lanzamiento:** eventos semanales (por ejemplo, Marea Roja con doble Perlas), islas nuevas cada mes y skins de temporada.

---

## 14. Checklist de "juegazo" antes de lanzar

- [ ] En los primeros 30 s el jugador ya está haciendo algo divertido.
- [ ] Siempre hay algo que comprar o mejorar "nomás uno más".
- [ ] Jugar con amigos es claramente mejor que jugar solo.
- [ ] Hay momentos para grabar: hundimiento, jefes, transformación del barco.
- [ ] Funciona bien en celular.
- [ ] No hay forma de hacer trampa con el dinero (todo se valida en el servidor).
- [ ] Los datos nunca se pierden.
- [ ] El ícono y la miniatura llaman la atención (barco + isla hundiéndose + criatura gigante).
