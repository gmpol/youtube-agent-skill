# Guía de estilo: explicadores animados verticales

Basada en el análisis de 3 reels (las grabaciones de pantalla que me pasaste):

| | ref1 | ref2 | ref3 |
|---|---|---|---|
| Cuenta | @engineeredwithin1 | @engineeredwithin1 | @curios0n ("AI-generated profile") |
| Tema | ¿Cómo funciona una máquina de cortar pelo? | ¿Cómo funciona un cepillo eléctrico? | ¿Por qué el gallo sabe a qué hora cantar? |
| Duración | 34,8 s | 33,1 s | 39,0 s (la grabación corta la última frase) |
| Voz | **No hay**: música + efectos | **No hay**: música + efectos | Narración masculina en español, 168 palabras/min |
| Gancho | Cartel "HOW DOES A HAIR CLIPPER WORK?" + "7,200 RPM: 240 SNIPS A SECOND" | Cartel "HOW DOES AN ELECTRIC TOOTHBRUSH WORK?" + "128 STROKES EVERY SECOND" | "¿Por qué el puto gallo sabe a qué puta hora cantar? No tiene reloj, no tiene móvil…" |
| Fórmula (`hooks.json`) | The Question | The Question | The Question + The Impossible Claim (hookscore no la detecta: sus patrones solo están en inglés) |
| hookscore | 45 (WEAK) | 41 (WEAK) | 34 (WEAK) |
| Likes | 189.703 | (sin metadatos, Instagram dio 429) | 243.281 |

Nota honesta sobre `hookscore.py`: los tres ganchos dan "WEAK" porque la herramienta puntúa *palabras* (busca "you", stakes…).
Estos reels enganchan con la *imagen* y con un número imposible. La herramienta no ve eso; el README del repo ya lo
advierte ("A low score is a reason to look again").

Las grabaciones llegaron a 384x848 (WhatsApp). Las medidas de tamaño se dan escaladas a 1080x1920, el formato original
según los metadatos de Instagram.

---

## 1. Lo que define el estilo (común a los 3)

1. **Una sola pregunta cotidiana** que todo el mundo se ha hecho y nadie sabe contestar ("¿cómo funciona…?", "¿por qué…?").
   El título del video ES la pregunta.
2. **El número imposible en los primeros 2 s.** 240 cortes por segundo, 128 pasadas por segundo, "cada 24 horas exactas".
   Siempre una cifra concreta, nunca "muy rápido".
3. **Ilustración animada, nunca video real.** Un objeto protagonista, centrado, en un mundo de fondo oscuro.
   La cámara no corta, **se mueve**: zoom in, travelling, rotación, corte transversal ("rayos X") del objeto.
   ffmpeg solo detecta 0–2 cortes duros por video. El ritmo lo marcan los **beats**, no los cortes.
4. **Explicación por capas, de fuera hacia dentro.** Primero el objeto entero, luego la pieza que se ve, luego la que no se
   ve, luego la fuente de energía, y al final "todo junto".
5. **Etiquetas técnicas con línea guía** (callouts): "MOTOR", "PIN", "SHAFT", "reloj interno". Una o dos palabras,
   mayúsculas o minúsculas, con una línea fina que apunta a la pieza.
6. **Paleta**: fondo azul marino/violeta muy oscuro, objeto en colores cálidos (rojo, naranja, amarillo, crema).
   Contraste alto: el ojo va directo a lo cálido.
7. **Final en bucle.** ref1 y ref2 terminan exactamente en el plano inicial, con el mismo cartel. ref3 termina en el
   "gallo jefe" con el mismo cielo nocturno del inicio. El espectador no nota dónde empieza la repetición, y eso suma
   reproducciones.
8. **Sin intro, sin "suscríbete", sin presentarse.** El primer fotograma ya es el gancho.

## 2. Lo propio de cada canal (variantes)

**Variante A, "engineeredwithin" (ref1, ref2): mudo, mecánico**
- Cartel de título estilo **cartel de feria/barbería**: tipografía slab serif gruesa en negro + rojo sobre crema, con
  marco dorado y "palos de barbero" a rayas en los extremos.
- Pasos **numerados** (círculo rojo con número, 1–5) y cada paso con pregunta + subtítulo: "WHAT MOVES IT? / A small motor inside".
- **Barra superior fija** con un velocímetro, "64x SLOWER → 32x → … → REAL SPEED" y un contador ("STROKES A MINUTE 7680").
  Todo el video va a cámara lenta y **acelera al final** (8 → 16 → 32 → 64 → 128 por segundo) hasta la velocidad real.
  Ese crescendo es el clímax.
- Estética **pixel-art / 3D low-poly**.
- Audio: música electrónica/chiptune constante (~114–121 BPM) + efectos ("SNIP!", whoosh) en cada cambio de cartel.

**Variante B, "curios0n" (ref3): narrado, cómico**
- Narración rápida (168 ppm), voz masculina expresiva (F0 mediana 157 Hz, rango 100–254 Hz: muy entonada), con
  **palabrotas como muletilla rítmica** ("puto" ×7, "puta" ×3 en 35 s). Probablemente voz IA (el perfil se declara
  "AI-generated").
- Estructura de 3 bloques (validada por `chapters.py`): **pregunta absurda (0:00)**, **experimento científico (0:13)**,
  **la respuesta + remate (0:24)**.
- Subtítulos palabra a palabra **arriba** (no abajo) y **sin texto en pantalla aparte**; los datos van en
  infografías (banderita "JAPÓN", etiqueta "LUZ TENUE · 24 H", gráfica de picos "día 1…día 4").
- Ilustración vectorial plana (estilo Kurzgesagt simplificado), personajes con ojos expresivos.
- **No hay música de fondo** bajo la voz: en las pausas el nivel cae a silencio (< −40 dB). Solo voz + efectos puntuales
  (aparición de iconos, "kikiriki").

## 3. Ritmo medido

| | ref1 | ref2 | ref3 |
|---|---|---|---|
| Cortes duros (ffmpeg scene > 0,3) | 2 | 2 | 0 |
| Cambios de escena (> 0,12) | 9 | 14 | 0 (todo es movimiento continuo) |
| **Beats** (cambio de cartel/escena, contados en frames) | 16 → 1 cada **2,2 s** (~27/min) | 10 → 1 cada **3,3 s** (~18/min) | 7 escenas, cada ~5,5 s, pero el subtítulo cambia cada **~1 s** y aparece un icono nuevo cada **2–3 s** |
| Pausas de voz > 0,25 s | – | – | 12 (la más larga 1,0 s, a los 12,1 s, justo antes del bloque "experimento") |
| `deadair.py` | – | – | 6 microcortes posibles, solo 1,6 s (4,6 %). Ya está casi sin aire. |

**Regla práctica**: algo nuevo en pantalla cada 2–3 s (etiqueta, icono, zoom, número). Cambio de "capítulo" cada 8–15 s.

## 4. Plantilla de guion (para 75–90 s, dentro de tu rango de 1–2 min)

Los originales duran 35 s. Para llegar a 1–2 min sin perder el ritmo, la plantilla **añade pasos**, no alarga cada uno.

| Tiempo | Bloque | Qué se dice | Qué se ve |
|---|---|---|---|
| 0–3 s | **Gancho** | La pregunta + el número imposible. Máx. 15 palabras. | El objeto entero, cartel de título, velocímetro en "REAL SPEED" |
| 3–8 s | **Imposible** | "No tiene X, no tiene Y, y aun así…". Negar las explicaciones obvias. | Iconos tachados que aparecen uno a uno |
| 8–12 s | **Freno** | "Vamos a verlo X veces más lento." | El velocímetro baja a "1000x MÁS LENTO", zoom in |
| 12–60 s | **Pasos 1…4** (10–12 s cada uno) | Cada paso es una pregunta corta + la respuesta en 1–2 frases + un dato. | Cartel numerado, corte transversal, callouts con línea |
| 60–72 s | **Todo junto** | Encadenar los pasos en una frase. | Vista completa en rayos X, todas las etiquetas a la vez |
| 72–82 s | **Acelerón** | El número del gancho, ahora entendido. | Velocímetro sube: 1000x, 100x, 10x, REAL SPEED |
| 82–90 s | **Remate + bucle** | Dato final sorprendente que **termina donde empieza la primera frase**. | Vuelve al plano exacto del segundo 0 |

## 5. Especificaciones técnicas

| Parámetro | Valor |
|---|---|
| Resolución | 1080x1920 (9:16), según los metadatos originales |
| FPS | 30 (las grabaciones son de 59,94 fps porque son de pantalla; para una animación 2D, 30 basta) |
| Códec | H.264 High, yuv420p, AAC 44,1 kHz estéreo, `+faststart` |
| Sonoridad total | **−14 LUFS integrado** (los tres miden −14,0 / −14,0 / −13,8), pico < −1 dBTP |
| LRA | 2–4 LU (muy comprimido, nivel constante) |
| Voz (variante B) | −14 LUFS, música **ausente** bajo la voz |
| Música (si la usamos, variante híbrida) | −32 a −30 LUFS bajo la voz (≈ −18 dB por debajo), sube a −16 LUFS en el acelerón final sin voz |
| SFX | Golpe en cada cambio de cartel e icono; −20 LUFS aprox. |
| **Subtítulos** | Arriba, centrados, línea base en **y ≈ 300 px** (16 % del alto); 2–4 palabras por bloque, ~1 s cada uno |
| Fuente subtítulos | Sans-serif bold redondeada (tipo Inter/Montserrat Bold), **~62 px**, sin contorno, sin caja, sombra suave |
| Color subtítulos | Blanco **#FFFFFF**; palabra clave en amarillo **#F2C94C** (medido #EADB83 en el video comprimido) |
| Cartel de paso | Slab serif gruesa (tipo "Alfa Slab One"), texto **#1B1925** + **#BC3A38** sobre crema **#FFEEE0**, borde **#A6613A** |
| Fondo | Gradiente **#282336 → #17161D** (violeta marino oscuro) |
| Acentos | Naranja **#E27E56** / **#CC7B3E**, rojo **#BF5B45**, crema **#F3EAD1**, azul acero **#526DA9** |
| Etiquetas (callouts) | Mayúsculas pequeñas ~30 px, blanco sobre negro o negro sobre crema, línea guía 2 px |
| Zona segura | Nada importante en los 280 px de abajo ni en los 140 px de la derecha (UI de Instagram/YouTube) |

## 6. Propuesta para tu video (necesito tu OK al decir "sigue")

Los tres videos mezclan dos variantes. Tú quieres un video **en español, de 1–2 min**, y para eso hace falta narración.
Propongo un **híbrido**: el *formato* de engineeredwithin (pasos numerados, cámara lenta con velocímetro, acelerón final,
bucle) con la *voz y los subtítulos* de curios0n.

- **Tema elegido: "¿Cómo calienta la comida un microondas?"**. Es una pregunta cotidiana, tiene un número imposible
  (las moléculas de agua giran **2.450 millones de veces por segundo**: 2,45 GHz es la frecuencia estándar de los
  microondas domésticos) y un mecanismo por capas (enchufe → magnetrón → ondas que rebotan → agua que gira → calor).
  Además tiene un remate que conecta con el inicio: **por qué gira el plato** (las ondas estacionarias dejan puntos
  calientes y fríos). Todo lo puedo dibujar con código, sin usar material de nadie.
- **Duración**: 80–90 s.
- **Palabrotas**: ref3 usa "puto/puta" 10 veces. Por defecto las dejo en **2–3, solo en el gancho y el remate**, para
  que sea apto para más plataformas y no se pierda el tono. Dime si las quieres **como ref3**, **suaves** (por defecto) o
  **ninguna**.
- **Voz**: `es-ES-AlvaroNeural` (edge-tts), masculina, a +15 % de velocidad para acercarme a 168 ppm.
  Alternativa: `es-MX-JorgeNeural`.
