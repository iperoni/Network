# Diagnóstico y Troubleshooting - v1.19.5

## Estado: ✅ COMPLETADO para tests 1-12

- v1.19.5: Comandos compatibles con Windows y Linux
- v1.19.4: Sugerencias y pie de página ahora se guardan en archivo
- v1.19.3: Archivo de texto idéntico al output de pantalla
- v1.19.2: Sugerencias ahora se guardan en archivo de texto
- v1.19.1: Fix parse_test_string() soporta "dns-configured"

**Todas las funciones analyze_test_N() para tests 1-12 están implementadas y funcionando.**

---

## Niveles de severidad

| Nivel | Símbolo | Descripción |
|-------|---------|-------------|
| CRÍTICO | 🔴 | Requiere acción inmediata |
| ADVERTENCIA | 🟡 | Problema potencial, investigar |
| INFO | ℹ️ | Dato útil, no urgente |

---

## TESTS IMPLEMENTADOS

### TEST 1 — Conectividad Local

**Datos:** `loopback_ok`, `gateway`, `gateway_ok`, `local_ip`, `gateway_latency`

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| IP starts 169.254. | CRÍTICO | APIPA — DHCP falló |
| gateway is None | CRÍTICO | Gateway no detectado |
| gateway_ok == False | CRÍTICO | Gateway inaccesible |
| gateway_latency > 10ms | WARNING | Gateway lento |

---

### TEST 2 — Internet y DNS

**Datos:** `internet_ok`, `dns_ok`

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| internet == False AND dns == False | CRÍTICO | Sin conectividad total |
| internet == False AND dns == True | WARNING | ICMP bloqueado |
| internet == True AND dns == False | CRÍTICO | DNS no resolver |

---

### TEST 2B — DNS Configurados

**Datos:** `dns_servers[]`, `dns_open{}`

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Lista vacía | CRÍTICO | Sin servidores DNS |
| Puerto 53 cerrado | CRÍTICO | DNS caído |
| Solo 1 DNS | WARNING | Sin redundancia |

---

### TEST 3 — Puertos

**Datos:** `port_443`, `port_53`

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Puerto 443 cerrado | CRÍTICO | HTTPS bloqueado |
| Puerto 53 cerrado | CRÍTICO | DNS bloqueado |

---

### TEST 4 — Latencia

**Datos:** `latency[]` con min, max, avg, jitter por servidor

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| avg > 500ms | CRÍTICO | Latencia crítica |
| avg > 200ms | WARNING | Latencia alta |
| avg > 100ms | WARNING | Latencia elevada |
| jitter > 100ms | CRÍTICO | Inestabilidad severa |
| jitter > 50ms | WARNING | Inestabilidad moderada |

---

### TEST 5 — WiFi

**Datos:** `conn_type`, `wifi_info{}` (Signal, Channel, etc.)

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Signal ≤ 20% | CRÍTICO | Señal muy débil |
| Signal ≤ 50% | WARNING | Señal débil |

---

### TEST 6 — ISP

**Datos:** `isp_info{}` (public_ip, isp, org, city, country)

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| ISP vacío | WARNING | ISP desconocido |
| city vacío | INFO | Geolocalización limitada |

---

### TEST 7 — Pérdida de Paquetes

**Datos:** `packets[]` con enviados, perdidos, pct

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| pérdida > 20% | CRÍTICO | Pérdida severa |
| pérdida 5-20% | WARNING | Pérdida moderada |
| pérdida > 0% | INFO | Pérdida leve |

---

### TEST 8 — Interfaz de Red

**Datos:** `interface_details{}` (Nombre, Descripción, Estado, MAC, Velocidad)

**Estado:** ⚠️ IMPLEMENTADO PARCIAL

**Reglas activas:** Ninguna (solo collecting de datos)

**Mejora sugerida:** Agregar análisis para interfaz caído, velocidad vs contratado

---

### TEST 9 — Firewall

**Datos:** `firewall_info{}` (Estado por perfil)

**Estado:** ⚠️ IMPLEMENTADO PARCIAL

**Reglas activas:** Ninguna

**Mejora sugerida:** Agregar análisis por perfil (Dominio/Privado/Público)

---

### TEST 10 — Traceroute

**Datos:** `routes{}` con hops por servidor

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| > 5 hops con timeout | WARNING | Ruta degradada |

**Mejora sugerida:** Análisis de latencia por hop, detección de aumento brusco

---

### TEST 11 — Velocidad

**Datos:** `download`, `upload` en Mbps

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| Download < 1 Mbps | CRÍTICO | Velocidad muy baja |
| Download < 10 Mbps | WARNING | Velocidad baja |
| Upload < 0.5 Mbps | WARNING | Upload muy bajo |

---

### TEST 12 — DHCP

**Datos:** `dhcp_info{}` (DHCP, Lease Obtained, Lease Expires)

**Estado:** ✅ IMPLEMENTADO

**Reglas activas:**
| Condición | Nivel | Problema |
|----------|-------|---------|
| DHCP Deshabilitado | INFO | IP Estática |

**Mejora sugerida:** Agregar análisis para lease próximo a expirar (< 1h)

---

## MEJORAS SUGERIDAS A FUTURO

### Prioridad Alta

| Test | Mejora | Beneficio |
|------|-------|-----------|
| 8 | Análisis de interfaz caído | Detectar adaptador deshabilitado |
| 8 | Velocidad vs plan contratado | Comparar con ancho de banda real |
| 9 | Análisis por perfil | Firewall por perfil (Dominio/Privado/Público) |
| 10 | Análisis latencia por hop | Detectar congestión en hop específico |
| 12 | Lease por expirar | Advertir cuando lease < 1h |

### Prioridad Media

| Test | Mejora | Beneficio |
|------|-------|-----------|
| 2 | DNS lento (> 2s) | Detectar DNS lento |
| 6 | Detección de VPN | Si país diferente al esperado |
| 4 | Latencia base alta (>50ms) | INFO en área rural |

### Prioridad Baja

| Test | Mejora | Beneficio |
|------|-------|-----------|
| 5 | Canal saturado (2.4GHz) | Sugerir cambio a 5GHz |
| 1 | Conexión duplex mismatch | Detectar half-duplex |

---

## PROGRESO

| Test | Estado | Complejidad |
|------|--------|-----------|
| 1 | ✅ COMPLETO | Baja |
| 2 | ✅ COMPLETO | Baja |
| 2B | ✅ COMPLETO | Baja |
| 3 | ✅ COMPLETO | Baja |
| 4 | ✅ COMPLETO | Alta |
| 5 | ✅ COMPLETO | Media |
| 6 | ✅ COMPLETO | Baja |
| 7 | ✅ COMPLETO | Baja |
| 8 | ⚠️ PARCIAL | Baja |
| 9 | ⚠️ PARCIAL | Baja |
| 10 | ✅ COMPLETO | Alta |
| 11 | ✅ COMPLETO | Baja |
| 12 | ✅ COMPLETO | Media |

---

## CÓMO AGREGAR NUEVAS REGLAS

1. Editar función `analyze_test_N(results)` en `network_diagnostic.py`
2. Usar `suggest(level, test_id, test_name, problem, suggestion, command)`
3. Niveles: "critical", "warning", "info"

```python
def analyze_test_N(results):
    """Test N: Descripción"""
    dato = results.get("dato", valor_default)
    
    if condicion:
        suggest(
            "critical",  # nivel
            "N",         # test_id
            "Nombre Test", # test_name
            "Problema",  # problem
            "Sugerencia", # suggestion
            "comando",   # command (opcional)
        )
```

---

*Última actualización: 2026-04-23*
*v1.19.3: Todos los tests implementados con sugerencias*