# Changelog - Network Diagnostic Tool

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

---

## [v1.25.3] - 2026-05-05

### Fixed
- Test 8: Ahora muestra TODAS las interfaces de red activas (no solo una)
- Test 8: Muestra múltiples adapters (Ethernet, WiFi, VirtualBox, etc.)

---

## [v1.25.2] - 2026-05-05

### Fixed
- Test 8: Fix PowerShell para obtener detalles de interfaz de red en Windows

---

## [v1.25.1] - 2026-05-05

### Fixed
- Test 12 (DHCP): Ahora muestra múltiples interfaces de red (no solo una)
- Test 12: Muestra estado DHCP, IP, máscara, gateway, DNS, servidor DHCP y lease por cada interfaz
- run_command(): Fix para ejecutar ipconfig/netsh en Windows (usa cmd /c)

---

## [v1.25.0] - 2026-04-24

### Added
- Test 14: MTU Path con tracepath y sugerencias específicas

---

## [v1.24.5] - 2026-04-24

### Updated
- README con enlaces a TODO, CHANGELOG, Diagnostico
- Diagnostico con lista de mejoras pendientes

---

## [v1.24.3] - 2026-04-23

### Updated
- Diagnostico.md: Documentación completa con los 16 tests implementados
- Agregada sección de argumentos CLI

---

## [v1.24.2] - 2026-04-23

### Updated
- README.md: Documentación de argumentos y tests 13-16
- Diagnostico.md: Tests 13-16 con reglas activas

---

## [v1.24.1] - 2026-04-23

### Added
- Help mejorado con ejemplos y lista de tests disponibles

---

## [v1.24.0] - 2026-04-23

### Added
- Test 16: Conexiones Simultáneas (TCP + HTTP concurrentes)

---

## [v1.23.1] - 2026-04-23

### Fixed
- Doble título en test 15 (DNS Alternativos)
- Sugerencia de DNS óptimos cuando no hay mejor alternativo

---

## [v1.23.0] - 2026-04-23

### Added
- Comparación DNS configurados vs alternativos
- Sugerencia de cambio si alternativo es >10ms más rápido

---

## [v1.22.0] - 2026-04-23

### Added
- Test 15: DNS Alternativos

---

## [v1.21.1] - 2026-04-23

### Fixed
- Doble título en test 13 y 14
- Suggestions muestran "→ " cuando comando vacío

---

## [v1.21.0] - 2026-04-23

### Added
- Test 14: MTU (fragmentación)
- Test 13: Bufferbloat separado

---

## [v1.20.1] - 2026-04-23

### Changed
- Test de Bufferbloat separado como Test 13

---

## [v1.20.0] - 2026-04-23

### Added
- Test de Bufferbloat (QoS) integrado en Test 11

---

## [v1.19.9] - 2026-04-23

### Added
- Test 10: Detección de latencia por hop (congestión)

---

## [v1.19.8] - 2026-04-23

### Added
- Test 8: Detección de half-duplex

---

## [v1.19.7] - 2026-04-23

### Added
- Test 4: Detección de latencia base alta (>50ms)

---

## [v1.19.6] - 2026-04-23

### Added
- Test 2: Detección de DNS lento (>2s)

---

## [v1.19.5] - 2026-04-23

### Fixed
- Comandos ahora son compatibles con Windows y Linux (SYS_COMMANDS + get_cmd())
- Sugerencias de troubleshooting muestran comandos según el SO

---

## [v1.19.4] - 2026-04-23

### Fixed
- sugerencias de troubleshooting y pie de página ahora se guardan en archivo de texto

---

## [v1.19.3] - 2026-04-23

### Fixed
- Archivo de texto ahora es idéntico al output de pantalla (usa DualOutput)

---

## [v1.19.2] - 2026-04-23

### Fixed
- Sugerencias de troubleshooting ahora se guardan en archivo de texto

---

## [v1.19.1] - 2026-04-23

### Fixed
- parse_test_string() ahora soporta "dns-configured" como nombre de test

---

## [v1.18] - 2026-04-23

### Agregado
- Tests 10-12 con sugerencias de troubleshooting
- analyze_test_10() para traceroute (timeouts, ruta degradada)
- analyze_test_11() para velocidad (download/upload bajo)
- analyze_test_12() para DHCP (IP estática)

### Fixed
- analyze_test_10() llamado desde main()

---

## [v1.17] - 2026-04-23

### Agregado
- Sistema completo de sugerencias de troubleshooting automático
- Funciones analyze_test_1() a analyze_test_9() para análisis de resultados
- Niveles de severidad: 🔴 CRÍTICO, 🟡 ADVERTENCIA, ℹ️ INFO

### Fixed
- test_packet_loss() función restaurada
- test_internet_speed() función restaurada
- test_ping() retorna (ok, latency)
- test_port() retorna True/False
- test_dns_verification() retorna True/False
- parse_test_string() maneja "2b"

---

## [v1.14] - 2026-04-23

### Agregado
- Primeros analyze_test para tests 1, 2, 2b, 3
- Sistema de sugerencias con niveles

---

## [v1.13] - 2026-04-22

### Agregado
- tempfile.org como servidor de upload fallback (~2 Mbps)
- oshi.io como servidor de upload fallback (~1 Mbps)
- Orden de upload: cloudflare → tempfile.org → oshi.io (fallback automático)

### Fixed
- Upload usa campo configurable (`upload_field`) para diferentes APIs

---

## [v1.7] - 2026-04-20

### Agregado
- Tests paralelos con `--parallel` (usa ThreadPoolExecutor)
- Tests rápidos en paralelo: 1, 2, 2b, 3, 4, 5, 6, 8, 9, 12
- Tests lentos secuenciales: 7 (pérdida), 10 (traceroute), 11 (speed)
- Backward compatible: sin `--parallel` ejecuta secuencialmente

---

## [v1.6] - 2026-04-20

### Agregado
- Speed test configurable: `--speed-size` (tamaño en MB)
- Soporte para diferentes tamaños de download/upload (`--speed-size 5,10`)
- Selección de servidores: `--speed-servers` (cloudflare, nperf, tele2)

---

## [v1.5] - 2026-04-20

### Agregado
- Sistema de argumentos CLI (argparse)
- Menú interactivo (`-i`)
- Selección de tests por número o nombre
- Soporte para rangos (`1-5`)
- Opciones `--no-speed` y `--no-isp`
- Formato JSON output (`--format json`)
- Sistema de preferencias (CFG)
- Backward compatible: sin args ejecuta todos los tests

---

## [v1.4] - 2026-04-20

### Agregado
- Verificación de dependencias opcionales en Linux
- Muestra advertencia al inicio si faltan dependencias
- Dependencias verificadas: iw, ethtool, traceroute, ufw, iptables
- Código limpio: eliminado import os duplicado

---

## [v1.3] - 2026-04-20

### Agregado
- Test 12: Información DHCP
- Muestra estado DHCP (habilitado/deshabilitado)
- Detecta IP estática vs dinámica

---

## [v1.2] - 2026-04-20

### Agregado
- Test 11: Velocidad de internet
- Download + Upload test
- Servidores: Cloudflare, nperf, Tele2
- 5MB por test

### Fixed
- Upload method changed to --data-binary
- nperf URL actualizada
- UTF-8 decode error en upload

---

## [v1.1] - 2026-04-20

### Agregado
- Test 10: Traceroute
- Destinos: YouTube (CDN), Yahoo (IPTransit)
- Muestra: IP, DNS reverso, saltos

---

## [v1.0] - 2026-04-20

### Agregado
- Test 9: Estado del firewall
- Muestra: Dominio, Privado, Publico, Reglas activas

---

## [v0.9] - 2026-04-20

### Agregado
- Test 8: Detalles del interfaz de red
- Muestra: Nombre, Descripcion, Estado, MAC, Velocidad

---

## [v0.8] - 2026-04-20

### Agregado
- Test 2B: Servidores DNS configurados
- Muestra los DNS del sistema
- Verifica puerto 53 de cada DNS

---

## [v0.7] - 2026-04-20

### Agregado
- Test 7: Detección de pérdida de paquetes
- Muestra: Enviados, Recibidos, Perdidos, Porcentaje
- Testea Google DNS (8.8.8.8) y Cloudflare (1.1.1.1)

---

## [v0.6] - 2026-04-20

### Agregado
- Test 6: Información del ISP
- Muestra: IP pública, ISP, Organización, Ubicación
- Usa ip-api.com (gratuito)

---

## [v0.5] - 2026-04-20

### Agregado
- Test 5: Detección de señal WiFi
- Detección automática de tipo de conexión (WiFi/Ethernet)
- Compatible con Windows (`netsh wlan`) y Linux (`iw`)
- Muestra: SSID, Signal, Channel, Radio Type, BSSID, Tx/Rx Rate

---

## [v0.4] - 2025

### Agregado
- Compatibilidad con Windows/Linux
- Soporte para codificación UTF-8 en Windows

---

## [v0.3] y anteriores

Versiones iniciales del proyecto por Xabier Pereira.

---

## Información

- **Autor Original**: Xabier Pereira
- **Modificado por**: Ignacio Peroni
- **GitHub**: https://github.com/iperoni/Network
