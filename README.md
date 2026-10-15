# Subway Surfers PS Vita — laboratorio de actualización

**Estado: herramientas de análisis y pruebas listas. No hay una actualización jugable ni un parche de rendimiento validado.**

Proyecto comunitario *no oficial* para estudiar mejoras del port de Subway Surfers para PS Vita, manteniendo los archivos originales fuera del repositorio. No afiliado a SYBO, Sony ni Unity. Crédito al port de 2025 publicado por **marcellus00**.

## VPK base identificado
- ID del título: `SUSU01010`
- Versión declarada en SFO: `01.00`
- Motor: `Unity 2018.2.19f1` / IL2CPP
- Binarios: `eboot.bin` y `Media/Modules/il2CppAssemblies.suprx`
- SHA-256 del VPK examinado: `d6c330b020b960b0c2c79afafa762a1a04eb8013f081a41f380dd38b513dbb7d`
- La estructura ZIP del ejemplar analizado pasó la verificación de integridad.

## Objetivos
Analizar estabilidad de FPS, tiempos de carga y problemas gráficos. Solo se publicarán mejoras después de implementarlas y verificarlas en una PS Vita real.

## Herramientas
**Auditar el VPK local sin subirlo a GitHub:**
```bash
python tools/audit_vpk.py "Subway Surfers new.vpk" --json auditoria.json
```

**Comparar muestras de FPS:**
```bash
python tools/compare_fps.py tests/ejemplo_fps.csv
```

**Preparar una copia con un archivo de reemplazo previamente desarrollado y validado:**
```bash
python tools/repack_vpk.py "Subway Surfers new.vpk" "Subway Surfers prueba.vpk" \
 --expected-sha d6c330b020b960b0c2c79afafa762a1a04eb8013f081a41f380dd38b513dbb7d \
 --replace Media/boot.config=mi-boot-validado.config
```
Es solo un ejemplo de empaquetado, **no una optimización**. No se ha desarrollado ni validado un archivo `mi-boot-validado.config`; no cambies `boot.config` arbitrariamente. El programa no sobrescribe el VPK original, exige el hash esperado y verifica la integridad del resultado.

**Ejecutar pruebas:**
```bash
python -m pip install pytest
python -m pytest -q
```

## Trabajo pendiente
- [x] Identificar y auditar el VPK.
- [x] Incorporar analizador ZIP/SFO, repacker conservador y comparador de FPS.
- [x] Añadir pruebas sintéticas sin archivos originales del juego.
- [ ] Obtener fuentes editables o evaluar cambios autorizados en módulos compilados.
- [ ] Registrar mediciones reproducibles en hardware real.
- [ ] Identificar un cuello de botella y desarrollar una solución.
- [ ] Crear una actualización jugable y validarla en PS Vita.
- [ ] Publicar únicamente parches y código que puedan distribuirse legítimamente.

## Derechos y distribución
Este repositorio **no contiene el VPK, ejecutables, recursos gráficos ni datos comerciales originales**. Los usuarios deben usar sus propios archivos y respetar los derechos de sus titulares. No se debe publicar un VPK completo de terceros sin autorización.

## Referencias
- https://www.gamebrew.org/wiki/Subway_Surfers_Vita
- https://www.reddit.com/r/vitahacks/comments/1n7eo1m/another_port_of_subway_surfers_more_content_and/
