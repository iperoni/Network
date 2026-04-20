#!/usr/bin/env python3
"""
Network Diagnostic Tool (v1.5)
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
import argparse
import configparser
import concurrent.futures
from datetime import datetime

VERSION = "v1.7"

TESTS_MAP = {
    "1": "connectivity",
    "2": "internet",
    "2b": "dns-configured",
    "3": "ports",
    "4": "latency",
    "5": "wifi",
    "6": "isp",
    "7": "packet-loss",
    "8": "interface",
    "9": "firewall",
    "10": "traceroute",
    "11": "speed",
    "12": "dhcp",
    # Nombres también
    "connectivity": "1",
    "internet": "2",
    "dns-configured": "2b",
    "dns-configured": "2b",
    "ports": "3",
    "latency": "4",
    "wifi": "5",
    "isp": "6",
    "packet-loss": "7",
    "packet-loss": "7",
    "interface": "8",
    "firewall": "9",
    "traceroute": "10",
    "speed": "11",
    "dhcp": "12",
}

TEST_NAMES = {
    "1": "Test 1: Conectividad local",
    "2": "Test 2: Internet y DNS",
    "2b": "Test 2B: DNS configurados",
    "3": "Test 3: Puertos críticos",
    "4": "Test 4: Latencia",
    "5": "Test 5: WiFi",
    "6": "Test 6: ISP",
    "7": "Test 7: Pérdida de paquetes",
    "8": "Test 8: Interfaz de red",
    "9": "Test 9: Firewall",
    "10": "Test 10: Traceroute",
    "11": "Test 11: Velocidad internet",
    "12": "Test 12: DHCP",
}

if platform.system().lower() == "windows":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        subprocess.run("chcp 65001", shell=True, capture_output=True)
    except Exception:
        pass


def check_linux_dependencies():
    """Verifica que las dependencias opcionales estén instaladas en Linux"""
    is_windows = platform.system().lower() == "windows"
    if is_windows:
        return {}

    deps = {}
    required_cmds = {
        "iw": "Test WiFi (signal)",
        "ethtool": "Network interface details",
        "traceroute": "Test traceroute",
        "ufw": "Firewall status (UFW)",
        "iptables": "Firewall status (iptables)",
    }

    for cmd, feature in required_cmds.items():
        result = subprocess.run(f"which {cmd}", shell=True, capture_output=True)
        deps[cmd] = result.returncode == 0

    return deps


def print_dependencies_warning(deps):
    """Imprime advertencia sobre dependencias faltantes en Linux"""
    is_windows = platform.system().lower() == "windows"
    if is_windows:
        return

    missing = [cmd for cmd, installed in deps.items() if not installed]
    if missing:
        print("\n⚠️  ADVERTENCIA: Dependencias opcionales faltantes en Linux:")
        for cmd in missing:
            feature = {
                "iw": "WiFi signal",
                "ethtool": "Interface details",
                "traceroute": "Traceroute",
                "ufw": "UFW firewall",
                "iptables": "iptables firewall",
            }.get(cmd, cmd)
            print(f"   - {cmd}: {feature}")
        print("   Instalar con: sudo apt install " + " ".join(missing))
        print()


def get_config_path():
    """Obtiene la ruta del archivo de configuración"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "network_diagnostic.cfg")


def save_preferences(prefs):
    """Guarda las preferencias en archivo CFG"""
    config = configparser.ConfigParser()
    config[" preferences "] = prefs
    try:
        with open(get_config_path(), "w") as f:
            config.write(f)
    except:
        pass


def load_preferences():
    """Carga las preferencias desde archivo CFG"""
    config = configparser.ConfigParser()
    try:
        if config.read(get_config_path()):
            return dict(config[" preferences "])
    except:
        pass
    return {}


def parse_args():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Network Diagnostic Tool - Herramienta de diagnóstico de red",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Abrir menú interactivo para seleccionar tests",
    )
    parser.add_argument(
        "--tests", help="Tests a executar (ej: 1,2,5-7 ou internet,dns,wifi)"
    )
    parser.add_argument(
        "--no-speed", action="store_true", help="Omitir test de velocidade"
    )
    parser.add_argument("--no-isp", action="store_true", help="Omitir consulta ISP")
    parser.add_argument(
        "--format",
        choices=["txt", "json"],
        default="txt",
        help="Formato de output (default: txt)",
    )
    parser.add_argument(
        "-o", "--output", help="Archivo de output (default: automático)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Output detallado")
    parser.add_argument("--version", action="store_true", help="Mostrar versión")
    parser.add_argument(
        "--save-prefs",
        action="store_true",
        help="Gardar preferencias actuales como defecto",
    )
    parser.add_argument(
        "--speed-size",
        help="Tamano del test de velocidad en MB (ej: 5 o 5,10 para download,upload)",
    )
    parser.add_argument(
        "--speed-servers",
        help="Servidores para speed test (cloudflare,nperf,tele2)",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Ejecutar tests independientes en paralelo",
    )

    return parser.parse_args()


def parse_test_string(test_str):
    """Parsea string de tests (ej: '1,2,5-7' ou 'internet,dns,wifi')"""
    if not test_str:
        return []

    tests = set()
    parts = test_str.replace(",", " ").replace("-", " ").split()

    i = 0
    while i < len(parts):
        part = parts[i]

        # Verificar rango (ej: 5-7)
        if i + 1 < len(parts) and parts[i + 1].isdigit():
            start = int(part) if part.isdigit() else TESTS_MAP.get(part, part)
            end = int(parts[i + 1])
            if isinstance(start, str):
                start_num = (
                    int(start) if start.isdigit() else int(TESTS_MAP.get(start, "1"))
                )
            else:
                start_num = start
            for n in range(start_num, end + 1):
                tests.add(str(n))
            i += 2
        else:
            # Test individual o nombre
            num = TESTS_MAP.get(part, part)
            if num.isdigit():
                tests.add(num)
            i += 1

    return sorted(tests, key=lambda x: (len(x), x))


def show_menu():
    """Muestra menú interactivo y retorna tests selecionados"""
    print("\n" + "=" * 50)
    print("       DIAGNÓSTICO DE RED")
    print("       Selecciona los tests:")
    print("=" * 50)

    for num, name in TEST_NAMES.items():
        print(f"  {num:>2}  - {name}")

    print("=" * 50)
    print("  [A] Executar TODOS los tests")
    print("  [Q] Sair")
    print("=" * 50)

    while True:
        try:
            selection = input("\nSelecciona: ").strip().lower()

            if selection == "a":
                return list(TEST_NAMES.keys())
            elif selection == "q":
                print("Saindo...")
                sys.exit(0)
            elif selection:
                return parse_test_string(selection)
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            sys.exit(0)


def get_tests_to_run(args):
    """Determina qué tests executar baseado en args"""
    # Si tem tests especificados
    if args.tests:
        return parse_test_string(args.tests)

    # Si no hay args (compatibilidade atrás) → todos
    return list(TEST_NAMES.keys())


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


def run_traceroute(host, max_hops=30):
    """Ejecuta traceroute y parsea resultados"""
    import re

    is_windows = platform.system().lower() == "windows"
    hops = []

    try:
        if is_windows:
            result = subprocess.run(
                f"tracert -d -h {max_hops} {host}",
                shell=True,
                capture_output=True,
                timeout=60,
            )
            output = result.stdout.decode("cp437", errors="replace")

            for line in output.split("\n"):
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) > 0 and parts[0].isdigit():
                    hop_num = parts[0]
                    ip = None
                    tiempos = []

                    # Extraer tiempos usando regex
                    tiempos_raw = re.findall(r"<?\d+>?\s*ms", line)
                    for t in tiempos_raw:
                        tiempo_clean = (
                            t.replace("<", "")
                            .replace(">", "")
                            .replace("ms", "")
                            .strip()
                        )
                        if tiempo_clean.replace(".", "").isdigit():
                            tiempos.append(tiempo_clean)

                    # Extraer IP
                    for part in parts[1:]:
                        part_clean = part.replace(":", "").strip()
                        if (
                            part_clean.replace(".", "").isdigit()
                            and len(part_clean) > 3
                            and part_clean.count(".") == 3
                        ):
                            ip = part_clean
                            break

                    if ip:
                        try:
                            hostname, _, _ = socket.gethostbyaddr(ip)
                        except:
                            hostname = "N/A"

                        tiempo_str = f"{tiempos[0]} ms" if tiempos else "N/A"
                        hops.append(f"{hop_num}. {ip} ({hostname}) - {tiempo_str}")
                    elif "* * *" in line or not ip:
                        hops.append(f"{hop_num}. * * * (Timeout)")
        else:
            result = subprocess.run(
                f"traceroute -m {max_hops} -I {host}",
                shell=True,
                capture_output=True,
                timeout=60,
            )
            output = result.stdout.decode("utf-8", errors="replace")

            for line in output.split("\n"):
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) > 0 and parts[0].isdigit():
                    hop_num = parts[0]
                    ip = None
                    hostname = "N/A"
                    tiempos = []

                    for part in parts:
                        if "(" in part and ")" in part:
                            ip = part.replace("(", "").replace(")", "")
                            break
                        elif (
                            part.replace(".", "").replace(":", "").isdigit()
                            and len(part) > 3
                        ):
                            ip = part
                            break

                    if ip and ip != "*":
                        try:
                            hostname, _, _ = socket.gethostbyaddr(ip)
                        except:
                            pass

                    for part in parts:
                        if "ms" in part:
                            try:
                                tiempo = part.replace("ms", "").strip()
                                if tiempo.replace(".", "").replace("<", "").isdigit():
                                    tiempos.append(tiempo)
                            except:
                                pass

                    if ip:
                        if ip == "*":
                            hops.append(f"{hop_num}. * * * (Timeout)")
                        else:
                            tiempo_str = f"{tiempos[0]} ms" if tiempos else "N/A"
                            hops.append(f"{hop_num}. {ip} ({hostname}) - {tiempo_str}")
    except Exception as e:
        hops.append(f"Error: {str(e)[:50]}")

    return hops


def get_dhcp_lease_info():
    """Obtiene información del lease DHCP"""
    is_windows = platform.system().lower() == "windows"
    lease_info = {}

    if is_windows:
        output = run_command("ipconfig /all")

        dhcp_enabled = False
        for line in output.split("\n"):
            line_lower = line.lower()
            if "dhcp habilitado" in line_lower or "dhcp enabled" in line_lower:
                if "si" in line_lower or "yes" in line_lower:
                    dhcp_enabled = True
                    lease_info["DHCP"] = "Habilitado"
                else:
                    lease_info["DHCP"] = "Deshabilitado (IP Estática)"

        if dhcp_enabled:
            for line in output.split("\n"):
                line_lower = line.lower()
                if "fecha de obtención" in line_lower or "obtain date" in line_lower:
                    if ":" in line:
                        lease_info["Fecha obtencion"] = line.split(":", 1)[1].strip()
                elif "vencimiento" in line_lower or "lease expires" in line_lower:
                    if ":" in line:
                        lease_info["Vencimiento"] = line.split(":", 1)[1].strip()
                elif "servidor dhcp" in line_lower or "dhcp server" in line_lower:
                    if ":" in line:
                        dhcp_server = line.split(":", 1)[1].strip()
                        if (
                            dhcp_server
                            and dhcp_server != "fec0:0:0ffff::1"
                            and dhcp_server != "fe80::1"
                        ):
                            lease_info["Servidor DHCP"] = dhcp_server
    else:
        output = run_command(
            "cat /var/lib/dhcp/dhclient.leases 2>/dev/null || echo 'No disponible'"
        )
        lines = output.split("\n")
        current_lease = {}
        for line in lines:
            line = line.strip()
            if "lease" in line and "{" in line:
                current_lease = {}
            if "}" in line and current_lease:
                if not lease_info or "ip" not in lease_info:
                    lease_info = current_lease
            if "interface" in line:
                current_lease["Interface"] = line.split()[-1].rstrip(";")
            elif "fixed-address" in line:
                current_lease["IP"] = line.split()[-1].rstrip(";")
            elif "option dhcp-lease-time" in line:
                current_lease["Tiempo lease"] = line.split()[-1].rstrip(";")
            elif "option dhcp-message-type" in line:
                current_lease["Tipo"] = line.split()[-1].rstrip(";")
            elif "renew" in line:
                current_lease["Renew"] = line.split()[1].rstrip(";")
            elif "rebind" in line:
                current_lease["Rebind"] = line.split()[1].rstrip(";")
            elif "expire" in line:
                current_lease["Expire"] = line.split()[1].rstrip(";")

    return lease_info


def test_internet_speed(test_size_mb=5, server_filter=None):
    """Test de velocidad de internet (download + upload)

    Args:
        test_size_mb: Tamaño en MB (puede ser int o tuple (download, upload))
        server_filter: Lista de servidores a usar (ej: ['cloudflare', 'nperf'])
    """
    import time

    if isinstance(test_size_mb, tuple):
        dl_size, ul_size = test_size_mb
    else:
        dl_size = test_size_mb
        ul_size = test_size_mb

    all_download_servers = [
        (
            "Cloudflare",
            "https://speed.cloudflare.com/__down?bytes={size}",
            "curl -L -k -s -A 'Mozilla/5.0'",
            5000000,
        ),
        (
            "nperf",
            "https://www.nperf.com/__down?bytes={size}",
            "curl -L -k -s -A 'Mozilla/5.0'",
            5000000,
        ),
        (
            "Tele2",
            "http://speedtest.tele2.net/{size}MB.zip",
            "curl -s -A 'Mozilla/5.0'",
            5,
        ),
    ]

    all_upload_servers = [
        (
            "Cloudflare",
            "https://speed.cloudflare.com/__up",
            "curl -L -k -s -X POST -A 'Mozilla/5.0'",
            None,
        ),
        (
            "Tele2",
            "http://speedtest.tele2.net/upload.php",
            "curl -s -X POST -A 'Mozilla/5.0'",
            None,
        ),
    ]

    def filter_servers(servers, filter_list):
        if not filter_list:
            return servers
        filter_lower = [s.lower() for s in filter_list]
        return [
            (name, url, opts, size)
            for name, url, opts, size in servers
            if name.lower() in filter_lower
        ]

    download_servers = filter_servers(all_download_servers, server_filter)
    upload_servers = filter_servers(all_upload_servers, server_filter)

    test_size_bytes = dl_size * 1024 * 1024
    test_data = b"X" * (ul_size * 1024 * 1024)

    download_results = []
    upload_results = []

    print(f"\n   📶 Download ({dl_size}MB):")
    for name, url, curl_opts, fixed_size in download_servers:
        try:
            actual_url = url.replace("{size}", str(dl_size))
            if fixed_size and dl_size != fixed_size // 1000000:
                actual_url = actual_url.replace(
                    str(dl_size), str(fixed_size // 1000000)
                )

            start = time.time()
            cmd = (
                f'{curl_opts} -o NUL --connect-timeout 30 --max-time 60 "{actual_url}"'
            )
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=65)
            elapsed = time.time() - start

            if result.returncode == 0 and elapsed > 0:
                speed_mbps = (dl_size * 8) / elapsed
                download_results.append((name, speed_mbps, elapsed))
                print(
                    f"      {name}: {speed_mbps:.1f} Mbps ({dl_size}MB en {elapsed:.1f}s)"
                )
            else:
                print(f"      {name}: Error del servidor")
        except Exception as e:
            print(f"      {name}: Error - {str(e)[:30]}")

    print(f"\n   📶 Upload ({ul_size}MB):")
    for name, url, curl_opts, _ in upload_servers:
        try:
            start = time.time()
            # Crear archivo temporal para upload
            with open("temp_upload.bin", "wb") as f:
                f.write(test_data)
            cmd = f'curl -X POST -o NUL --connect-timeout 30 --max-time 60 -A "Mozilla/5.0" --data-binary "@temp_upload.bin" "{url}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=65)
            elapsed = time.time() - start

            # Limpiar archivo temporal
            try:
                os.remove("temp_upload.bin")
            except:
                pass

            if result.returncode == 0 and elapsed > 0:
                speed_mbps = (ul_size * 8) / elapsed
                upload_results.append((name, speed_mbps, elapsed))
                print(
                    f"      {name}: {speed_mbps:.1f} Mbps ({ul_size}MB en {elapsed:.1f}s)"
                )
            else:
                print(f"      {name}: Error del servidor")
        except Exception as e:
            print(f"      {name}: Error - {str(e)[:30]}")

    summary = {"download": download_results, "upload": upload_results}
    return summary


PARALLEL_TESTS = ["1", "2", "2b", "3", "4", "5", "6", "8", "9", "12"]
SLOW_TESTS = ["7", "10", "11"]


def run_test_by_id(test_id, args, is_windows):
    """Ejecuta un test específico y retorna sus resultados"""
    results = {}

    if test_id == "1":
        loopback_ok = test_ping("127.0.0.1", "Loopback (Interno)")
        gateway = None
        if is_windows:
            output = run_command("ipconfig")
            for line in output.split("\n"):
                if (
                    "puerta de enlace" in line.lower()
                    or "default gateway" in line.lower()
                ):
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
            gateway_ok = test_ping(gateway, f"Gateway ({gateway})")
        results = {
            "gateway": gateway,
            "loopback_ok": loopback_ok,
            "gateway_ok": gateway_ok,
        }

    elif test_id == "2":
        internet_ok = test_ping("8.8.8.8", "Google DNS")
        dns_ok, dns_ip = test_dns("google.com")
        results = {"internet_ok": internet_ok, "dns_ok": dns_ok}

    elif test_id == "2b":
        dns_servers = get_configured_dns()
        for dns in dns_servers:
            test_dns_verification(dns)
        results = {"dns_servers": dns_servers}

    elif test_id == "3":
        test_port("google.com", 443, "HTTPS")
        test_port("8.8.8.8", 53, "DNS")

    elif test_id == "4":
        targets = [("8.8.8.8", "Google"), ("1.1.1.1", "Cloudflare")]
        for ip, name in targets:
            param = "-n" if is_windows else "-c"
            output = run_command(f"ping {param} 5 {ip}")
            for line in output.split("\n"):
                if any(k in line.lower() for k in ["average", "media", "min", "max"]):
                    pass

    elif test_id == "5":
        conn_type = get_connection_type()
        wifi_info = None
        if is_windows:
            wifi_info = test_wifi_signal()
        else:
            if conn_type == "wifi":
                wifi_info = test_wifi_signal()
        results = {"conn_type": conn_type, "wifi_info": wifi_info}

    elif test_id == "6" and not args.no_isp:
        isp_info = get_public_ip_and_isp()
        results = {"isp_info": isp_info}

    elif test_id == "8":
        interface_details = get_network_interface_details()
        results = {"interface_details": interface_details}

    elif test_id == "9":
        firewall_info = get_firewall_status()
        results = {"firewall_info": firewall_info}

    elif test_id == "12":
        dhcp_info = get_dhcp_lease_info()
        results = {"dhcp_info": dhcp_info}

    return results


def run_parallel_tests(selected_tests, args, is_windows):
    """Ejecuta tests independientes en paralelo"""
    parallel = [t for t in selected_tests if t in PARALLEL_TESTS]
    slow = [t for t in selected_tests if t in SLOW_TESTS]

    results = {}

    print("\n⚡ Ejecutando tests en paralelo...")

    if parallel:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                test_id: executor.submit(run_test_by_id, test_id, args, is_windows)
                for test_id in parallel
            }

            for test_id, future in futures.items():
                try:
                    results[test_id] = future.result()
                except Exception as e:
                    results[test_id] = {"error": str(e)}

    print("✅ Tests paralelos completados")

    if slow:
        print("\n⏳ Ejecutando tests secuenciales...")
        for test_id in slow:
            if test_id == "7":
                print_header("TEST 7: PÉRDIDA DE PAQUETES")
                hosts = [("8.8.8.8", "Google DNS"), ("1.1.1.1", "Cloudflare")]
                for host, name in hosts:
                    test_packet_loss(host, count=10)
            elif test_id == "10":
                print_header("TEST 10: TRACEROUTE")
                targets = [("youtube.com", "YouTube"), ("yahoo.com", "Yahoo")]
                for host, name in targets:
                    run_traceroute(host, max_hops=30)
            elif test_id == "11" and not args.no_speed:
                print_header("TEST 11: VELOCIDAD DE INTERNET")
                speed_size = 5
                if args.speed_size:
                    parts = args.speed_size.split(",")
                    if len(parts) == 2:
                        speed_size = (int(parts[0]), int(parts[1]))
                    else:
                        speed_size = int(parts[0])
                speed_servers = None
                if args.speed_servers:
                    speed_servers = [s.strip() for s in args.speed_servers.split(",")]
                test_internet_speed(speed_size, speed_servers)

    return results


def main():
    args = parse_args()

    # Version flag
    if args.version:
        print(f"Network Diagnostic Tool {VERSION}")
        return

    # Cargar preferencias
    prefs = load_preferences()

    # Determinar tests a ejecutar
    if args.interactive:
        selected_tests = show_menu()
    else:
        selected_tests = get_tests_to_run(args)

    # Guardar preferencias si se pide
    if args.save_prefs:
        save_preferences(
            {
                "format": args.format,
                "no_speed": str(args.no_speed),
                "no_isp": str(args.no_isp),
                "verbose": str(args.verbose),
            }
        )
        print("Preferencias guardadas.")

    is_windows = platform.system().lower() == "windows"

    # Verificar dependencias en Linux
    linux_deps = check_linux_dependencies()

    # Si no hay tests selecionados (compatibilidad atrás), ejecutar todos
    if not selected_tests:
        selected_tests = list(TEST_NAMES.keys())

    # Ejecutar en paralelo si se pide
    if args.parallel and len(selected_tests) > 1:
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 20 + "DIAGNÓSTICO DE RED" + " " * 20 + "║")
        print("╚" + "═" * 58 + "╝")
        print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Versión: {VERSION}")
        print_dependencies_warning(linux_deps)

        # Info local siempre
        print_header("INFORMACIÓN LOCAL")
        print(f"📌 Hostname: {socket.gethostname()}")
        print(f"📌 IP Local Detectada: {get_real_ip()}")

        # Ejecutar tests
        run_parallel_tests(selected_tests, args, is_windows)
        return

    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 20 + "DIAGNÓSTICO DE RED" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Versión: {VERSION}")

    # Mostrar advertencias de dependencias en Linux
    print_dependencies_warning(linux_deps)

    # Si no hay tests selecionados (compatibilidad atrás), ejecutar todos
    if not selected_tests:
        selected_tests = list(TEST_NAMES.keys())

    # ========== INFORMACIÓN LOCAL (siempre) ==========
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

    # Ejecutar solo los tests seleccionados
    # Variables globales para compartir entre tests
    global gateway, gateway_ok, loopback_ok, internet_ok, dns_ok
    global dns_servers, conn_type, wifi_info, isp_info
    global packet_loss_results, interface_details, firewall_info
    global traceroute_results, speed_results, dhcp_info

    loopback_ok = False
    gateway = None
    gateway_ok = False
    internet_ok = False
    dns_ok = False
    dns_servers = []
    conn_type = "unknown"
    wifi_info = {}
    isp_info = {}
    packet_loss_results = []
    interface_details = {}
    firewall_info = {}
    traceroute_results = []
    speed_results = {}
    dhcp_info = {}

    # Test 1: Conectividad local
    if "1" in selected_tests:
        print_header("TEST 1: CONECTIVIDAD LOCAL")
        loopback_ok = test_ping("127.0.0.1", "Loopback (Interno)")

        gateway = None
        if is_windows:
            output = run_command("ipconfig")
            for line in output.split("\n"):
                if (
                    "puerta de enlace" in line.lower()
                    or "default gateway" in line.lower()
                ):
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

    # Test 2: Internet y DNS
    if "2" in selected_tests:
        print_header("TEST 2: INTERNET Y DNS")

        internet_ok = test_ping("8.8.8.8", "Google DNS")
        dns_ok, _ = test_dns("google.com")

    # Test 2B: DNS configurados
    if "2b" in selected_tests:
        print_header("TEST 2B: SERVIDORES DNS CONFIGURADOS")
        dns_servers = get_configured_dns()
        if dns_servers:
            print(f"   📋 Servidores DNS configurados ({len(dns_servers)}):")
            for dns in dns_servers:
                print(f"      - {dns}")
                test_dns_verification(dns)
        else:
            print("   ⚠️ No se detectaron servidores DNS configurados")

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

    # Test 3: Puertos
    if "3" in selected_tests:
        print_header("TEST 3: PUERTOS CRÍTICOS")
        test_port("google.com", 443, "HTTPS")
        test_port("8.8.8.8", 53, "DNS")

    # Test 4: Latencia
    if "4" in selected_tests:
        print_header("TEST 4: ESTADÍSTICAS DE LATENCIA")
        targets = [("8.8.8.8", "Google"), ("1.1.1.1", "Cloudflare")]
        for ip, name in targets:
            print(f"\n📡 {name}:")
            param = "-n" if is_windows else "-c"
            output = run_command(f"ping {param} 5 {ip}")
            for line in output.split("\n"):
                if any(k in line.lower() for k in ["average", "media", "min", "max"]):
                    print(f"   {line.strip()}")

    # Test 5: WiFi
    if "5" in selected_tests:
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
            elif (
                "Estado" in wifi_info and "no disponible" in wifi_info["Estado"].lower()
            ):
                print(f"   ⚠️ {wifi_info.get('Estado', 'Servicio WiFi no disponible')}")
                print(f"   💡 Tipo de conexión: ETHERNET")
            else:
                print(f"   ℹ️ Adaptador WiFi detectado pero Sin conexión activa")
                print(f"   💡 Tipo de conexión actual: ETHERNET")
        else:
            print(f"   ℹ️ Sin adaptador WiFi detectado")
            print(f"   💡 Tipo de conexión: ETHERNET")

    # Test 6: ISP
    if "6" in selected_tests and not args.no_isp:
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

    # Test 7: Pérdida de paquetes
    if "7" in selected_tests:
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

    # Test 8: Interfaz de red
    if "8" in selected_tests:
        print_header("TEST 8: DETALLES DEL INTERFAZ DE RED")
        interface_details = get_network_interface_details()
        if interface_details:
            print(f"   📡 Información del interfaz de red:")
            for key, value in interface_details.items():
                print(f"      {key}: {value}")
        else:
            print("   ⚠️ No se pudo obtener información del interfaz")

    # Test 9: Firewall
    if "9" in selected_tests:
        print_header("TEST 9: ESTADO DEL FIREWALL")
        firewall_info = get_firewall_status()
        if firewall_info:
            print(f"   🔥 Estado del firewall:")
            for key, value in firewall_info.items():
                print(f"      {key}: {value}")
        else:
            print("   ⚠️ No se pudo obtener información del firewall")

    # Test 10: Traceroute
    if "10" in selected_tests:
        print_header("TEST 10: TRACEROUTE")
        targets = [("youtube.com", "YouTube (CDN)"), ("yahoo.com", "Yahoo (IPTransit)")]
        traceroute_results = []

        for host, name in targets:
            print(f"\n   📍 Ruta hacia {name}:")
            hops = run_traceroute(host, max_hops=30)
            if hops:
                traceroute_results.append((name, hops))
                for hop in hops[:20]:
                    print(f"      {hop}")
                if len(hops) > 20:
                    print(f"      ... y {len(hops) - 20} saltos más")
            else:
                print("      ⚠️ No se pudo obtener ruta")
                traceroute_results.append((name, None))

    # Test 11: Velocidad (omitir si --no-speed)
    if "11" in selected_tests and not args.no_speed:
        speed_size = 5
        if args.speed_size:
            parts = args.speed_size.split(",")
            if len(parts) == 2:
                speed_size = (int(parts[0]), int(parts[1]))
            else:
                speed_size = int(parts[0])

        speed_servers = None
        if args.speed_servers:
            speed_servers = [s.strip() for s in args.speed_servers.split(",")]

        print_header("TEST 11: VELOCIDAD DE INTERNET")
        speed_results = test_internet_speed(speed_size, speed_servers)

    if speed_results.get("download") or speed_results.get("upload"):
        print("\n   📊 Resumen:")
        if speed_results.get("download"):
            avg_dl = sum(r[1] for r in speed_results["download"]) / len(
                speed_results["download"]
            )
            max_dl = max(r[1] for r in speed_results["download"])
            print(f"      Download promedio: {avg_dl:.1f} Mbps")
            print(f"      Download máxima: {max_dl:.1f} Mbps")
        if speed_results.get("upload"):
            avg_ul = sum(r[1] for r in speed_results["upload"]) / len(
                speed_results["upload"]
            )
            max_ul = max(r[1] for r in speed_results["upload"])
            print(f"      Upload promedio: {avg_ul:.1f} Mbps")
            print(f"      Upload máxima: {max_ul:.1f} Mbps")
    else:
        print("   ⚠️ No se pudo obtener información de velocidad")

    # Test 12: DHCP
    if "12" in selected_tests:
        print_header("TEST 12: INFORMACIÓN DHCP")
        dhcp_info = get_dhcp_lease_info()
        if dhcp_info:
            print(f"   📋 Información del lease DHCP:")
            for key, value in dhcp_info.items():
                print(f"      {key}: {value}")
        else:
            print("   ⚠️ No se pudo obtener información DHCP")

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

        # TEST 10: TRACEROUTE
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 10: TRACEROUTE\n")
        f.write("=" * 60 + "\n")
        for name, hops in traceroute_results:
            f.write(f"\n{name}:\n")
            if hops:
                for hop in hops[:20]:
                    f.write(f"   {hop}\n")
                if len(hops) > 20:
                    f.write(f"   ... y {len(hops) - 20} saltos más\n")
            else:
                f.write("   No se pudo obtener ruta\n")

        # TEST 11: VELOCIDAD
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 11: VELOCIDAD DE INTERNET\n")
        f.write("=" * 60 + "\n")

        dl_results = speed_results.get("download", [])
        ul_results = speed_results.get("upload", [])

        f.write("\nDownload:\n")
        if dl_results:
            for name, speed, time_sec in dl_results:
                f.write(f"   {name}: {speed:.1f} Mbps\n")
        else:
            f.write("   No disponible\n")

        f.write("\nUpload:\n")
        if ul_results:
            for name, speed, time_sec in ul_results:
                f.write(f"   {name}: {speed:.1f} Mbps\n")
        else:
            f.write("   No disponible\n")

        if dl_results:
            avg_dl = sum(r[1] for r in dl_results) / len(dl_results)
            max_dl = max(r[1] for r in dl_results)
            f.write(f"\nResumen Download:\n")
            f.write(f"   Promedio: {avg_dl:.1f} Mbps\n")
            f.write(f"   Maxima: {max_dl:.1f} Mbps\n")

        if ul_results:
            avg_ul = sum(r[1] for r in ul_results) / len(ul_results)
            max_ul = max(r[1] for r in ul_results)
            f.write(f"\nResumen Upload:\n")
            f.write(f"   Promedio: {avg_ul:.1f} Mbps\n")
            f.write(f"   Maxima: {max_ul:.1f} Mbps\n")

        # TEST 12: DHCP INFO
        f.write("\n" + "=" * 60 + "\n")
        f.write("   TEST 12: INFORMACIÓN DHCP\n")
        f.write("=" * 60 + "\n")
        if dhcp_info:
            for key, value in dhcp_info.items():
                f.write(f"{key}: {value}\n")
        else:
            f.write("No se pudo obtener información DHCP\n")

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
