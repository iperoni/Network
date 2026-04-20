# Changelog - Network Diagnostic Tool

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

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
