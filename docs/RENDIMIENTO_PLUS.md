# v1.2-pre — Rendimiento Plus (experimental)

Esta es **una variante experimental, no una mejora de FPS verificada**. La versión Ultra Ligero funcionó en la PS Vita del usuario; el nuevo parche cambia dos parámetros adicionales de QualitySettings de Unity 2018.2.19f1.

| Parámetro | Ultra Ligero | Rendimiento Plus |
|---|---:|---:|
| Calidad de texturas | 2 | 2 (igual) |
| LOD Bias | 0.5 | 0.5 (igual) |
| Filtrado anisotrópico | 0 | 0 (igual) |
| softVegetation | 1 | 0 |
| particleRaycastBudget | 32 | 16 |
| VSync del perfil Unity | 0 | 0 (igual) |

Se deshabilita el renderizado de vegetación en dos pasadas **si el juego usa esa característica** y se reduce el presupuesto de raycasts aproximados de partículas. Es posible que **no haya ninguna mejora de FPS**, ya que el port puede no utilizar esas funciones. Podría cambiar el aspecto de algún elemento vegetal o las colisiones de partículas visuales.

Los valores de pixelLightCount, sombras y antialiasing ya están en cero en el original, por lo que no se redujeron nuevamente. No se modifican la resolución del juego, los ejecutables, la lógica de los controles ni los límites de FPS.

## Generación del VPK local

Se requiere el VPK exacto de Ultra Ligero v1.1 (SHA-256 322f95262b4fc9fcd9f3dcfdcaa3ba5a6a9296009b4f4907bf812e8866849c93):

~~~powershell
python tools/performance_plus.py "SubwaySurfers_Vita_UltraLigero_Experimental.vpk" "SubwaySurfers_Vita_RendimientoPlus_Experimental.vpk" --report reporte.json
~~~

Resultado verificado localmente: SHA-256 029698535ca2d6a22fa78c073f436436aef365bb9c5ece6bbc77e591f20d0c77.

**Conserva la versión anterior y respalda tus partidas antes de sustituir la instalación.** Al compartir ID de título SUSU01010, el nuevo VPK se instala encima del anterior.

## Comparar FPS con el mismo recorrido

- Comprueba VSync desactivado *dentro del juego* para explorar más de 30 FPS. El VSync del asset ya es 0, pero la opción interna puede modificarlo en ejecución.
- Usa PSVShell con el mismo perfil en ambas versiones (CPU y GPU iguales, por ejemplo 500/222 MHz), manteniendo BUS/XBAR como los tengas si no necesitas cambiarlos.
- Haz carreras en escenarios similares. Anota lecturas del contador de FPS en intervalos regulares; registra si ves borrosidad, tearing, cierres y consumo de batería.
- Reúne los números en un CSV perfil,escena,fps (mira tests/ejemplo_fps_v12.csv; son **datos ficticios de ejemplo**, no benchmarks).
- Ejecuta: python tools/fps_compare_v12.py mediciones.csv --salida comparacion.md.
- Si no hay mejora de FPS, vuelve a Ultra Ligero; bajar más la calidad gráfica no tiene por qué ayudar a una limitación de CPU o de los fotogramas del motor.

**Pruebas realizadas:** validación ZIP/CRC del VPK, mismo contenido excepto Media/globalgamemanagers, solo dos bytes modificados respecto a Ultra Ligero, seis pruebas sintéticas superadas. **Sin pruebas de FPS o compatibilidad en PS Vita real para esta nueva variante.**
