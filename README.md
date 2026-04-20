# Network Diagnostic Tool (v0.4)

Herramienta de diagnóstico de conectividad de red para Windows y Linux.

## Funcionalidades

- Detección de IP real de la interfaz de red activa
- Test de ping a múltiples hosts (Google DNS, Cloudflare, servidores local)
- Verificación de resolución DNS para múltiples dominios
- Test de conectividad a puertos comunes (HTTP, HTTPS, SSH, FTP, etc.)
- Compatible con Windows y Linux

## Requisitos

### Windows
- Python 3.x instalado
- No requiere dependencias adicionales (usa librerías estándar)

### Linux
- Python 3.x instalado
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

## Autor

- Original: Xabier Pereira
- Modificado por: Ignacio Peroni

## Licencia

MIT