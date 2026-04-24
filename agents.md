# Network Diagnostic Tool - Documentación del Agente

## Información del Proyecto

**Nombre**: Network Diagnostic Tool
**Descripción**: Herramienta de diagnóstico de conectividad de red para Windows y Linux con sugerencias de troubleshooting automatizadas
**Autor Original**: Xabier Pereira
**Autor Modificaciones**: Ignacio Peroni (https://github.com/iperoni)
**Repositorio**: https://github.com/iperoni/Network
**Versión Actual**: v1.24.5

---

## Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| `network_diagnostic.py` | Script principal (16 tests) |
| `README.md` | Documentación principal |
| `CHANGELOG.md` | Historial de cambios (Keep a Changelog) |
| `Diagnostico.md` | Detalle de tests y reglas de troubleshooting |
| `TODO.md` | Lista de tareas pendientes y completadas |
| `agents.md` | **(Este archivo)** - Documentación del agente |

---

## Configuración del Entorno

### Rutas de Ejecutables

- **Python**: `C:\Users\Nacho\.local\bin\python3.14.exe`
- **Git**: `C:\Program Files\Git\bin\git.exe`
- **GitHub CLI**: `C:\Program Files\GitHub CLI\gh.exe`

### Comandos útiles

```bash
# Añadir Git al PATH
$env:Path = "$env:Path;C:\Program Files\Git\bin"

# Añadir GitHub CLI al PATH
$env:Path = "$env:Path;C:\Program Files\GitHub CLI"

# Ejecutar script
python3.14.exe network_diagnostic.py
python3.14.exe network_diagnostic.py --help
python3.14.exe network_diagnostic.py --tests 1-16

# Ver ayuda
python3.14.exe network_diagnostic.py --version

# Git commands
git add -A
git commit -m "mensaje"
git push
gh release create v1.x.x --title "v1.x.x" --notes "notas"
gh release upload v1.x.x "network_diagnostic.py"
```

---

## Tests Implementados (16 tests)

| # | Test | Descripción |
|---|------|-------------|
| 1 | Conectividad Local | Loopback, gateway |
| 2 | Internet y DNS | Conectividad, resolución DNS |
| 2b | DNS Configurados | Lista servidores DNS del sistema |
| 3 | Puertos Críticos | 443 (HTTPS), 53 (DNS) |
| 4 | Latencia | Jitter, min/max/avg |
| 5 | WiFi | Intensidad de señal (Linux) |
| 6 | ISP | Información del ISP (ip-api.com) |
| 7 | Pérdida de Paquetes | 10 paquetes |
| 8 | Interfaz de Red | Estado, velocidad, duplex |
| 9 | Firewall | Estado del firewall |
| 10 | Traceroute | Ruta hacia YouTube/Yahoo |
| 11 | Velocidad | Download/Upload (Cloudflare) |
| 12 | DHCP | Información del lease |
| 13 | Bufferbloat (QoS) | Latencia bajo carga |
| 14 | MTU | MTU óptimo |
| 15 | DNS Alternativos | Comparación DNS configurados vs alternativos |
| 16 | Conexiones Simultáneas | TCP + HTTP concurrentes |

---

## Argumentos CLI

```bash
# Básico
python network_diagnostic.py              # Ejecutar todos los tests
python network_diagnostic.py -i           # Menú interactivo

# Tests específicos
python network_diagnostic.py --tests 1           # Solo test 1
python network_diagnostic.py --tests 1,2,3       # Tests 1, 2 y 3
python network_diagnostic.py --tests 1-5         # Tests 1 al 5
python network_diagnostic.py --tests internet    # Por nombre
python network_diagnostic.py --tests latency,simul-connections

# Omitir tests
python network_diagnostic.py --no-speed          # Sin test de velocidad
python network_diagnostic.py --no-isp            # Sin consulta ISP

# Output
python network_diagnostic.py -o resultados.txt   # Guardar en archivo
python network_diagnostic.py --format json       # Formato JSON
python network_diagnostic.py --parallel          # Tests en paralelo
python network_diagnostic.py --speed-size 10     # Velocidad con 10MB
python network_diagnostic.py -v                  # Verbose
python network_diagnostic.py --version           # Mostrar versión
python network_diagnostic.py --help              # Ver ayuda completa
```

---

## Comportamiento para Subir a GitHub

### Proceso Normal (Nuevas Features)

1. **Desarrollar y probar** la nueva funcionalidad
2. **Ejecutar pruebas** con `python network_diagnostic.py --tests <test>`
3. **Actualizar VERSION** en `network_diagnostic.py` (ej: v1.25.0)
4. **Actualizar archivos de documentación**:
   - `README.md` - Añadir "Novedades en vX.X.X" al inicio
   - `CHANGELOG.md` - Añadir entrada con fecha y cambios
   - `Diagnostico.md` - Actualizar tabla de estado si aplica
   - `TODO.md` - Marcar tareas completadas si aplica
5. **Commit y push**:
   ```bash
   git add -A
   git commit -m "v1.25.0: Descripción de cambios"
   git push
   ```
6. **Crear release**:
   ```bash
   gh release create v1.25.0 --title "v1.25.0" --notes "Notas del release"
   ```
7. **Subir script** al release:
   ```bash
   gh release upload v1.25.0 "network_diagnostic.py"
   ```

### Proceso para Fixes o Cambios Menores

1. **Desarrollar y probar** el fix
2. **Ejecutar pruebas** antes de subir
3. **Actualizar VERSION** a versión menor (ej: v1.24.6 si está en v1.24.5)
4. **Actualizar documentación** relevante (README, CHANGELOG, etc.)
5. **Probar todo** antes de commit
6. **Commit y push**
7. **Crear release** con el fix

---

## Reglas de Versionado

- **v1.x.0**: Nueva funcionalidad mayor
- **v1.24.x**: Fixes, mejoras menores, documentación
- **Ejemplo**: 
  - v1.24.5 → v1.24.6 (fix)
  - v1.24.5 → v1.25.0 (nueva feature)

---

## Notas Importantes

- **NO subir** el archivo `agents.md` a GitHub (ya está en .gitignore)
- **Siempre probar** antes de hacer commit
- **Mantener** CHANGELOG.md como fuente principal de historial
- **Usar** `--help` para ver todos los argumentos disponibles
- **NO BORRAR** este archivo sin preguntar primero al usuario

---

*Documento generado: 2026-04-24*
*v1.24.5*