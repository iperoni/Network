# Diagnóstico y Troubleshooting - v1.24.2

## Estado: ✅ Todas las mejoras implementadas

El Network Diagnostic Tool cuenta con 16 tests completamente funcionales con sugerencias de troubleshooting automatizadas.

---

## Historial de Versiones

| Versión | Cambios |
|---------|---------|
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

### TEST 14 — MTU

**Descripción:** Determina MTU óptimo probando tamaños de paquete

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| MTU < 1500 | INFO | MTU suboptimal |
| MTU < 1280 | WARNING | MTU muy bajo |

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

### Media Prioridad

| # | Nueva Prueba | Complejidad | Beneficio |
|---|--------------|-------------|-----------|
| 1 | IPv6 | Baja | Media |
| 2 | Gateway secundario | Baja | Bajo |
| 3 | ARP/Neighbor table | Baja | Bajo |
| 4 | Jitter real (RFC 3550) | Media | Medio |

**1. Test de IPv6**
- Verificar conectividad IPv6
- Detectar si ISP no proporciona IPv6

**2. Test de Gateway Secundario**
- Verificar gateway alternativo
- Si secundario funciona, problema está más allá

**3. Test de ARP/Neighbor Table**
- Verificar tabla ARP (Linux) / Neighbor (Windows)
- Detectar problemas de conectividad local

**4. Test de Jitter Real**
- Calcular jitter usando fórmula RFC 3550
- Precisión para VoIP/gaming

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