# v1.1-pre2: modo Ultra Ligero, experimental

Este modo es una prueba adicional orientada a reducir la carga gráfica, **no una aceleración de FPS demostrada**. El VPK generado se ha comprobado como archivo ZIP, pero todavía no está probado en una PS Vita real.

| Parámetro Unity | Original | Ligero (pre1) | Ultra Ligero (pre2) |
|---|---:|---:|---:|
| `textureQuality` | 0 | 1 | 2 |
| `anisotropicTextures` | 1 | 0 | 0 |
| `lodBias` | 1.0 | 0.7 | 0.5 |
| `particleRaycastBudget` | 256 | 64 | 32 |

No cambia la resolución del framebuffer, los shaders compilados, los ejecutables, la lógica del juego ni el bloqueo de FPS. Unity puede ignorar o sobrescribir estos ajustes en tiempo de ejecución; por tanto el rendimiento podría ser idéntico y las texturas verse más borrosas.

## Crear desde tu VPK original

1. Necesitas el **VPK original** con SHA-256 `d6c330b020b960b0c2c79afafa762a1a04eb8013f081a41f380dd38b513dbb7d`.
2. Ejecuta desde la carpeta del repositorio:

```powershell
python tools/quality_patch.py "Subway Surfers new.vpk" "SubwaySurfers_Vita_UltraLigero_Experimental.vpk" --modo ultraligero
```

3. El SHA-256 esperado del VPK es `322f95262b4fc9fcd9f3dcfdcaa3ba5a6a9296009b4f4907bf812e8866849c93`.
4. Este script concreto requiere el original, **no** un VPK modificado. También existe un constructor independiente para probar desde el VPK experimental anterior, pero el repositorio mantiene el flujo desde el original para minimizar variantes.

## PSVshell, VSync y pruebas

El creador del port indica que **VSync activado limita a 30 FPS** y que recomienda overclock en CPU y GPU; reportó hasta ~45 FPS, no constantes (fuente: https://www.reddit.com/r/vitahacks/comments/1n7eo1m/another_port_of_subway_surfers_more_content_and/ ).

- Desactiva VSync en la configuración **dentro del juego** para comprobar si supera 30 FPS. Puede causar tearing visual.
- Prueba un perfil únicamente para este juego con CPU 500 MHz y GPU 222 MHz usando PSVshell; BUS 222 y XBAR 166 pueden dejarse tal como estén si ya tienen esos valores.
- Mantén los mismos relojes y VSync en ambas pruebas para comparar la variante pre1 con pre2. Mide tramos equivalentes e identifica tirones y calidad de texturas.
- Haz una copia de tu partida. Al conservar el Title ID `SUSU01010`, instalar otro VPK puede sustituir la aplicación existente.
- Si notas cierres o errores gráficos, reinstala la versión que funcionaba. El perfil Ultra Ligero no ha sido probado en hardware y puede reducir la calidad visual más de lo deseable.

## Validación realizada

- ZIP: integridad correcta, 44 entradas intactas.
- Comparación con el VPK pre1: solo `Media/globalgamemanagers` alterado; 5 bytes cambiados.
- Comparación con original: mismo contenido del archivo de ajustes generable de forma reproducible.
- SHA-256: `322f95262b4fc9fcd9f3dcfdcaa3ba5a6a9296009b4f4907bf812e8866849c93`.
- **Sin mediciones de FPS ni prueba de arranque en PS Vita para pre2.**

Los VPK con datos comerciales no se distribuyen públicamente en el repositorio.
