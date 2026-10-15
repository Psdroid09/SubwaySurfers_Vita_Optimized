# v1.1-pre1: modo ligero (EXPERIMENTAL)

Se ha creado un parche binario específico para el VPK base comprobado (SHA-256: `d6c330b020b960b0c2c79afafa762a1a04eb8013f081a41f380dd38b513dbb7d`).

**Todavía no ha sido probado en hardware PS Vita; no se han medido FPS y no se garantiza ni rendimiento ni arranque.**

## Cambios al perfil Unity QualitySettings "Good"

| Propiedad | Original | Modo ligero | Modo equilibrado |
| --- | ---: | ---: | ---: |
| textureQuality | 0 (texturas completas) | 1 (primer mipmap, si existe) | 0 |
| anisotropicTextures | 1 (por textura) | 0 | 0 |
| lodBias | 1.0 | 0.7 | 0.8 |
| particleRaycastBudget | 256 | 64 | 128 |

No se modifican `eboot.bin`, módulos `.suprx`, VSync ni controles.

### Generación local

Desde la carpeta del repositorio, usando **tu propia copia** del VPK exacto:

```powershell
python tools/quality_patch.py "Subway Surfers new.vpk" "SubwaySurfers_Vita_Ligero_Experimental.vpk" --modo ligero --reporte quality_report.json
```

Para texturas completas: cambia a `--modo equilibrado` y otro archivo de salida.

La versión ligera construida localmente produjo el hash SHA-256:
`d228888498a79fda88af66ee0ffc08337812ba69a14fcaa786800504ae820460`.

### Cómo probarlo

1. Respalda tus partidas y conserva el VPK original. Se conserva el Title ID `SUSU01010`, de modo que la instalación podría reemplazar la existente.
2. Prueba el arranque, menú, carrera, cambios de carril, salto, tabla, pausa, guardado y cierre a frecuencias normales.
3. Verifica VSync activado y desactivado por separado. Haz mediciones de FPS antes/después en tramos equivalentes, sin cambiar otras condiciones.
4. Busca texturas borrosas o elementos visuales ausentes, cierres inesperados y problemas de guardado. Si falla, reinstala el VPK original y, si es necesario, restaura el respaldo.

**Alcance de las pruebas:** validación de serialización Unity 2018.2, 9 tests sintéticos y ZIP sin errores de CRC. No hay perfilado de GPU, benchmark ni ejecución en hardware.
