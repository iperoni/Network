# TODO - Network Diagnostic Tool

Lista de mejoras pendientes para el proyecto.

## v1.20.1 - Completado

- [x] Test 13: Bufferbloat (QoS) separado

## v1.20.0 - Completado

## v1.19.9 - Completado

- [x] Test 10: Detección de latencia por hop (congestión)

## v1.19.8 - Completado

- [x] Test 8: Detección de half-duplex

## v1.19.7 - Completado

- [x] Test 4: Detección de latencia base alta (>50ms)

## v1.19.6 - Completado

- [x] Test 2: Detección de DNS lento (>2s)

## v1.19.5 - Completado

- [x] Fix: Comandos compatibles Windows/Linux

## v1.19.4 - Completado

- [x] Fix: Sugerencias de troubleshooting y pie de página se guardan en archivo

## v1.19.3 - Completado

- [x] Fix: Archivo de texto idéntico al output de pantalla

## v1.19.2 - Completado

- [x] Fix: Sugerencias de troubleshooting se guardan en archivo de texto

## v1.19.1 - Completado

- [x] Fix: parse_test_string() soporta "dns-configured"

## Alta Prioridad

- [x] Tests paralelos - Ejecutar tests independientes (ping, DNS, speed) en paralelo para reducir tiempo total
- [x] Menú interactivo - Permitir seleccionar qué tests ejecutar
- [x] Args/flags - Añadir argumentos CLI (`--no-speed`, `--wifi-only`, etc.)
- [x] Modo verbose - Añadir flag `-v` para ver output completo

## Media Prioridad

- [x] Exportar JSON - Opción para exportar resultados a JSON además de TXT (--format json)
- [x] Speed test configurable - Tamaño de archivo personalizable para speed test
- [ ] Timeouts configurables - Timeouts ajustables para conexiones lentas
- [ ] Retry logic - Reintentos automáticos en tests que fallen
- [x] Upload fallback servers - Múltiples servidores de upload con fallback automático

## Baja Prioridad

- [ ] Soporte macOS - Añadir compatibilidad para macOS (airport, networksetup)
- [ ] Dashboard HTML - Generar reporte HTML interactivo
- [ ] Comparar resultados - Comparar resultados entre ejecuciones
- [ ] Notificaciones - Notificaciones cuando el estado cambia

## Código

- [ ] Test unitarios - Añadir pytest para las funciones principales
- [ ] Type hints - Añadir typing a las funciones
- [ ] Logging - Usar logging en vez de print

---

## Refactorización

- [x] Eliminar duplicados en TESTS_MAP
- [x] Crear constantes globales (IS_WINDOWS, TIMEOUTS, etc.)
- [x] Extraer configuración a constantes
- [x] Reducir duplicación de código
- [ ] Dividir funciones largas (main(), test_internet_speed())
- [ ] Agregar type hints
- [ ] Unificar manejo de errores

---

## Bugs (Resueltos)

- [x] --tests no funciona correctamente (fix v1.9)
- [x] Reporte TXT incluye tests no ejecutados (fix v1.10)
- [x] Speed test simplificado con fallback (v1.11)
- [x] Upload no funciona (fix v1.12 - Cloudflare usa FormData)
- [x] Upload solo un servidor (fix v1.13 - tempfile.org + oshi.io fallback)
- [x] Troubleshooting suggestions (v1.14-v1.17 - tests 1-9)
- [x] Funciones faltantes packet_loss, test_internet_speed (v1.17)

---

*Última actualización: 2026-04-23*

*Completado en v1.17: Troubleshooting sistema completo para tests 1-9 + fixing functions*

*Completado en v1.14-v1.16: Sugerencias de troubleshooting para tests 1-9*

*Pendiente: Tests 10-12, macOS, Dashboard, Comparar resultados, Notificaciones*