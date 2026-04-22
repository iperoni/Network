# TODO - Network Diagnostic Tool

Lista de mejoras pendientes para el proyecto.

## Alta Prioridad

- [x] Tests paralelos - Ejecutar tests independientes (ping, DNS, speed) en paralelo para reducir tiempo total
- [x] Menú interactivo - Permitir seleccionar qué tests ejecutar
- [x] Args/flags - Añadir argumentos CLI (`--no-speed`, `--wifi-only`, etc.)
- [x] Modo verbose - Añadir flag `-v` para ver output completo

## Media Prioridad

- [x] Exportar JSON - Opción para exportar resultados a JSON además de TXT (--format json)
- [x] Speed test configurable - Tamaño de archivo personalizable para speed test
- [ ] Timeouts configurables - Timeouts ajustables para conexiones lentas
- [ ] Retry logic - Reintentos automáticos en tests quefallen

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

---

*Última actualización: 2026-04-22*

*Completado en v1.9: Bugfix --tests*

*Completado en v1.8: Refactorización - constantes, código limpio*

*Completado en v1.7: Tests paralelos y releases*

*Pendiente: Timeouts, Retry, macOS, Dashboard, Comparar resultados, Notificaciones, Tests unitarios, Logging*