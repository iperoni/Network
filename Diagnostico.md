# Diagnóstico y Troubleshooting - v1.14

## Objetivo

Agregar sugerencias de troubleshooting automatizadas basadas en los resultados de cada test.
Las sugerencias se imprimen junto con el resultado del test **y** se muestran al final del diagnóstico.

## Niveles de severidad

| Nivel | Símbolo | Descripción |
|-------|--------|-------------|
| CRÍTICO | 🔴 | Requiere acción inmediata |
| ADVERTENCIA | 🟡 | Problema potencial, investigar |
| INFO | ℹ️ | Dato útil, no urgente |

---

## Arquitectura

### Estructura de datos por test

Cada función de test retorna un dict `suggestions[]` con:
```python
{
    "level": "critical|warning|info",
    "test_id": "1",
    "test_name": "Conectividad Local",
    "problem": "APIPA detectada",
    "suggestion": "DHCP falló, la IP 169.254.x.x indica que no se obtuvo lease DHCP",
    "command": "ipconfig /release && ipconfig /renew",
}
```

### Ubicación en el código

Las sugerencias se generan:
1. En cada test: `analyze_test_N(results)` retorna lista de sugerencias
2. Se invocan desde `run_test_by_id()` y desde `run_diagnostics()` (secuencial)
3. Se colectan en `all_suggestions[]` global
4. Se imprimen al final del diagnóstico

---

## TEST 1 — Conectividad Local

**Datos:** `loopback_ok`, `gateway`, `gateway_ok`, `local_ip`

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| IP starts 169.254. | CRÍTICO | **APIPA** — DHCP falló | `ipconfig /release` → `ipconfig /renew` |
| gateway is None | CRÍTICO | Gateway no detectado | `ipconfig /all` → verificar DHCP del router |
| gateway != None AND gateway_ok == False | CRÍTICO | Gateway inaccesible | Ping manual al gateway; reiniciar router |
| gateway_ok == True AND latency > 10ms | WARNING | Gateway lento (>10ms) | Verificar congestión LAN; equipo sobrecargado |

### Parsing nuevo

Extraer IP local de la sección del adaptador activo de ipconfig:
```
Dirección IPv4. . . . . . . . . . . . . . : 192.168.100.203
```

### Estado: ✅ IMPLEMENTADO

---

## TEST 2 — Internet y DNS

**Datos:** `internet_ok`, `dns_ok`

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| internet == False AND dns == False | CRÍTICO | Sin conectividad total | Reiniciar módem/router; llamar ISP |
| internet == False AND dns == True | WARNING | ICMP bloqueado (normal en ISP) | Ninguna, web debería funcionar |
| internet == True AND dns == False | CRÍTICO | DNS no resuelve | Verificar DNS; probar `nslookup google.com 8.8.8.8` |
| DNS resolution > 2s | WARNING | DNS lento | Cambiar a 8.8.8.8 / 1.1.1.1 |

### Estado: ✅ IMPLEMENTADO

---

## TEST 2B — DNS Configurados

**Datos:** lista de DNS IPs, resultado de test_dns_verification()

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| Lista vacía | CRÍTICO | Sin servidores DNS | `netsh interface ip set dns "Ethernet" static 8.8.8.8` |
| Puerto 53 cerrado en algún DNS | CRÍTICO | DNS caído | Cambiar DNS primario a 8.8.8.8 |
| Solo 1 DNS | WARNING | Sin redundancia | `netsh interface ip add dns "Ethernet" 1.1.1.1 index=2` |
| DNS en 192.168.x.x | INFO | DNS del router | Considerar cambiar a 8.8.8.8 si es lento |

### Parsing nuevo

test_dns_verification() debe retornar True/False en vez de solo imprimir.

### Estado: ✅ IMPLEMENTADO

---

## TEST 3 — Puertos

**Datos:** resultado de test_port() para 443 (google.com) y 53 (8.8.8.8)

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| Puerto 443 cerrado | CRÍTICO | HTTPS bloqueado | Verificar firewall; `netsh advfirewall show all profiles` |
| Puerto 53 cerrado | CRÍTICO | DNS bloqueado | Verificar firewall o ISP bloquea puerto 53 |
| Puerto 443 abierto AND 53 cerrado | WARNING | DNS interceptado por VPN | Verificar si VPN está activa |

### Parsing nuevo

test_port() debe retornar True/False para colectar resultados.

### Estado: ✅ IMPLEMENTADO

---

## TEST 4 — Latencia

**Datos:** raw ping output — **se necesita parsing numérico**

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| avg > 500ms | CRÍTICO | Latencia crítica | Verificar línea; `tracert 8.8.8.8` |
| avg > 200ms | WARNING | Latencia alta | Llamar ISP; verificar plan |
| avg > 100ms | WARNING | Latencia elevada | Verificar QoS del router |
| jitter > 100ms | CRÍTICO | Inestabilidad severa | `tracert` para identificar hop |
| jitter > 50ms | WARNING | Inestabilidad moderada | Verificar cableado |
| min > 50ms | INFO | Latencia base alta | Normal en área rural/ISP lento |

### Parsing nuevo

Extraer `time=XXms` de cada línea de ping. Calcular min, max, avg, jitter = max - min.

Windows output example:
```
Tiempo = 5ms, Aproximación a 8.8.8.8 con 32 bytes de datos:
Respuesta desde 8.8.8.8: bytes=32 tiempo=5 TTL=117
Respuesta desde 8.8.8.8: bytes=32 tiempo=4 TTL=117
```

Linux output example:
```
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=4.50 ms
```

### Estado: PENDIENTE (requiere refactoring)

---

## TEST 5 — WiFi

**Datos:** SSID, Signal, Channel, Radio Type, BSSID, Tx/Rx Rate

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| Signal ≤ 20% | CRÍTICO | Señal muy débil | Sin conexión estable; mover router |
| Signal ≤ 50% | WARNING | Señal débil | Verificar obstrucciones, interferencia |
| Estado != Conectado | CRÍTICO | Sin conexión WiFi | Verificar que WiFi está activo |
| Canal 1/6/11 (2.4GHz overlap) | INFO | Canal puede estar saturado | Cambiar a canal 1, 6, 11 o 5GHz |
| Canal > 14 | INFO | Canal 5GHz | Mejor para menor interferencia |

### Parsing nuevo

Extraer valor numérico de Signal (ej: "85%") para comparar.

### Estado: PENDIENTE

---

## TEST 6 — ISP

**Datos:** IP pública, ISP, Organización, Ciudad, País

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| ISP == "" (vacío) | WARNING | ISP desconocido | Puede ser VPN o proxy |
| country != AR (esperado Argentina) | WARNING | País inesperado | Verificar VPN activa |
| city == "" | INFO | Geolocalización limitada | No requiere acción |

### Estado: PENDIENTE

---

## TEST 7 — Pérdida de Paquetes

**Datos:** enviados, recibidos, perdidos, porcentaje

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| pérdida > 20% | CRÍTICO | Pérdida severa | `tracert` para identificar hop problemático |
| pérdida 5-20% | WARNING | Pérdida moderada | Verificar router, línea ISP |
| pérdida 1-5% | INFO | Pérdida leve | Normal en horas pico |

### Estado: PENDIENTE

---

## TEST 8 — Interfaz de Red

**Datos:** Nombre, Descripción, Estado, MAC, Velocidad, MTU, Duplex

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| Estado != "Up" | CRÍTICO | Interfaz caído | `netsh interface set interface "Ethernet" admin=enabled` |
| Velocidad | INFO | Velocidad link | Comparar con plan contratado |
| MTU < 1500 | INFO | MTU reducido | Puede indicar fragmentación |

### Parsing nuevo

Extraer estado "Up" vs "Down" para comparar.

### Estado: PENDIENTE

---

## TEST 9 — Firewall

**Datos:** Estado por perfil (Dominio/Privado/Público), reglas activas

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| Todos OFF | WARNING | Firewall desactivado | Considerar activar firewall |
| Perfil específico OFF | INFO | Perfil desactivado | `netsh advfirewall set allprofiles state on` |

### Estado: PENDIENTE

---

## TEST 10 — Traceroute

**Datos:** lista de hops con IPs, hostnames, latencias

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| Hop > 15 | WARNING | Ruta larga | Normal para larga distancia |
| Hop con * * * | INFO | Timeout en hop | Puede ser normal (firewall en hop) |
| Aumento brusco de latencia entre hops | WARNING | Congestión en hop específico | Identificar proveedor |
| > 5 hops con * * * | WARNING | Múltiples timeout | Puede indicar ruta degradada |

### Parsing nuevo

Extraer latencia numérica por hop para detectar patrones.

### Estado: PENDIENTE

---

## TEST 11 — Velocidad

**Datos:** download Mbps, upload Mbps

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| Download < 1 Mbps | CRÍTICO | Velocidad muy baja | Verificar línea; llamar ISP |
| Download < 10 Mbps | WARNING | Velocidad baja | Congestión o plan bajo |
| Upload < 0.5 Mbps | WARNING | Upload muy bajo | Verificar QoS del ISP |
| Download muy bajo + Upload OK | INFO | Asimetría esperada | Normal en algunos planes |

### Estado: PENDIENTE

---

## TEST 12 — DHCP

**Datos:** servidor DHCP, leaseobtained, leasesexpires, IP estática vs dinámica

### Reglas

| Condición | Nivel | Problema | Sugerencia | Comando |
|----------|-------|---------|----------|---------|
| Lease expira pronto (< 1h) | WARNING | Lease por expirar | Renovar: `ipconfig /renew` |
| Sin servidor DHCP | INFO | IP estática o sin DHCP | Normal si es estática |
| Servidor DHCP en 192.168.x.x | INFO | DHCP del router | Normal en LAN doméstica |

### Parsing nuevo

Extraer fecha de lease para calcular tiempo restante.

### Estado: PENDIENTE

---

## Progreso

| Test | Estado | Complejidad |
|------|--------|-----------|
| 1 | ✅ IMPLEMENTADO | Baja |
| 2 | ✅ IMPLEMENTADO | Baja |
| 2B | ✅ IMPLEMENTADO | Baja |
| 3 | ✅ IMPLEMENTADO | Baja |
| 4 | ⏳ PENDIENTE | Alta (parsing numérico) |
| 5 | ⏳ PENDIENTE | Media |
| 6 | ⏳ PENDIENTE | Baja |
| 7 | ⏳ PENDIENTE | Baja |
| 8 | ⏳ PENDIENTE | Media |
| 9 | ⏳ PENDIENTE | Baja |
| 10 | ⏳ PENDIENTE | Alta (parsing hops) |
| 11 | ⏳ PENDIENTE | Baja |
| 12 | ⏳ PENDIENTE | Media |

---

## Implementación para Tests 1, 2, 2B, 3 (v1.14)

### Cambios realizados

1. **test_ping()** ahora retorna `(ok, latency)` en vez de solo `ok`
2. **test_port() y test_dns_verification()** ahora retornan True/False
3. Nuevas funciones `analyze_test_N(results)` que evalúan cada resultado
4. Sugerencias se colectan en `SUGGESTIONS[]` global
5. Se imprimen al final del diagnóstico si hay problemas

### Cómo funciona

- Cada test al ejecutarse llama a su función `analyze_test_N()`
- La función evalúa los resultados contra reglas y agrega sugerencias
- Al final, `print_all_suggestions()` imprime todas las sugerencias

### Ejemplo de output

Cuando hay problemas:
```
════════════════════════════════════════════════════════════
   SUGERENCIAS DE TROUBLESHOOTING
════════════════════════════════════════════════════════════
   🔴 [1] Conectividad Local: APIPA detectada — DHCP falló
      → La IP 169.254.x.x indica que no se obtuvo lease DHCP
      → ipconfig /release && ipconfig /renew

   🔴 [2] Internet y DNS: Sin conectividad
      → Reiniciar módem y router. Si persiste, contactar ISP
```

---

*Última actualización: 2026-04-23*

*v1.14: Tests 1, 2, 2B, 3 implementados con sugerencias de troubleshooting*