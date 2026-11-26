# 🌊 Isla Menguante — guía del proyecto

El diseño completo está en [`DISENO.md`](DISENO.md). Esta guía explica cómo instalar todo y cómo probar cada fase.

**Fase actual: 1. Configuración** (Rojo, carpetas, Config, Remotes y guardado de Perlas).

---

## 1. Qué hay en cada carpeta

Rojo copia estos archivos dentro de Roblox Studio. El nombre del archivo dice qué tipo de script es:

| Terminación | Tipo en Studio | Dónde corre |
|---|---|---|
| `.server.luau` | **Script** | Servidor |
| `.client.luau` | **LocalScript** | Cliente (el jugador) |
| `.luau` (sin nada más) | **ModuleScript** | Lo usa quien lo pida con `require` |

| En tu computadora | En Roblox Studio | Qué es |
|---|---|---|
| `src/shared/Config/` | `ReplicatedStorage/Config` | ModuleScripts con TODOS los números del juego (precios, tiempos, vida…). Aquí se balancea. |
| `src/shared/Shared/` | `ReplicatedStorage/Shared` | Utilidades que usan servidor y cliente. |
| *(lo crea el servidor al arrancar)* | `ReplicatedStorage/Remotes` | Las RemoteEvents. La lista está en `Shared/RemoteDefinitions.luau`. |
| `src/places/lobby/PlaceInfo.luau` o `src/places/expedition/PlaceInfo.luau` | `ReplicatedStorage/PlaceInfo` | Dice si estamos en el Lobby o en la Expedición. |
| `src/server/Main.server.luau` | `ServerScriptService/Main` (Script) | Arranca todos los servicios. |
| `src/server/Services/` | `ServerScriptService/Services` | Lógica del servidor (datos, remotas…). |
| `src/server/Packages/` | `ServerScriptService/Packages` | Librerías externas (ProfileStore). |
| `src/client/Main.client.luau` | `StarterPlayer/StarterPlayerScripts/Main` (LocalScript) | Arranca todos los controllers. |
| `src/client/Controllers/` | `StarterPlayer/StarterPlayerScripts/Controllers` | Lógica del cliente (UI, cámara…). |

Hay **dos archivos de proyecto**, uno por place:
- `lobby.project.json` → el place del **Lobby**.
- `expedition.project.json` → el place de la **Expedición** (con `StreamingEnabled` activado).

> ⚠️ Rojo solo toca lo que está en esta carpeta. Lo que construyas a mano en Studio (el mapa en Workspace, los modelos en ServerStorage) **no se borra** y se guarda con el place, como siempre.
>
> ⚠️ Nunca edites en Studio los scripts que vienen de Rojo: los cambios se pierden en la siguiente sincronización. Los scripts se editan aquí, en los archivos.

---

## 2. Instalación (una sola vez)

### 2.1 Bajar el proyecto a tu computadora
1. Instala **GitHub Desktop** (desktop.github.com) e inicia sesión con tu cuenta de GitHub.
2. *File → Clone repository* → elige `gmpol/youtube-agent-skill` → *Clone*.
3. Arriba, en *Current branch*, elige la rama **`claude/exciting-brahmagupta-8qgp7x`**.
4. Cada vez que yo suba cambios, pulsa **Fetch origin** y luego **Pull origin** para bajarlos.

El juego está en la subcarpeta `isla-menguante` del repositorio.

### 2.2 Instalar VS Code y Rokit (que instala Rojo)
1. Instala **Visual Studio Code** (code.visualstudio.com).
2. En VS Code: *File → Open Folder…* → abre la carpeta `isla-menguante`.
3. Abre la terminal de VS Code: menú *Terminal → New Terminal*.
4. Instala **Rokit** (el instalador de herramientas):
   - **Windows:** entra a github.com/rojo-rbx/rokit/releases, descarga el `.zip` que dice `windows-x86_64`, descomprímelo, y en la terminal ve a esa carpeta y ejecuta `./rokit.exe self-install`. **Cierra y vuelve a abrir VS Code.**
   - **Mac:** en la terminal ejecuta
     `curl -sSf https://raw.githubusercontent.com/rojo-rbx/rokit/main/scripts/install.sh | bash`
     y luego cierra y vuelve a abrir VS Code.
5. En la terminal, dentro de `isla-menguante`, ejecuta:
   ```
   rokit install
   ```
   Si pregunta si confías en `rojo-rbx/rojo`, responde que sí. Comprueba que funcionó con `rojo --version`.
6. Instala el plugin de Rojo en Studio (con Studio cerrado):
   ```
   rojo plugin install
   ```
7. *(Recomendado)* En VS Code, pestaña de Extensiones, instala **Luau Language Server** (de JohnnyMorganz). Te marca errores en rojo mientras editas.

### 2.3 Descargar ProfileStore (la librería que guarda los datos)
1. Entra a **github.com/MadStudioRoblox/ProfileStore**.
2. Abre el archivo **`ProfileStore.luau`** y pulsa el botón **Download raw file** (icono de flecha hacia abajo).
3. Guárdalo exactamente aquí: `isla-menguante/src/server/Packages/ProfileStore.luau`.

Sin este archivo el servidor muestra el error: *"No encuentro ProfileStore"*.

---

## 3. Preparar el juego en Roblox Studio

1. Abre Studio → **New → Baseplate**.
2. *File → Publish to Roblox* → crea una experiencia nueva llamada **Isla Menguante**. Este place será el **Lobby**.
3. *Home → Game Settings → Security* → activa **Enable Studio Access to API Services** → *Save*.
   (Sin esto, ProfileStore no puede guardar en Studio y usa datos de prueba que se borran al parar.)
4. *(El place de la Expedición lo creamos en la fase 2.)*

---

## 4. Conectar Rojo (cada vez que vayas a trabajar)

1. En la terminal de VS Code, dentro de `isla-menguante`:
   ```
   rojo serve lobby.project.json
   ```
   Deja esa terminal abierta. Debe decir algo como `Rojo server listening on port 34872`.
2. En Studio, con el place del Lobby abierto: pestaña **Plugins → Rojo → Connect**.
3. Verás aparecer en el Explorer: `ReplicatedStorage/Config`, `ReplicatedStorage/Shared`, `ServerScriptService/Main`, `ServerScriptService/Services`, etc.
4. Guarda el place (*Ctrl+S* / *File → Publish to Roblox*) para que los scripts queden guardados en él.

Para detener Rojo: en la terminal pulsa `Ctrl+C`.

---

## 5. ✅ Cómo probar la Fase 1

### Prueba A — arranca sin errores
1. Pulsa **Play**.
2. Abre la ventana **Output** (*View → Output*). Debe salir:
   - `[Main] ✅ Servidor listo (Lobby)…`
   - `[DataService] Datos cargados de TuNombre: 0 Perlas`
3. Arriba a la izquierda aparece el **contador de Perlas** (círculo de perla + número).
4. Abajo a la derecha aparece el botón amarillo **"+10 Perlas (prueba)"** (solo existe en Studio).

### Prueba B — las Perlas se guardan
1. Pulsa el botón varias veces (por ejemplo, 5 veces → 50 Perlas). El número sube con un saltito y arriba aparece el aviso *"+10 Perlas (prueba)"*.
2. Pulsa **Stop**.
3. Pulsa **Play** otra vez. El contador debe mostrar las **mismas Perlas** que tenías.

### Prueba C — protección contra spam (rate limit)
1. Pulsa el botón muy rápido, como loco.
2. Solo debe aceptar unas 3 pulsaciones por segundo. En Output verás:
   `[NetService] ⚠️ TuNombre → DebugAddPearls: superó el límite de uso (rate limit)`.
   Eso es correcto: así frenamos a los tramposos.

### Prueba D — varios jugadores
1. Pestaña **Test → Clients and Servers → 2 Players → Start**.
2. Cada ventana tiene su propio contador. Las Perlas de un jugador no cambian las del otro.
3. Pulsa **Cleanup** para cerrar.

> ⚠️ **Si sale "Usando datos de prueba (Mock)" o un aviso de que no hay acceso a la API**, revisa el paso 3.3 (Enable Studio Access to API Services) y que el juego esté publicado.

**Cuando las 4 pruebas funcionen, avísame y pasamos a la Fase 2 (Lobby básico).**
