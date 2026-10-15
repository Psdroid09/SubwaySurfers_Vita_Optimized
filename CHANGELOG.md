# Historial de cambios

## Herramientas iniciales — 2026-10-14
- Auditoría del VPK: ZIP, SFO, motor Unity, integridad y SHA-256.
- Reempaquetador reproducible para archivos reemplazados previamente validados.
- Resumen de mediciones de FPS a partir de CSV.
- Pruebas sintéticas automatizadas.
- **Sin modificación del juego; sin optimización de FPS afirmada.**

## v1.1-pre1 — perfil gráfico experimental (2026-10-14)
- Parche de `QualitySettings` con modos equilibrado y ligero, para un VPK de SHA-256 conocido.
- Verificados 7 bytes diferentes dentro de `Media/globalgamemanagers` y todos los demás miembros ZIP idénticos.
- 5 tests nuevos; 9 tests automáticos superados localmente.
- Pendiente confirmar arranque y rendimiento real en PS Vita.
