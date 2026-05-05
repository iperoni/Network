# Diagnóstico y Troubleshooting - v1.25.3

## Estado: ✅ Test 8 con múltiples interfaces

El Network Diagnostic Tool cuenta con 16 tests funcionales + MTU Path.

El Network Diagnostic Tool cuenta con 16 tests completamente funcionales y lista de mejoras pendientes para futuro.

---

## Historial de Versiones

| Versión | Cambios |
|---------|---------|
| v1.25.3 | Test 8 con múltiples interfaces |
| v1.25.2 | Test 8 y Test 12 fix para Windows |
| v1.25.1 | Test 12 DHCP mejorado con múltiples interfaces |
| v1.24.2 | README y Diagnostico actualizados |
| v1.24.1 | Help mejorado con ejemplos |
| v1.24.0 | Test 16: Conexiones Simultáneas |
| v1.23.1 | Fix DNS y doble título |
| v1.23.0 | Comparación DNS configurados vs alternativos |
| v1.22.0 | Test 15: DNS Alternativos |
| v1.21.0 | Tests 13 y 14 (Bufferbloat, MTU) |
| v1.20.0 | Test de Bufferbloat (QoS) |
| v1.19.9 | Latencia por hop en traceroute |
| v1.19.8 | Detección half-duplex |
| v1.19.7 | Detección latencia base alta |
| v1.19.6 | Detección DNS lento |

---

## TESTS IMPLEMENTADOS (16 tests)

### TEST 1 — Conectividad Local

**Descripción:** Verifica loopback, gateway y conectividad básica

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| IP starts 169.254. | CRÍTICO | APIPA — DHCP falló |
| gateway is None | CRÍTICO | Gateway no detectado |
| gateway_ok == False | CRÍTICO | Gateway inaccesible |
| gateway_latency > 10ms | WARNING | Gateway lento |

---

### TEST 2 — Internet y DNS

**Descripción:** Verifica conectividad a internet y resolución DNS

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| internet == False AND dns == False | CRÍTICO | Sin conectividad total |
| internet == False AND dns == True | WARNING | ICMP bloqueado |
| internet == True AND dns == False | CRÍTICO | DNS no resuelve |
| dns_time > 2000ms | WARNING | DNS lento (>2s) |

---

### TEST 2B — DNS Configurados

**Descripción:** Lista los servidores DNS configurados en el sistema

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Lista vacía | CRÍTICO | Sin servidores DNS |
| Puerto 53 cerrado | CRÍTICO | DNS caído |
| Solo 1 DNS | WARNING | Sin redundancia |

---

### TEST 3 — Puertos Críticos

**Descripción:** Verifica puertos esenciales (443 HTTPS, 53 DNS)

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Puerto 443 cerrado | CRÍTICO | HTTPS bloqueado |
| Puerto 53 cerrado | CRÍTICO | DNS bloqueado |

---

### TEST 4 — Latencia

**Descripción:** Mide latencia a múltiples servidores y calcula jitter

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| avg > 500ms | CRÍTICO | Latencia crítica |
| avg > 200ms | WARNING | Latencia alta |
| avg > 100ms | WARNING | Latencia elevada |
| jitter > 100ms | CRÍTICO | Inestabilidad severa |
| jitter > 50ms | WARNING | Inestabilidad moderada |
| min > 50ms | INFO | Latencia base elevada |

---

### TEST 5 — WiFi

**Descripción:** Mide intensidad de señal WiFi (solo Linux)

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Signal ≤ 20% | CRÍTICO | Señal muy débil |
| Signal ≤ 50% | WARNING | Señal débil |

---

### TEST 6 — ISP

**Descripción:** Consulta información del ISP via ip-api.com

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| ISP vacío | WARNING | ISP desconocido |
| city vacío | INFO | Geolocalización limitada |

---

### TEST 7 — Pérdida de Paquetes

**Descripción:** Envía 10 paquetes y mide pérdida

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| pérdida > 20% | CRÍTICO | Pérdida severa |
| pérdida 5-20% | WARNING | Pérdida moderada |
| pérdida > 0% | INFO | Pérdida leve |

---

### TEST 8 — Interfaz de Red

**Descripción:** Muestra detalles del adaptador de red

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Estado != "up" | CRÍTICO | Interfaz caído |
| Velocidad < 1 Gbps | INFO | Velocidad link baja |
| Duplex == "half" | WARNING | Half-duplex detectado |

---

### TEST 9 — Firewall

**Descripción:** Verifica estado del firewall de Windows/Linux

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Todos OFF | WARNING | Firewall desactivado |

---

### TEST 10 — Traceroute

**Descripción:** Rastrea ruta hacia YouTube y Yahoo

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| > 5 timeouts | WARNING | Ruta degradada |
| Aumento > 50ms/hop | WARNING | Congestión en hop |

---

### TEST 11 — Velocidad

**Descripción:** Mide velocidad de download/upload via Cloudflare

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Download < 1 Mbps | CRÍTICO | Velocidad muy baja |
| Download < 10 Mbps | WARNING | Velocidad baja |
| Upload < 0.5 Mbps | WARNING | Upload muy bajo |

---

### TEST 12 — DHCP

**Descripción:** Muestra información del lease DHCP

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| DHCP Deshabilitado | INFO | IP Estática |

---

### TEST 13 — Bufferbloat (QoS)

**Descripción:** Mide latencia bajo carga de download

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| bufferbloat > 30ms | CRÍTICO | Bufferbloat severo |
| bufferbloat > 15ms | WARNING | Bufferbloat moderado |
| bufferbloat < 5ms | INFO | QoS bueno |

---

### TEST 14 — MTU (con Path)

**Descripción:** Determina MTU óptimo probando tamaños de paquete + tracepath para ver ruta

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| MTU = 0 | CRÍTICO | Sin conectividad |
| MTU = 1500 | INFO | MTU óptimo - sin fragmentación |
| MTU > 1500 | WARNING | Puede causar fragmentación |
| MTU ≤ 1280 | WARNING | Muy bajo - posible VPN/tunnel |
| MTU 1281-1499 | INFO | MTU subóptimo |
| Sin ruta | WARNING | Ruta no disponible |

---

### TEST 15 — DNS Alternativos

**Descripción:** Compara DNS configurados vs alternativos (Cloudflare, Google, Quad9, OpenDNS)

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Alternativo >10ms más rápido | SUCCESS | Sugiere cambiar DNS |
| DNS configurados son óptimos | SUCCESS | No necesita cambios |
| Ningún DNS funciona | WARNING | Sin conectividad |

---

### TEST 16 — Conexiones Simultáneas

**Descripción:** Prueba múltiples conexiones TCP y HTTP concurrentes

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Todas las conexiones fallan | WARNING | Sin conectividad |
| <50% TCP exitosas | WARNING | Límites del ISP |
| HTTP <10 Mbps concurrente | WARNING | Límite conexiones simultáneas |
| Todo OK | INFO | Conexiones múltiples OK |

---

## MEJORAS PENDIENTES A FUTURO

### Alta Prioridad (Problemas Comunes de Conectividad)

| # | Nueva Prueba | Complejidad | Beneficio |
|---|--------------|-------------|-----------|
| A1 | MTR (hop-by-hop) | Media | Alto |
| A2 | TCP Traceroute | Media | Medio |
| ~~A3~~ | ~~Test MTU path~~ | ~~Baja~~ | ~~Alto~~ |

**A1. MTR (My Traceroute)**
- MTR combina traceroute + ping para mostrar pérdida por cada salto
- Detectar en qué salto ISP hay pérdida de paquetes
- Si primer salto OK pero hay loss en salto 3 → problema ISP
- Windows: requiere tools adicionales (WinMTR)
- Linux: `mtr -c 100 8.8.8.8`

**A2. TCP Traceroute**
- Si ICMP bloqueado pero TCP funciona
- Útil cuando traceroute tradicional falla
- Windows: `tcptraceroute` o Test-NetConnection con -TraceRoute
- Linux: `tcptraceroute -n 443 8.8.8.8`

~~**A3. Test de MTU Path** - ✅ IMPLEMENTADO en v1.25.0~~

**A4. ARP/Neighbor Table**
- Verificar tabla ARP (Linux) / Neighbor (Windows)
- Detectar problemas de conectividad local
- Detectar MAC duplicate, entradas stagnantes
- Windows: `netsh interface ipv4 show neighbors`
- Linux: `ip neighbor show`

---

### Media Prioridad

| # | Nueva Prueba | Complejidad | Beneficio |
|---|--------------|-------------|-----------|
| M1 | IPv6 | Baja | Media |
| M2 | Gateway secundario | Baja | Bajo |
| M3 | DNS reverso | Baja | Medio |
| M4 | TCP ports scan | Media | Medio |
| M5 | Interface errors | Baja | Medio |
| M6 | VPN detection | Baja | Bajo |

**M1. Test de IPv6**
- Verificar conectividad IPv6
- Detectar si ISP proporciona IPv6 o no
- Testing: `ping6 -n 1 ipv6.google.com`
- Dual-stack: verificar que ambos protocolos funcionan

**M2. Test de Gateway Secundario**
- Verificar gateway alternativo
- Si secundario funciona, problema está más allá
- Útil para redundant routing

**M3. DNS Reverso**
- Resolución inversa de IPs en ruta del traceroute
- Verificar queDNS reverso funciona
- `nslookup 8.8.8.8` o `dig -x 8.8.8.8`

**M4. TCP Ports Scan**
- Testear múltiples puertos comunes
- Puertos: 22 (SSH), 80 (HTTP), 443 (HTTPS), 3389 (RDP), 21 (FTP), 25 (SMTP)
- Windows: `Test-NetConnection -Port 443`
- Linux: `nc -zv -w 3 target port`

**M5. Interface Errors**
- Ver errores de interfaz (RX/TX errors, overruns, drops)
- Windows: `netsh interface show interface`
- Linux: `cat /proc/net/dev | grep eth0`
- High errors = problema físico (cable, NIC, switch)

**M6. VPN Detection**
- Identificar si hay VPN activa
- Verificar rutas inesperadas
- Detectar DNS leaks

---

### Baja Prioridad (Comparaciones Útiles)

| # | Nueva Prueba | Complejidad | Beneficio |
|---|--------------|-------------|-----------|
| B1 | Multi-server speed | Media | Medio |
| B2 | CDN comparison | Media | Medio |
| B3 | ISP comparison | Baja | Medio |
| B4 | Jitter real (RFC 3550) | Media | Medio |

**B1. Multi-Server Speed**
- Comparar velocidad hacia múltiples servers
- Servers: Cloudflare, nperf, Fast.com
- Detectar si un server específico está lento vs internet lento

**B2. CDN Comparison**
- Comparar Cloudflare vs Netflix vs Google
- Ver cómo-rinden diferentes CDNs
- Indicador de peering/optimización

**B3. ISP Comparison**
- Comparar velocidad real vs velocidad publicada
- Tests a diferentes horas del día
- Detectar congestion en peak hours

**B4. Jitter Real (RFC 3550)**
- Calcular jitter usando fórmula RFC 3550
- Más preciso para VoIP/gaming
- Diferente de packet-to-packet variation

---

### Tests Existentes (ya implementados)

| # | Test | Estado | Notas |
|---|------|--------|-------|
| 1 | Conectividad Local | ✅ Listo | Loopback, gateway |
| 2 | Internet y DNS | ✅ Listo | Conectividad básica |
| 2B | DNS Configurados | ✅ Listo | Lista DNS sistema |
| 3 | Puertos Críticos | ✅ Listo | Solo 443, 53 |
| 4 | Latencia | ✅ Listo | Jitter básico |
| 5 | WiFi | ✅ Listo | Solo Linux |
| 6 | ISP | ✅ Listo | Solo ip-api.com |
| 7 | Pérdida de Paquetes | ✅ Listo | 10 packets |
| 8 | Interfaz de Red | ✅ Listo | Estado/duplex |
| 9 | Firewall | ✅ Listo | Estado basic |
| 10 | Traceroute | ✅ Listo | Con detección |
| 11 | Velocidad | ✅ Listo | Solo Cloudflare |
| 12 | DHCP | ✅ Listo | Solo lectura |
| 13 | Bufferbloat | ✅ Listo | Latencia bajo carga |
| 14 | MTU | ✅ Listo | MTU óptimo + tracepath |
| 15 | DNS Alternativos | ✅ Listo | Comparación |
| 16 | Conexiones Simultáneas | ✅ Listo | TCP/HTTP |

---

## Argumentos CLI Disponibles

```bash
# Básico
python network_diagnostic.py              # Ejecutar todos los tests
python network_diagnostic.py -i           # Menú interactivo

# Tests específicos
python network_diagnostic.py --tests 1           # Solo test 1
python network_diagnostic.py --tests 1,2,3       # Tests 1, 2 y 3
python network_diagnostic.py --tests 1-5         # Tests 1 al 5
python network_diagnostic.py --tests internet    # Por nombre

# Omitir tests
python network_diagnostic.py --no-speed          # Sin test de velocidad
python network_diagnostic.py --no-isp            # Sin consulta ISP

# Output
python network_diagnostic.py -o resultados.txt   # Guardar en archivo
python network_diagnostic.py --format json       # Formato JSON

# Opciones
python network_diagnostic.py --parallel          # Tests en paralelo
python network_diagnostic.py --speed-size 10     # Velocidad con 10MB
python network_diagnostic.py -v                  # Verbose
python network_diagnostic.py --version           # Mostrar versión
python network_diagnostic.py --help              # Ver ayuda completa
```

---

*Última actualización: 2026-04-23*
*v1.24.2: Todas las mejoras implementadas (16 tests)*