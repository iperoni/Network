# Network Diagnostic Tool (v0.6)

Herramienta de diagnóstico de conectividad de red para Windows y Linux.

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
- Compatible con Windows y Linux
- Soporte para codificación UTF-8 en Windows
- Detección automática del sistema operativo

## Requisitos

### Windows
- Python 3.x instalado
- No requiere dependencias adicionales (usa librerías estándar)

### Linux
- Python 3.x instalado
- Paquete `iw` instalado (para test WiFi): `sudo apt install iw`
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

```bash
python network_diagnostic.py
```

O en Linux:
```bash
chmod +x network_diagnostic.py
./network_diagnostic.py
```

## Historial de Cambios

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
- Mejoras en兼容性 con Windows/Linux
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