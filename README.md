# Network Diagnostic Tool (v1.24.3)

Herramienta de diagnóstico de conectividad de red para Windows y Linux con sugerencias de troubleshooting automatizadas.

## Tabla de Contenidos

- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Tests Disponibles](#tests-disponibles)
- [Argumentos CLI](#argumentos-cli)
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
# Ejecutar todos los tests
python network_diagnostic.py

# Ejecutar tests específicos por número
python network_diagnostic.py --tests 1,2,5,11
python network_diagnostic.py --tests 1-5          # Rango
python network_diagnostic.py --tests 1-7,9       # Combinado

# Ejecutar tests por nombre
python network_diagnostic.py --tests internet,wifi,speed
python network_diagnostic.py --tests connectivity,dns-configured,firewall
python network_diagnostic.py --tests latency,bufferbloat,simul-connections

# Omitir tests lentos
python network_diagnostic.py --no-speed            # Omitir test de velocidad
python network_diagnostic.py --no-isp             # Omitir consulta ISP

# Speed test configurable
python network_diagnostic.py --speed-size 20         # 20MB (default)
python network_diagnostic.py --speed-size 10         # 10MB personalizado

# Formato de output
python network_diagnostic.py -o mis-resultados.txt
python network_diagnostic.py --format json -o resultado.json

# Tests en paralelo (más rápido)
python network_diagnostic.py --parallel

# Opciones adicionales
python network_diagnostic.py -v                   # Verbose
python network_diagnostic.py --version             # Mostrar versión
python network_diagnostic.py --help               # Ver ayuda completa
python network_diagnostic.py --save-prefs          # Guardar preferencias
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
| 13 | bufferbloat | Bufferbloat (QoS) - latencia bajo carga |
| 14 | mtu | MTU óptimo y fragmentación |
| 15 | dns-alternatives | Comparación DNS configurados vs alternativos |
| 16 | simul-connections | Conexiones TCP/HTTP simultáneas |

### Tests por categoría

```bash
# Tests básicos de conectividad
python network_diagnostic.py --tests 1-4

# Tests de red local
python network_diagnostic.py --tests connectivity,ports,interface,dhcp

# Tests de rendimiento
python network_diagnostic.py --tests latency,speed,bufferbloat,simul-connections

# Tests de diagnóstico avanzado
python network_diagnostic.py --tests traceroute,dns-alternatives,m tu
```

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

## Autor

- Original: [Xabier Pereira](https://github.com/xabierpereira)
- Modificado por: [Ignacio Peroni](https://github.com/iperoni)

## Licencia

MIT

---

*Para ver el historial completo de cambios, consulte el archivo CHANGELOG.md*
- Análisis de resultados con recomendaciones de acción
- Niveles: 🔴 CRÍTICO, 🟡 ADVERTENCIA, ℹ️ INFO