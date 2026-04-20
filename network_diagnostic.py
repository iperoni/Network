#!/usr/bin/env python3
"""
Network Diagnostic Tool (v1.0)
Diagnóstico completo de conectividad de red mejorado para Windows/Linux

Autor: Xabier Pereira - Modificado por Ignacio Peroni (v0.5)
"""

import socket
import subprocess
import re
import platform
import time
import sys
import os
import os
from datetime import datetime

if platform.system().lower() == "windows":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        subprocess.run("chcp 65001", shell=True, capture_output=True)
    except Exception:
        pass


def print_header(title):
    """Imprime cabecera de sección"""
    print("\n" + "=" * 60)
    print(f"   {title}")
    print("=" * 60)


def get_real_ip():
    """Obtiene la IP real de la interfaz activa (evita 127.0.1.1 en Linux)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No requiere conexión real, solo detecta por dónde saldría el tráfico
        s.connect(("8.8.8.8", 1))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = "No detectada"
    finally:
        s.close()
    return ip


def run_command(command):
    """Ejecuta comando y devuelve output"""
    try:
        is_win = platform.system().lower() == "windows"
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            timeout=10,
        )
        return (
            result.stdout.decode("cp437", errors="replace")
            if is_win
            else result.stdout.decode("utf-8", errors="replace")
        )
    except Exception:
        return ""


def test_ping(host, name=""):
    """Test ping a un host"""
    is_win = platform.system().lower() == "windows"
    param = "-n" if is_win else "-c"
    command = f"ping {param} 4 {host}"

    print(f"\n🔍 Testing {name or host}...")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            timeout=10,
        )
        output = (
            result.stdout.decode("cp437", errors="replace")
            if is_win
            else result.stdout.decode("utf-8", errors="replace")
        )
        if result.returncode == 0:
            print(f"   ✅ {name or host} - RESPONDE")
            lines = [
                l
                for l in output.split("\n")
                if "time=" in l.lower() or "tiempo=" in l.lower()
            ]
            if lines:
                print(f"      {lines[-1].strip()}")
            return True
        else:
            print(f"   ❌ {name or host} - NO RESPONDE")
            return False
    except:
        return False


def test_dns(domain):
    """Test resolución DNS"""
    print(f"\n🔍 Resolviendo DNS: {domain}")
    try:
        ip = socket.gethostbyname(domain)
        print(f"   ✅ {domain} → {ip}")
        return True, ip
    except:
        print(f"   ❌ No se pudo resolver {domain}")
        return False, None


def test_port(host, port, service_name=""):
    """Test si un puerto está abierto"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"   ✅ Puerto {port} ({service_name}) ABIERTO")
            return True
        else:
            print(f"   ❌ Puerto {port} ({service_name}) CERRADO/BLOQUEADO")
            return False
    except:
        return False
    finally:
        sock.close()


def get_connection_type():
    """Detectar tipo de conexión: WiFi o Ethernet"""
    is_windows = platform.system().lower() == "windows"

    if is_windows:
        output = run_command("netsh wlan show interfaces")
        if output and "el servicio" not in output.lower():
            if "conectado" in output.lower() and "estado" in output.lower():
                return "wifi"
            if any(
                keyword in output.lower()
                for keyword in ["ssid", "dirección", "channel", "señal"]
            ):
                return "wifi"
        return "ethernet"
    else:
        output = run_command("ip link show")
        if output:
            for line in output.split("\n"):
                if (
                    "wlo" in line.lower()
                    or "wlan" in line.lower()
                    or "wlp" in line.lower()
                    or "wifi" in line.lower()
                ):
                    if "state UP" in line or "state UNKNOWN" in line:
                        return "wifi"
        return "ethernet"


def test_wifi_signal():
    """Test de señal WiFi - Windows/Linux"""
    is_windows = platform.system().lower() == "windows"
    wifi_info = {}

    if is_windows:
        output = run_command("netsh wlan show interfaces")
        if not output:
            return None
        if "el servicio" in output.lower() or "no se" in output.lower():
            wifi_info["Estado"] = "Servicio WiFi no disponible"
            return wifi_info
        if "no hay" in output.lower() or "no existe" in output.lower():
            wifi_info["Estado"] = "No hay adaptador WiFi"
            return wifi_info

        for line in output.split("\n"):
            line_lower = line.lower().strip()
            if "ssid" in line_lower and ":" in line:
                wifi_info["SSID"] = line.split(":", 1)[1].strip()
            elif "se" in line_lower and "%" in line:
                try:
                    wifi_info["Signal"] = line.split(":", 1)[1].strip()
                except:
                    pass
            elif "canal" in line_lower or "channel" in line_lower:
                if ":" in line:
                    wifi_info["Channel"] = line.split(":", 1)[1].strip()
            elif "tipo de radio" in line_lower or "radio type" in line_lower:
                if ":" in line:
                    wifi_info["Radio Type"] = line.split(":", 1)[1].strip()
            elif "bssid" in line_lower:
                if ":" in line:
                    wifi_info["BSSID"] = line.split(":", 1)[1].strip()
            elif "estado" in line_lower or "state" in line_lower:
                if ":" in line:
                    wifi_info["Estado"] = line.split(":", 1)[1].strip()
    else:
        output = run_command("ip link show | grep -E '^[0-9]+: wl'")
        interface = ""
        if output:
            parts = output.split(":")
            if len(parts) > 1:
                interface = parts[1].strip().split()[0]

        if interface:
            output = run_command(f"iw dev {interface} link")
            if output:
                for line in output.split("\n"):
                    line_lower = line.lower().strip()
                    if "ssid" in line_lower:
                        wifi_info["SSID"] = line.strip()
                    elif "signal" in line_lower and "dBm" in line:
                        wifi_info["Signal"] = line.strip().split(":")[-1].strip()
                    elif "freq" in line_lower:
                        try:
                            freq = line.split(":")[-1].strip().split()[0]
                            channel = int((int(freq) - 2412) / 5) + 1
                            wifi_info["Channel"] = f"{channel} ({freq} MHz)"
                        except:
                            pass
                    elif "tx bitrate" in line_lower:
                        wifi_info["Tx Rate"] = line.split(":")[-1].strip()
                    elif "rx bitrate" in line_lower:
                        wifi_info["Rx Rate"] = line.split(":")[-1].strip()

    return wifi_info if wifi_info else None


def get_public_ip_and_isp():
    """Obtiene IP pública y datos del ISP"""
    import json

    try:
        result = subprocess.run(
            ["curl", "-s", "http://ip-api.com/json"], capture_output=True, timeout=10
        )
        data = json.loads(result.stdout.decode())
        return {
            "public_ip": data.get("query"),
            "isp": data.get("isp"),
            "org": data.get("org"),
            "city": data.get("city"),
            "country": data.get("country"),
        }
    except:
        try:
            result = subprocess.run(
                ["curl", "-s", "ifconfig.me"], capture_output=True, timeout=10
            )
            return {"public_ip": result.stdout.decode().strip()}
        except:
            return None


def test_packet_loss(host, count=10):
    """Test de pérdida de paquetes"""
    is_windows = platform.system().lower() == "windows"
    param = "-n" if is_windows else "-c"

    result = subprocess.run(
        f"ping {param} {count} {host}", shell=True, capture_output=True, timeout=30
    )
    output = (
        result.stdout.decode("cp437", errors="replace")
        if is_windows
        else result.stdout.decode("utf-8", errors="replace")
    )

    packet_info = {}

    if is_windows:
        for line in output.split("\n"):
            line_lower = line.lower()
            if "paquetes" in line_lower and "enviados" in line_lower:
                try:
                    parts = line.split(",")
                    for part in parts:
                        if "enviados" in part.lower():
                            packet_info["enviados"] = part.split("=")[1].strip()
                        elif "recibidos" in part.lower():
                            packet_info["recibidos"] = part.split("=")[1].strip()
                        elif "perdidos" in part.lower():
                            packet_info["perdidos"] = part.split("=")[1].strip()
                    if "perdidos" in packet_info and "enviados" in packet_info:
                        try:
                            p_perdidos = int(packet_info["perdidos"])
                            p_enviados = int(packet_info["enviados"])
                            if p_enviados > 0:
                                pct = (p_perdidos / p_enviados) * 100
                                packet_info["% perda"] = f"{pct:.0f}%"
                        except:
                            pass
                except:
                    pass
    else:
        for line in output.split("\n"):
            line_lower = line.lower()
            if "packets transmitted" in line_lower:
                try:
                    parts = line.split(",")
                    for part in parts:
                        part = part.strip()
                        if "transmitted" in part:
                            packet_info["enviados"] = part.split()[0]
                        elif "received" in part:
                            packet_info["recibidos"] = part.split()[0]
                        elif "%" in part and "loss" in part:
                            packet_info["% perda"] = part.split()[0]
                except:
                    pass

    return packet_info


def get_configured_dns():
    """Obtiene servidores DNS configurados"""
    is_windows = platform.system().lower() == "windows"
    dns_servers = []

    if is_windows:
        output = run_command("netsh interface ipv4 show dns")
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        matches = re.findall(ip_pattern, output)
        for ip in matches:
            if ip not in dns_servers:
                dns_servers.append(ip)
    else:
        output = run_command("cat /etc/resolv.conf")
        for line in output.split("\n"):
            if line.strip().startswith("nameserver"):
                parts = line.split()
                if len(parts) > 1:
                    dns_servers.append(parts[1])

    return dns_servers


def test_dns_verification(dns_server):
    """Prueba un servidor DNS específico"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((dns_server, 53))
        sock.close()
        if result == 0:
            print(f"         ✅ {dns_server}:53 (Puerto DNS abierto)")
        else:
            print(f"         ⚠️ {dns_server}:53 (Puerto DNS cerrado)")
    except Exception as e:
        print(f"         ❌ {dns_server}:53 (Error: {str(e)[:30]})")


def get_network_interface_details():
    """Obtiene detalles del interfaz de red"""
    is_windows = platform.system().lower() == "windows"
    details = {}

    if is_windows:
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object Name, InterfaceDescription, Status, MacAddress, LinkSpeed | ConvertTo-Json",
                ],
                capture_output=True,
                timeout=15,
            )
            output = result.stdout.decode("utf-8", errors="replace")
            if output.strip().startswith("["):
                import json

                data = json.loads(output)
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
            elif output.strip().startswith("{"):
                import json

                data = json.loads(output)
            else:
                return details

            if data:
                details["Nombre"] = data.get("Name", "N/A")
                details["Descripcion"] = data.get("InterfaceDescription", "N/A")
                details["Estado"] = data.get("Status", "N/A")
                details["MAC"] = data.get("MacAddress", "N/A")
                details["Velocidad"] = data.get("LinkSpeed", "N/A")
        except Exception as e:
            pass
    else:
        output = run_command("ip link show")
        for line in output.split("\n"):
            if "state UP" in line or "state UNKNOWN" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    details["Interfaz"] = parts[1].strip().split()[0]
                    for part in parts[1:]:
                        if "metric" not in part.lower():
                            details["Estado"] = "UP"
                if "link/ether" in line:
                    mac = line.split("link/ether")[1].strip().split()[0]
                    details["MAC"] = mac
                if "mtu" in line:
                    mtu = line.split("mtu")[1].strip().split()[0]
                    details["MTU"] = mtu

        try:
            output = run_command("ethtool " + details.get("Interfaz", "eth0"))
            for line in output.split("\n"):
                line_lower = line.lower()
                if "speed" in line_lower:
                    details["Velocidad"] = line.split(":")[-1].strip()
                elif "duplex" in line_lower:
                    details["Duplex"] = line.split(":")[-1].strip()
        except:
            pass

    return details


def get_firewall_status():
    """Obtiene estado del firewall"""
    is_windows = platform.system().lower() == "windows"
    firewall_info = {}

    if is_windows:
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                "Get-NetFirewallProfile | Select-Object Name, Enabled | ConvertTo-Json",
            ],
            capture_output=True,
            timeout=15,
        )
        output = result.stdout.decode("utf-8", errors="replace")

        import json

        try:
            data = json.loads(output)
            if isinstance(data, list):
                for profile in data:
                    name = profile.get("Name", "")
                    enabled = profile.get("Enabled", False)
                    if name == "Domain":
                        firewall_info["Dominio"] = "ON" if enabled else "OFF"
                    elif name == "Private":
                        firewall_info["Privado"] = "ON" if enabled else "OFF"
                    elif name == "Public":
                        firewall_info["Publico"] = "ON" if enabled else "OFF"
            elif isinstance(data, dict):
                name = data.get("Name", "")
                enabled = data.get("Enabled", False)
                firewall_info[name] = "ON" if enabled else "OFF"
        except:
            pass

        if not firewall_info:
            output = run_command("netsh advfirewall show allprofiles")
            if "Configuración de Perfil de dominio" in output:
                firewall_info["Dominio"] = "ON"
            if "Configuración de Perfil privado" in output:
                firewall_info["Privado"] = "ON"
            if "Configuración de Perfil público" in output:
                firewall_info["Publico"] = "ON"

        output = run_command("netsh advfirewall show rule name=all")
        reglas_count = len(
            [l for l in output.split("\n") if "Regla name" in l or "Rule name" in l]
        )
        firewall_info["Reglas activas"] = str(reglas_count)
    else:
        output = run_command(
            "sudo ufw status verbose 2>/dev/null || echo 'UFW not available'"
        )
        for line in output.split("\n"):
            line_lower = line.lower()
            if "status" in line_lower:
                if "active" in line_lower:
                    firewall_info["UFW"] = "Active"
                elif "inactive" in line_lower:
                    firewall_info["UFW"] = "Inactive"

        output = run_command(
            "sudo iptables -L -n 2>/dev/null || echo 'iptables not available'"
        )
        reglas_count = len(
            [l for l in output.split("\n") if l.strip() and "Chain" not in l]
        )
        firewall_info["iptables rules"] = str(reglas_count)

    return firewall_info


def main():
    is_windows = platform.system().lower() == "windows"

    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 20 + "DIAGNÓSTICO DE RED" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ========== INFORMACIÓN LOCAL ==========
    print_header("INFORMACIÓN LOCAL")

    print(f"📌 Hostname: {socket.gethostname()}")
    print(f"📌 IP Local Detectada: {get_real_ip()}")

    if is_windows:
        print("\n📋 Resumen Adaptadores (Windows):")
        output = run_command("ipconfig")
        for line in output.split("\n"):
            if any(
                k in line.lower() for k in ["ipv4", "puerta", "gateway", "adaptador"]
            ):
                if ":" in line:
                    print(f"   {line.strip()}")
    else:
        print("\n📋 Resumen Adaptadores (Linux):")
        output = run_command("ip -4 addr show scope global | grep inet")
        if output:
            for line in output.split("\n"):
                if line:
                    print(f"   {line.strip()}")

    # ========== TEST CONECTIVIDAD LOCAL ==========
    print_header("TEST 1: CONECTIVIDAD LOCAL")
    loopback_ok = test_ping("127.0.0.1", "Loopback (Interno)")

    gateway = None
    if is_windows:
        output = run_command("ipconfig")
        for line in output.split("\n"):
            if "puerta de enlace" in line.lower() or "default gateway" in line.lower():
                parts = line.split(":")
                if len(parts) > 1 and parts[1].strip():
                    gateway = parts[1].strip()
                    break
    else:
        output = run_command("ip route | grep default")
        if output:
            parts = output.split()
            if len(parts) > 2:
                gateway = parts[2]

    gateway_ok = False
    if gateway:
        print(f"\n📍 Gateway detectado: {gateway}")
        gateway_ok = test_ping(gateway, f"Gateway ({gateway})")
    else:
        print("\n⚠️ No se detectó Gateway automáticamente.")

    # ========== TEST INTERNET Y DNS ==========
    print_header("TEST 2: INTERNET Y DNS")

    internet_ok = test_ping("8.8.8.8", "Google DNS")
    dns_ok, _ = test_dns("google.com")

    # ========== DNS CONFIGURADOS ==========
    print_header("TEST 2B: SERVIDORES DNS CONFIGURADOS")
    dns_servers = get_configured_dns()
    if dns_servers:
        print(f"   📋 Servidores DNS configurados ({len(dns_servers)}):")
        for dns in dns_servers:
            print(f"      - {dns}")
            test_dns_verification(dns)
    else:
        print("   ⚠️ No se detectaron servidores DNS configurados")

    # ========== TEST PUERTOS ==========
    print_header("TEST 3: PUERTOS CRÍTICOS")
    test_port("google.com", 443, "HTTPS")
    test_port("8.8.8.8", 53, "DNS")

    # ========== LATENCIA DETALLADA ==========
    print_header("TEST 4: ESTADÍSTICAS DE LATENCIA")
    targets = [("8.8.8.8", "Google"), ("1.1.1.1", "Cloudflare")]
    for ip, name in targets:
        print(f"\n📡 {name}:")
        param = "-n" if is_windows else "-c"
        output = run_command(f"ping {param} 5 {ip}")
        for line in output.split("\n"):
            if any(k in line.lower() for k in ["average", "media", "min", "max"]):
                print(f"   {line.strip()}")

    # ========== SEÑAL WIFI ==========
    print_header("TEST 5: SEÑAL WI-FI")
    conn_type = get_connection_type()

    is_windows = platform.system().lower() == "windows"
    wifi_info = None

    if is_windows:
        wifi_info = test_wifi_signal()
    else:
        if conn_type == "wifi":
            wifi_info = test_wifi_signal()

    if wifi_info:
        is_connected_wifi = any(
            key in wifi_info for key in ["SSID", "Signal", "Channel"]
        )
        has_wifiHardware = wifi_info.get("Estado", "") not in [
            "No hay adaptador WiFi",
            "",
        ]

        if is_connected_wifi:
            print(f"\n📶 Conexión WiFi activa:")
            for key, value in wifi_info.items():
                print(f"   {key}: {value}")
        elif "Estado" in wifi_info and "no disponible" in wifi_info["Estado"].lower():
            print(f"   ⚠️ {wifi_info.get('Estado', 'Servicio WiFi no disponible')}")
            print(f"   💡 Tipo de conexión: ETHERNET")
        else:
            print(f"   ℹ️ Adaptador WiFi detectado pero Sin conexión activa")
            print(f"   💡 Tipo de conexión actual: ETHERNET")
    else:
        print(f"   ℹ️ Sin adaptador WiFi detectado")
        print(f"   💡 Tipo de conexión: ETHERNET")

    # ========== INFO ISP ==========
    print_header("TEST 6: INFORMACIÓN DEL ISP")
    print("   🌐 Consultando información del ISP...")
    isp_info = get_public_ip_and_isp()
    if isp_info:
        print(f"   IP Pública: {isp_info.get('public_ip', 'N/A')}")
        print(f"   ISP: {isp_info.get('isp', 'N/A')}")
        print(f"   Organización: {isp_info.get('org', 'N/A')}")
        print(
            f"   Ubicación: {isp_info.get('city', 'N/A')}, {isp_info.get('country', 'N/A')}"
        )
    else:
        print("   ⚠️ No se pudo obtener información del ISP")

    # ========== PÉRDIDA DE PAQUETES ==========
    print_header("TEST 7: PÉRDIDA DE PAQUETES")
    hosts = [("8.8.8.8", "Google DNS"), ("1.1.1.1", "Cloudflare")]
    packet_loss_results = []

    for host, name in hosts:
        print(f"\n   📊 Testeando {name} ({host})...")
        packet_info = test_packet_loss(host, count=10)
        if packet_info:
            if "enviados" in packet_info:
                print(f"   {name}:")
                print(f"      Enviados: {packet_info.get('enviados', 'N/A')}")
                print(f"      Recibidos: {packet_info.get('recibidos', 'N/A')}")
                print(f"      Perdidos: {packet_info.get('perdidos', 'N/A')}")
                print(f"      Porcentaje: {packet_info.get('% perda', 'N/A')}")
            else:
                print(f"   {name}: {packet_info.get('% perda', 'N/A')}")
            packet_loss_results.append((name, packet_info))
        else:
            print(f"   ⚠️ No se pudo obtener información de {name}")
            packet_loss_results.append((name, None))

    # ========== DETALLES INTERFAZ DE RED ==========
    print_header("TEST 8: DETALLES DEL INTERFAZ DE RED")
    interface_details = get_network_interface_details()
    if interface_details:
        print(f"   📡 Información del interfaz de red:")
        for key, value in interface_details.items():
            print(f"      {key}: {value}")
    else:
        print("   ⚠️ No se pudo obtener información del interfaz")

    # ========== ESTADO DEL FIREWALL ==========
    print_header("TEST 9: ESTADO DEL FIREWALL")
    firewall_info = get_firewall_status()
    if firewall_info:
        print(f"   🔥 Estado del firewall:")
        for key, value in firewall_info.items():
            print(f"      {key}: {value}")
    else:
        print("   ⚠️ No se pudo obtener información del firewall")

    # ========== RESUMEN ==========
    print_header("RESULTADO FINAL")
    puntos = 0
    if gateway:
        puntos += 1
    if internet_ok:
        puntos += 1
    if dns_ok:
        puntos += 1

    status = "🔴 SIN CONEXIÓN"
    if puntos == 3:
        status = "🟢 TODO OK"
    elif puntos == 2:
        status = "🟡 PROBLEMA PARCIAL (Revisar DNS)"

    print(f"Estado General: {status}")
    print(f"Puntuación: {puntos}/3 tests principales superados.")

    # ========== COMANDOS ÚTILES ==========
    print_header("COMANDOS ÚTILES PARA TROUBLESHOOTING")

    if is_windows:
        print("""
💻 Windows:
  ipconfig /all          - Ver configuración completa
  ipconfig /flushdns     - Limpiar caché DNS
  netsh winsock reset    - Resetear el catálogo de red
  ping 8.8.8.8           - Probar internet básico
  tracert google.com     - Rastrear ruta al servidor
        """)
    else:
        print("""
🐧 Linux:
  ip addr show           - Ver interfaces y IPs
  ip route show          - Ver tabla de rutas
  nmcli dev status       - Estado de dispositivos (NetworkManager)
  ping -c 4 8.8.8.8      - Probar internet
  traceroute google.com  - Rastrear ruta
        """)

    # ========== GUARDAR RESULTADOS ==========
    hostname = socket.gethostname()
    local_ip = get_real_ip()
    fecha = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"{fecha}-{hostname}-{local_ip}.txt"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(script_dir, nombre_archivo)

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write("╔" + "═" * 58 + "╗\n")
        f.write("║" + " " * 20 + "DIAGNÓSTICO DE RED" + " " * 20 + "║\n")
        f.write("╚" + "═" * 58 + "╝\n")
        f.write(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # INFORMACIÓN LOCAL
        f.write("\n" + "=" * 60 + "\n")
        f.write("   INFORMACIÓN LOCAL\n")
        f.write("=" * 60 + "\n")
        f.write(f"Hostname: {hostname}\n")
        f.write(f"IP Local: {local_ip}\n")
        f.write(f"Gateway: {gateway}\n")

        if is_windows:
            output = run_command("ipconfig")
            f.write("\nAdaptadores de red:\n")
            for line in output.split("\n"):
                if any(
                    k in line.lower()
                    for k in ["ipv4", "puerta", "gateway", "adaptador"]
                ):
                    if ":" in line:
                        f.write(f"   {line.strip()}\n")

        # TEST 1: CONECTIVIDAD LOCAL
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 1: CONECTIVIDAD LOCAL\n")
        f.write("=" * 60 + "\n")
        f.write(f"Loopback (127.0.0.1): {'OK' if loopback_ok else 'FALLO'}\n")
        f.write(f"Gateway ({gateway}): {'OK' if gateway_ok else 'FALLO'}\n")

        # TEST 2: INTERNET Y DNS
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 2: INTERNET Y DNS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Internet (8.8.8.8): {'OK' if internet_ok else 'FALLO'}\n")
        f.write(f"DNS (google.com): {'OK' if dns_ok else 'FALLO'}\n")

        # TEST 2B: DNS CONFIGURADOS
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 2B: SERVIDORES DNS CONFIGURADOS\n")
        f.write("=" * 60 + "\n")
        if dns_servers:
            f.write(f"Servidores DNS ({len(dns_servers)}):\n")
            for dns in dns_servers:
                f.write(f"   - {dns}\n")
        else:
            f.write("No se detectaron servidores DNS configurados\n")

        # TEST 3: PUERTOS
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 3: PUERTOS CRÍTICOS\n")
        f.write("=" * 60 + "\n")

        def test_port_check(host, port, service_name):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            try:
                result = sock.connect_ex((host, port))
                sock.close()
                return "ABIERTO" if result == 0 else "CERRADO"
            except:
                sock.close()
                return "ERROR"

        https_status = test_port_check("google.com", 443, "HTTPS")
        dns_status = test_port_check("8.8.8.8", 53, "DNS")
        f.write(f"Puerto 443 (HTTPS): {https_status}\n")
        f.write(f"Puerto 53 (DNS): {dns_status}\n")

        # TEST 4: LATENCIA
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 4: ESTADÍSTICAS DE LATENCIA\n")
        f.write("=" * 60 + "\n")

        for ip, name in [("8.8.8.8", "Google"), ("1.1.1.1", "Cloudflare")]:
            param = "-n" if is_windows else "-c"
            output = run_command(f"ping {param} 5 {ip}")
            for line in output.split("\n"):
                if any(k in line.lower() for k in ["average", "media", "min", "max"]):
                    f.write(f"{name}: {line.strip()}\n")

        # TEST 5: SEÑAL WIFI
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 5: SEÑAL WI-FI\n")
        f.write("=" * 60 + "\n")
        f.write(f"Tipo de conexión: {conn_type}\n")
        if conn_type == "wifi" and wifi_info:
            for key, value in wifi_info.items():
                f.write(f"{key}: {value}\n")
        elif conn_type != "wifi":
            f.write(f"Conexión {conn_type} - Test WiFi no aplicable\n")

        # TEST 6: ISP INFO
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 6: INFORMACIÓN DEL ISP\n")
        f.write("=" * 60 + "\n")
        if isp_info:
            f.write(f"IP Pública: {isp_info.get('public_ip', 'N/A')}\n")
            f.write(f"ISP: {isp_info.get('isp', 'N/A')}\n")
            f.write(f"Organización: {isp_info.get('org', 'N/A')}\n")
            f.write(
                f"Ubicación: {isp_info.get('city', 'N/A')}, {isp_info.get('country', 'N/A')}\n"
            )
        else:
            f.write("No se pudo obtener información del ISP\n")

        # TEST 7: PÉRDIDA DE PAQUETES
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 7: PÉRDIDA DE PAQUETES\n")
        f.write("=" * 60 + "\n")
        for name, packet_info in packet_loss_results:
            if packet_info:
                f.write(f"{name}:\n")
                f.write(f"   Enviados: {packet_info.get('enviados', 'N/A')}\n")
                f.write(f"   Recibidos: {packet_info.get('recibidos', 'N/A')}\n")
                f.write(f"   Perdidos: {packet_info.get('perdidos', 'N/A')}\n")
                f.write(f"   Porcentaje: {packet_info.get('% perda', 'N/A')}\n")
            else:
                f.write(f"{name}: No disponible\n")

        # TEST 8: DETALLES INTERFAZ DE RED
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 8: DETALLES DEL INTERFAZ DE RED\n")
        f.write("=" * 60 + "\n")
        if interface_details:
            for key, value in interface_details.items():
                f.write(f"{key}: {value}\n")
        else:
            f.write("No se pudo obtener información del interfaz\n")

        # TEST 9: ESTADO DEL FIREWALL
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 9: ESTADO DEL FIREWALL\n")
        f.write("=" * 60 + "\n")
        if firewall_info:
            for key, value in firewall_info.items():
                f.write(f"{key}: {value}\n")
        else:
            f.write("No se pudo obtener información del firewall\n")

        # RESULTADO FINAL
        f.write("\n" + "=" * 60 + "\n")
        f.write("   RESULTADO FINAL\n")
        f.write("=" * 60 + "\n")
        f.write(f"Estado: {status}\n")
        f.write(f"Puntuación: {puntos}/3\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write(f"Autor: Ignacio Peroni\n")
        f.write(f"GitHub: github.com/iperoni\n")
        f.write("=" * 60 + "\n")

    print(f"\n💾 Resultados guardados en: {nombre_archivo}")

    # ========== PIE DE PÁGINA ==========
    print("\n" + "=" * 60)
    print("Diagnóstico completado")
    print(f"Autor: Xabier Pereira - Modificado por Ignacio Peroni")
    print("github.com/xabierpereira |  github.com/iperoni")
    print("=" * 60)


if __name__ == "__main__":
    main()
