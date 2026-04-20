# TODO - Network Diagnostic Tool

Lista de mejoras pendientes para el proyecto.

## Alta Prioridad

- [ ] Tests paralelos - Ejecutar tests independentes (ping, DNS, speed) en paralelo para reducir tiempo total
- [ ] Menú interactivo - Permitir seleccionar qué tests ejecutar
- [ ] Args/flags - Añadir argumentos CLI (`--no-speed`, `--wifi-only`, etc.)
- [ ] Modo verbose - Añadir flag `-v` para ver output completo

## Media Prioridad

- [ ] Exportar JSON - Opción para exportar resultados a JSON además de TXT
- [ ] Speed test configurable - Tamaño de archivo personalizable para speed test
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

*Última actualización: 2026-04-20*