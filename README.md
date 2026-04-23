# Network Diagnostic Tool (v1.19.6)

Herramienta de diagnóstico de conectividad de red para Windows y Linux con sugerencias de troubleshooting automatizadas.

## Novedades en v1.19.6

- **Added**: Detección de DNS lento (>2s)

## Novedades en v1.19.5

- **Fix**: Comandos compatibles con Windows y Linux

## Novedades en v1.19.4

- **Fix**: Sugerencias de troubleshooting y pie de página ahora se guardan en archivo

## Novedades en v1.19.3

- **Fix**: Archivo de texto idéntico al output de pantalla

## Novedades en v1.19.2

- **Fix**: Sugerencias de troubleshooting ahora se guardan en archivo de texto

## Novedades en v1.19.1

- **Fix**: parse_test_string() ahora soporta "dns-configured" como nombre de test

## Novedades en v1.18

- **Tests 10-12 con sugerencias**: Traceroute, Velocidad, DHCP
- Sistema completo de troubleshooting para todos los tests (1-12)

## Novedades en v1.17

- **Sugerencias de troubleshooting automáticas** para los tests 1-9
- Análisis de resultados con recomendaciones de acción
- Niveles: 🔴 CRÍTICO, 🟡 ADVERTENCIA, ℹ️ INFO

## Tabla de Contenidos

- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Historial de Cambios](#historial-de-cambios)
- [Autor](#autor)
- [Licencia](#licencia)

## Funcionalidades

- Detección de IP real de la interfaz de red activa
- Test de ping a múltiples hosts (Google DNS, Cloudflare, servidores local)
- Verificación de resolución DNS para múltiples dominios
- Test de conectividad a puertos comunes (HTTP, HTTPS, SSH, FTP, etc.)
- Información del servidor DNS configurado
- Detección de pérdida de paquetes
- Detalles del interfaz de red (Windows)
- Estado del firewall (Windows)
- Traceroute
- Test de velocidad de internet (download/upload)
- Información DHCP
- Compatible con Windows y Linux
- Soporte para codificación UTF-8 en Windows
- Detección automática del sistema operativo
- Verificación de dependencias opcionales en Linux

## Requisitos

### Windows
- Python 3.x instalado
- No requiere dependencias adicionales (usa librerías estándar)

### Linux
- Python 3.x instalado
- Dependencias opcionales (se verifica automáticamente):
  - `iw` - Test de señal WiFi
  - `ethtool` - Detalles del interfaz de red
  - `traceroute` - Test traceroute
  - `ufw` - Estado del firewall (UFW)
  - `iptables` - Estado del firewall (iptables)
- Instalación: `sudo apt install iw ethtool traceroute ufw iptables`
- Módulos estándar de Python:
  - socket
  - subprocess
  - platform
  - datetime

## Instalación

```bash
git clone https://github.com/iperoni/Network.git
cd Network
```

## Uso

### Básico

```bash
python network_diagnostic.py
```

O en Linux:
```bash
chmod +x network_diagnostic.py
./network_diagnostic.py
```

### Menú Interactivo

```bash
python network_diagnostic.py -i
```

### Argumentos CLI

```bash
# Ejecutar tests específicos por número
python network_diagnostic.py --tests 1,2,5,11
python network_diagnostic.py --tests 1-5          # Rango
python network_diagnostic.py --tests 1-7,9       # Combinado

# Ejecutar tests por nombre
python network_diagnostic.py --tests internet,wifi,speed
python network_diagnostic.py --tests connectivity,dns-configured,firewall

# Omitir tests lentos
python network_diagnostic.py --no-speed            # Omitir test de velocidad
python network_diagnostic.py --no-isp             # Omitir consulta ISP

# Speed test configurable
python network_diagnostic.py --speed-size 20         # 20MB (default)
python network_diagnostic.py --speed-size 10         # 10MB personalizado

# Formato de output
python network_diagnostic.py -o mis-resultados.txt
python network_diagnostic.py --format json -o resultado.json

# Opciones adicionales
python network_diagnostic.py -v                   # Verbose
python network_diagnostic.py --version             # Mostrar versión
python network_diagnostic.py --help               # Ver ayuda
python network_diagnostic.py --save-prefs          # Guardar preferencias
python network_diagnostic.py --parallel            # Ejecutar tests en paralelo
```

### Tabla de Tests

| # | Nombre | Descripción |
|---|--------|-------------|
| 1 | connectivity | Conectividad local (loopback, gateway) |
| 2 | internet | Internet y DNS |
| 2b | dns-configured | Servidores DNS configurados |
| 3 | ports | Puertos críticos (443, 53) |
| 4 | latency | Estadísticas de latencia |
| 5 | wifi | Señal WiFi |
| 6 | isp | Información del ISP |
| 7 | packet-loss | Pérdida de paquetes |
| 8 | interface | Detalles del interfaz de red |
| 9 | firewall | Estado del firewall |
| 10 | traceroute | Ruta hacia destinos |
| 11 | speed | Velocidad de internet |
| 12 | dhcp | Información DHCP |

### Preferencias

Las preferencias se guardan en `network_diagnostic.cfg` en el directorio del script.

### Tests Paralelos

Por defecto, los tests se ejecutan secuencialmente. Con `--parallel` se ejecutan en paralelo:

```bash
python network_diagnostic.py --parallel              # Todos los tests en paralelo
python network_diagnostic.py --parallel --tests 1,2,5,6  # Solo tests específicos
```

**Tests que se ejecutan en paralelo**: 1, 2, 2b, 3, 4, 5, 6, 8, 9, 12

**Tests que siempre son secuenciales**: 7 (pérdida), 10 (traceroute), 11 (speed)

## Historial de Cambios

### v1.17 (2026)
**Modificado por: Ignacio Peroni**

- Sistema de sugerencias de troubleshooting automático
- Análisis de resultados con niveles: 🔴 CRÍTICO, 🟡 ADVERTENCIA, ℹ️ INFO
- Nuevas funciones analyze_test_1() a analyze_test_9()
- Tests 1-9 con sugerencias automáticas basadas en resultados
- Fix: test_packet_loss, test_internet_speed funciones agregadas

### v1.16 (2026)
**Modificado por: Ignacio Peroni**

- Fix: test_ping ahora retorna (ok, latency)
- Fix: test_port retorna True/False
- Fix: test_dns_verification retorna True/False
- Fix: parse_test_string maneja "2b"

### v1.15 (2026)
**Modificado por: Ignacio Peroni**

- Agregado troubleshooting para tests 1-7: latency, wifi, isp, packet loss
- Funciones analyze_test_4() a analyze_test_7()

### v1.14 (2026)
**Modificado por: Ignacio Peroni**

- Sistema de sugerencias de troubleshooting inicial
- Tests 1, 2, 2B, 3 con análisis de resultados

### v1.13 (2026)
**Modificado por: Ignacio Peroni**

- Servidores de upload adicionales: tempfile.org y oshi.io como fallback
- Orden de upload: cloudflare → tempfile.org → oshi.io
- Fallback automático: si cloudflare falla, prueba tempfile.org, si falla, prueba oshi.io
- tempfile.org: ~2 Mbps upload (servidor temporal de archivos, expira en 1-48h)
- oshi.io: ~1 Mbps upload

### v1.12 (2026)
**Modificado por: Ignacio Peroni**

- Fix upload: Cloudflare ahora usa FormData (`-F`) en lugar de `--data-binary`
- Tele2 NO DISPONIBLE (requiere autenticación)
- Upload reparado exitosamente

### v1.11 (2026)
**Modificado por: Ignacio Peroni**

- Speed test simplificado con fallback automático
- Orden de servidores: cloudflare → nperf → tele2
- Tamaño por defecto: 20MB
- Muestra solo el resultado del servidor que funcionó

### v1.10 (2026)
**Modificado por: Ignacio Peroni**

- Fix: Reporte TXT solo incluye tests ejecutados
- Tests no ejecutados no se escriben en el archivo

### v1.9 (2026)
**Modificado por: Ignacio Peroni**

- Bugfix: `--tests` ahora funciona correctamente
- Fix en `parse_test_string()` para aceptar números directamente

### v1.8 (2026)
**Modificado por: Ignacio Peroni**

- Refactorización del código: constantes globales extraídas
- IS_WINDOWS, TIMEOUT_DEFAULT, TIMEOUT_LONG, etc.
- TEST_HOSTS para hosts de test
- DOWNLOAD_SERVERS / UPLOAD_SERVERS extraídos
- LINUX_DEPS / LINUX_FEATURES constantes
- Código duplicado y muerto eliminado
- ~220 líneas reducidas

### v1.7 (2026)
**Modificado por: Ignacio Peroni**

- Tests paralelos con `--parallel` (usa ThreadPoolExecutor)
- Tests rápidos en paralelo: 1, 2, 2b, 3, 4, 5, 6, 8, 9, 12
- Tests lentos secuenciales: 7 (pérdida), 10 (traceroute), 11 (speed)
- Backward compatible: sin `--parallel` ejecuta secuencialmente

### v1.6 (2026)
**Modificado por: Ignacio Peroni**

- Speed test configurable: `--speed-size` (tamaño en MB)
- Soporte para diferentes tamaños de download/upload (`--speed-size 5,10`)
- Selección de servidores: `--speed-servers` (cloudflare, nperf, tele2)

### v1.5 (2026)
**Modificado por: Ignacio Peroni**

- Agregado sistema de argumentos CLI (argparse)
- Agregado menú interactivo (`-i`)
- Agregada selección de tests por número o nombre
- Agregado soporte para rangos (`1-5`)
- Agregadas opciones `--no-speed` y `--no-isp`
- Agregado formato JSON output
- Agregado sistema de preferencias (CFG)
- Backward compatible: sin args ejecuta todos los tests

### v1.4 (2026)
**Modificado por: Ignacio Peroni**

- Agregada verificación de dependencias opcionales en Linux
- Muestra advertencia al inicio si faltan зависиcias
- Dependencias verificadas: iw, ethtool, traceroute, ufw, iptables
- Código limpio: eliminado import os duplicado

### v1.3 (2026)
**Modificado por: Ignacio Peroni**

- Agregado Test 12: Información DHCP
- Muestra estado DHCP (habilitado/deshabilitado)
- Detecta IP estática vs dinámica

### v1.2.5 (2026)
**Modificado por: Ignacio Peroni**

- Fix: Upload method changed to --data-binary
- Cloudflare upload no soportado actualmente

### v1.2.4 (2026)
**Modificado por: Ignacio Peroni**

- Fix: nperf URL actualizada (ahora funciona)
- Fix: UTF-8 decode error en upload
- Test de velocidad: Cloudflare, nperf, Tele2

### v1.2.3 (2026)
**Modificado por: Ignacio Peroni**

- Fix: Mejor manejo de errores en test de velocidad
- Mensaje más claro cuando el servidor falla

### v1.2.2 (2026)
**Modificado por: Ignacio Peroni**

- Fix: Test de velocidad con opciones mejoradas de curl
- Cloudflare download ahora funciona correctamente

### v1.2.1 (2026)
**Modificado por: Ignacio Peroni**

- Fix: Traceroute ahora muestra tiempos de ping correctamente
- Mejor parsing con regex

### v1.2 (2026)
**Modificado por: Ignacio Peroni**

- Agregado Test 11: Velocidad de internet
- Download + Upload test
- Servidores: Cloudflare, nperf, Tele2
- 5MB por test

### v1.1 (2026)
**Modificado por: Ignacio Peroni**

- Agregado Test 10: Traceroute
- Destinos: YouTube (CDN), Yahoo (IPTransit)
- Muestra: IP, DNS reverso, saltos

### v1.0 (2026) - Stable
**Modificado por: Ignacio Peroni**

- Agregado Test 9: Estado del firewall
- Muestra: Dominio, Privado, Publico, Reglas activas

### v0.9 (2026) - Beta
**Modificado por: Ignacio Peroni**

- Agregado Test 8: Detalles del interfaz de red
- Muestra: Nombre, Descripcion, Estado, MAC, Velocidad

### v0.8 (2026) - Beta
**Modificado por: Ignacio Peroni**

- Agregado Test 2B: Servidores DNS configurados
- Muestra los DNS del sistema
- Verifica puerto 53 de cada DNS

### v0.7.1 (2026) - Beta
**Modificado por: Ignacio Peroni**

- Fix: Mostrar porcentaje de paquetes perdidos en pantalla y archivo

### v0.7 (2026) - Beta
**Modificado por: Ignacio Peroni**

- Agregado Test 7: Detección de pérdida de paquetes
- Muestra: Enviados, Recibidos, Perdidos, Porcentaje
- Testea Google DNS (8.8.8.8) y Cloudflare (1.1.1.1)

### v0.6 (2026) - Beta
**Modificado por: Ignacio Peroni**

- Agregado Test 6: Información del ISP
- Muestra: IP pública, ISP, Organización, Ubicación
- Usa ip-api.com (gratuito)

### v0.5 (2026) - Beta
**Modificado por: Ignacio Peroni**

- Agregado Test 5: Detección de señal WiFi
- Detección automática de tipo de conexión (WiFi/Ethernet)
- Compatible con Windows (`netsh wlan`) y Linux (`iw`)
- Muestra: SSID, Signal, Channel, Radio Type, BSSID, Tx/Rx Rate
- Guardado de resultados en archivo

### v0.4 (2025) - Beta
**Modificado por: Ignacio Peroni**

- Actualización a versión v0.4
- Mejoras en compatibilidad con Windows/Linux
- Soporte para codificación UTF-8 en Windows
- Actualización de información del autor

### v2.0 (Original)
**Autor: Xabier Pereira**

- Diagnóstico completo de conectividad de red
- Test de ping a hosts (Google DNS, Cloudflare)
- Verificación de resolución DNS
- Test de conectividad a puertos comunes
- Compatible con Windows y Linux

---

## Autor

- Original: [Xabier Pereira](https://github.com/xabierpereira)
- Modificado por: [Ignacio Peroni](https://github.com/iperoni)

## Licencia

MIT