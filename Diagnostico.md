# Diagnóstico y Troubleshooting - v1.19.9

## Estado: ✅ TODAS LAS MEJORAS IMPLEMENTADAS

Todas las mejoras planificadas están implementadas en esta versión.

---

## MEJORAS IMPLEMENTADAS

| Test | Mejora | Versión | Estado |
|------|-------|--------|--------|
| 2 | DNS lento (>2s) | v1.19.6 | ✅ IMPLEMENTADO |
| 4 | Latencia base alta (>50ms) | v1.19.7 | ✅ IMPLEMENTADO |
| 8 | Duplex mismatch | v1.19.8 | ✅ IMPLEMENTADO |
| 10 | Latencia por hop | v1.19.9 | ✅ IMPLEMENTADO |

---

## TESTS IMPLEMENTADOS CON SUGERENCIAS

### TEST 1 — Conectividad Local

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| IP starts 169.254. | CRÍTICO | APIPA — DHCP falló |
| gateway is None | CRÍTICO | Gateway no detectado |
| gateway_ok == False | CRÍTICO | Gateway inaccesible |
| gateway_latency > 10ms | WARNING | Gateway lento |

---

### TEST 2 — Internet y DNS

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| internet == False AND dns == False | CRÍTICO | Sin conectividad total |
| internet == False AND dns == True | WARNING | ICMP bloqueado |
| internet == True AND dns == False | CRÍTICO | DNS no resuelve |
| dns_time > 2000ms | WARNING | DNS lento |

---

### TEST 2B — DNS Configurados

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Lista vacía | CRÍTICO | Sin servidores DNS |
| Puerto 53 cerrado | CRÍTICO | DNS caído |
| Solo 1 DNS | WARNING | Sin redundancia |

---

### TEST 3 — Puertos

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Puerto 443 cerrado | CRÍTICO | HTTPS bloqueado |
| Puerto 53 cerrado | CRÍTICO | DNS bloqueado |

---

### TEST 4 — Latencia

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

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Signal ≤ 20% | CRÍTICO | Señal muy débil |
| Signal ≤ 50% | WARNING | Señal débil |

---

### TEST 6 — ISP

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| ISP vacío | WARNING | ISP desconocido |
| city vacío | INFO | Geolocalización limitada |

---

### TEST 7 — Pérdida de Paquetes

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| pérdida > 20% | CRÍTICO | Pérdida severa |
| pérdida 5-20% | WARNING | Pérdida moderada |
| pérdida > 0% | INFO | Pérdida leve |

---

### TEST 8 — Interfaz de Red

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Estado != "up" | CRÍTICO | Interfaz caído |
| Velocidad < 1 Gbps | INFO | Velocidad link baja |
| Duplex == "half" | WARNING | Half-duplex detectado |

---

### TEST 9 — Firewall

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Todos OFF | WARNING | Firewall desactivado |

---

### TEST 10 — Traceroute

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| > 5 timeouts | WARNING | Ruta degradada |
| Aumento > 50ms/hop | WARNING | Congestión en hop |

---

### TEST 11 — Velocidad

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Download < 1 Mbps | CRÍTICO | Velocidad muy baja |
| Download < 10 Mbps | WARNING | Velocidad baja |
| Upload < 0.5 Mbps | WARNING | Upload muy bajo |

---

### TEST 12 — DHCP

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| DHCP Deshabilitado | INFO | IP Estática |

---

## MEJORAS PENDIENTES A FUTURO

### Alta Prioridad

| # | Nueva Prueba | Complejidad | Beneficio |
|---|--------------|-------------|-----------|
| 1 | Ancho de banda por servidor | Media | Alto |
| 2 | Bufferbloat (QoS) | Alta | Alto |

**1. Test de Ancho de Banda por Servidor**
- Medir velocidad por servidor individual (Netflix fast.com, Google QUIC, Cloudflare)
- Detectar si un servidor específico está lento vs Internet lento

**2. Test de Bufferbloat (QoS)**
- Medir latencia bajo carga de download
- Diferencia >50ms indica QoS mal configurado en router
- Necesita test de velocidad + ping simultáneo

---

### Media Prioridad

| # | Nueva Prueba | Complejidad | Beneficio |
|---|--------------|-------------|-----------|
| 3 | MTU/Fragmentación | Baja | Media |
| 4 | IPv6 | Baja | Media |
| 5 | DNS alternativos | Media | Medio |
| 6 | Conexiones simultáneas | Baja | Bajo |
| 7 | Gateway secundario | Baja | Bajo |

**3. Test de MTU/Fragmentación**
- Verificar MTU óptimo con `ping -f -l 1472`
- MTU > 1500 puede causar fragmentación

**4. Test de IPv6**
- Verificar conectividad IPv6
- Detectar si ISP no proporciona IPv6

**5. Test de DNS Alternativos**
- Probar múltiples DNS (1.1.1.1, 9.9.9.9, 8.8.8.8)
- Sugerir mejor DNS según rendimiento

**6. Test de Conexiones Simultáneas**
- Verificar múltiples conexiones TCP
- Detectar límites de conexiones del ISP

**7. Test de Gateway Secundario**
- Verificar gateway alternativo
- Si secundario funciona, problema está más allá

---

### Baja Prioridad

| # | Nueva Prueba | Complejidad | Beneficio |
|---|--------------|-------------|-----------|
| 8 | ARP/Neighbor table | Baja | Bajo |
| 9 | Jitter real (RFC 3550) | Media | Medio |

**8. Test de ARP/Neighbor Table**
- Verificar tabla ARP (Linux) / Neighbor (Windows)
- Detectar problemas de conectividad local

**9. Test de Jitter Real**
- Calcular jitter usando fórmula RFC 3550
- Precisión para VoIP/gaming

---

## NUEVAS PRUEBAS SUGERIDAS - DETALLE

### Test QoS/Bufferbloat

```python
# Pseudocódigo:
def test_bufferbloat():
    # 1. Medir latencia base (ping sin carga)
    base_latency = ping_latency()
    
    # 2. Iniciar download y medir latencia simultánea
    download_start()
    load_latency = ping_during_download()
    
    # 3. Calcular diferencia
    bloat = load_latency - base_latency
    
    # 4. Reglas
    if bloat > 50ms:
        suggest("warning", "Bufferbloat detectado (+{bloat}ms)")
```

### Test MTU

```python
def test_mtu():
    # Probar con don't fragment
    result = ping("-f -l 1472 8.8.8.8")
    if result.has("packets need to be fragmented"):
        suggest("warning", "MTU > 1500 puede causar problemas")
```

### Test IPv6

```python
def test_ipv6():
    ipv6_ok = ping6("ipv6.google.com")
    if not ipv6_ok:
        suggest("info", "IPv6 no disponible", "Considerar habilitar IPv6")
```

---

*Última actualización: 2026-04-23*
*v1.19.9: Todas las mejoras implementadas*