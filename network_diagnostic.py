#!/usr/bin/env python3
"""
Network Diagnostic Tool (v1.7)
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
import io
import urllib.request
import urllib.error
from datetime import datetime

# ==============================================================================
# CONSTANTES GLOBALES
# ==============================================================================

VERSION = "v1.25.2"
IS_WINDOWS = platform.system().lower() == "windows"

# Timeout configurations
TIMEOUT_DEFAULT = 10  # Timeout general para comandos
TIMEOUT_LONG = 30  # Timeout largo (speed test, traceroute)
TIMEOUT_CONNECT = 3  # Timeout para conexión de sockets

# Test configurations
PING_COUNT = 4  # Número de pings por test
PACKET_LOSS_COUNT = 10  # Paquetes para test de pérdida
TRACEROUTE_HOPS = 30  # Saltos máximos para traceroute

# Test hosts
TEST_HOSTS = {
    "loopback": "127.0.0.1",
    "google_dns": "8.8.8.8",
    "cloudflare_dns": "1.1.1.1",
}

# Mapeo de tests: número -> nombre y nombre -> número
TESTS_MAP = {
    # Número a nombre
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
    # Nombre a número
    "connectivity": "1",
    "internet": "2",
    "dns-configured": "2b",
    "ports": "3",
    "latency": "4",
    "wifi": "5",
    "isp": "6",
    "packet-loss": "7",
    "interface": "8",
    "firewall": "9",
    "traceroute": "10",
    "speed": "11",
    "dhcp": "12",
    "16": "simul-connections",
    # Nombre a número
    "connectivity": "1",
    "internet": "2",
    "dns-configured": "2b",
    "ports": "3",
    "latency": "4",
    "wifi": "5",
    "isp": "6",
    "packet-loss": "7",
    "interface": "8",
    "firewall": "9",
    "traceroute": "10",
    "speed": "11",
    "dhcp": "12",
    "simul-connections": "16",
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
    "13": "Test 13: Bufferbloat (QoS)",
    "14": "Test 14: MTU",
    "15": "Test 15: DNS Alternativos",
    "16": "Test 16: Conexiones Simultáneas",
}

# ==============================================================================
# CONFIGURACIONES DE PLATAFORMA
# ==============================================================================

# Linux: dependencias opcionales para ciertas funciones
LINUX_DEPS = {
    "iw": "Test WiFi (signal)",
    "ethtool": "Network interface details",
    "traceroute": "Test traceroute",
    "ufw": "Firewall status (UFW)",
    "iptables": "Firewall status (iptables)",
}

# Linux: features que requieren dependencias
LINUX_FEATURES = {
    "iw": "WiFi signal",
    "ethtool": "Interface details",
    "traceroute": "Traceroute",
    "ufw": "UFW firewall",
    "iptables": "iptables firewall",
}

# ==============================================================================
# CONFIGURACIÓN DE PLATAFORMA
# ==============================================================================

# Configurar UTF-8 en Windows
if IS_WINDOWS:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        subprocess.run("chcp 65001", shell=True, capture_output=True)
    except Exception:
        pass


# ==============================================================================
# CONFIGURACIONES DE TESTS
# ==============================================================================

# Comandos del sistema por SO
SYS_COMMANDS = {
    "windows": {
        "config_all": "ipconfig /all",
        "dns_flush": "ipconfig /flushdns",
        "winsock": "netsh winsock reset",
        "ping": "ping -n {count} {host}",
        "traceroute": "tracert -d -h {max_hops} {host}",
        "wifi_show": "netsh wlan show interfaces",
        "wifi_list": "netsh wlan show networks mode=bssid",
        "firewall_profiles": "netsh advfirewall show allprofiles",
        "firewall_rules": "netsh advfirewall show rule name=all",
        "dhcp_info": "ipconfig /all",
        "interface_set": 'netsh interface set interface "{name}" admin=enabled',
        "dns_set": 'netsh interface ip set dns "{adapter}" static {dns}',
        "dns_add": 'netsh interface ip add dns "{adapter}" {dns} index={index}',
        "dnsserver_show": "netsh interface ipv4 show dns",
    },
    "linux": {
        "config_all": "ip addr show",
        "dns_flush": "systemd-resolve --flush-caches || resolvectl flush-caches",
        "winsock": "sudo systemctl restart NetworkManager",
        "ping": "ping -c {count} {host}",
        "traceroute": "traceroute -m {max_hops} -n {host}",
        "wifi_show": "iwconfig || nmcli dev status",
        "wifi_list": "nmcli dev wifi list",
        "firewall_profiles": "sudo iptables -L -n -v",
        "firewall_rules": "sudo iptables -L -n --line-numbers",
        "dhcp_info": "cat /var/lib/dhcp/dhclient.leases",
        "interface_set": "sudo ip link set {name} up",
        "dns_set": 'echo "nameserver {dns}" | sudo tee /etc/resolv.conf',
        "dns_add": 'echo "nameserver {dns}" | sudo tee -a /etc/resolv.conf',
        "dnsserver_show": "cat /etc/resolv.conf",
    },
}


# Obtener comandos según el SO actual
def get_cmd(key):
    """Retorna comando según el SO actual"""
    os_type = "windows" if IS_WINDOWS else "linux"
    return SYS_COMMANDS.get(os_type, {}).get(key, "")


# Tamaño por defecto para speed test
DEFAULT_SPEED_SIZE = 20  # MB

# Servidores para speed test con fallback automático
SPEED_SERVERS = {
    "cloudflare": {
        "download": "https://speed.cloudflare.com/__down?bytes={size}",
        "upload": "https://speed.cloudflare.com/__up",
        "upload_method": "formdata",
    },
    "nperf": {
        "download": "https://www.nperf.com/__down?bytes={size}",
        "upload": None,
        "upload_method": None,
    },
    "tele2": {
        "download": "http://speedtest.tele2.net/{size}MB.zip",
        "upload": "http://speedtest.tele2.net/upload.php",
        "upload_method": "databinary",
    },
    "tempfile": {
        "download": None,
        "upload": "https://tempfile.org/api/upload/local",
        "upload_method": "formdata",
        "upload_field": "files",
    },
    "oshi": {
        "download": None,
        "upload": "https://oshi.io/upload",
        "upload_method": "formdata",
    },
}

# Orden de fallback para download y upload
DOWNLOAD_ORDER = ["cloudflare", "nperf", "tele2"]
UPLOAD_ORDER = ["cloudflare", "tempfile", "oshi"]

# ==============================================================================
# TROUBLESHOOTING - SUGERENCIAS AUTOMATIZADAS
# ==============================================================================

SUGGESTIONS = []

# ==============================================================================
# OUTPUT CAPTURE - Captura stdout para archivo idéntico
# ==============================================================================

import io

OUTPUT_BUFFER = None
ORIGINAL_STDOUT = None


class DualOutput:
    """Wrapper que escribe a stdout y buffer simultáneamente"""

    def __init__(self, original, buffer):
        self.original = original
        self.buffer = buffer

    def write(self, data):
        self.original.write(data)
        self.buffer.write(data)

    def flush(self):
        self.original.flush()
        self.buffer.flush()

    def isatty(self):
        return self.original.isatty()


def start_capture():
    """Inicia captura de stdout"""
    global OUTPUT_BUFFER, ORIGINAL_STDOUT
    ORIGINAL_STDOUT = sys.stdout
    OUTPUT_BUFFER = io.StringIO()
    sys.stdout = DualOutput(sys.stdout, OUTPUT_BUFFER)


def end_capture(ruta_archivo):
    """Guarda contenido capturado al archivo"""
    global ORIGINAL_STDOUT
    OUTPUT_BUFFER.seek(0)
    content = OUTPUT_BUFFER.getvalue()
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(content)
    sys.stdout = ORIGINAL_STDOUT


def suggest(level, test_id, test_name, problem, suggestion, command=""):
    """Agrega una sugerencia de troubleshooting"""
    SUGGESTIONS.append(
        {
            "level": level,
            "test_id": test_id,
            "test_name": test_name,
            "problem": problem,
            "suggestion": suggestion,
            "command": command,
        }
    )


def print_suggestion(s):
    """Imprime una sugerencia formateada"""
    icon = {"critical": "🔴", "warning": "🟡", "info": "ℹ️"}.get(s["level"], "ℹ️")
    print(f"   {icon} [{s['test_id']}] {s['test_name']}: {s['problem']}")
    if s["suggestion"]:
        print(f"      → {s['suggestion']}")
    if s["command"]:
        print(f"      → {s['command']}")


def print_all_suggestions():
    """Imprime todas las sugerencias colectadas"""
    if not SUGGESTIONS:
        return
    print("\n" + "=" * 60)
    print("   SUGERENCIAS DE TROUBLESHOOTING")
    print("=" * 60)
    critical = [s for s in SUGGESTIONS if s["level"] == "critical"]
    warning = [s for s in SUGGESTIONS if s["level"] == "warning"]
    info = [s for s in SUGGESTIONS if s["level"] == "info"]
    for s in critical:
        print_suggestion(s)
    for s in warning:
        print_suggestion(s)
    for s in info:
        print_suggestion(s)
    print()


def write_all_suggestions(f):
    """Escribe todas las sugerencias al archivo"""
    if not SUGGESTIONS:
        return
    f.write("\n" + "=" * 60 + "\n")
    f.write("   SUGERENCIAS DE TROUBLESHOOTING\n")
    f.write("=" * 60 + "\n")
    critical = [s for s in SUGGESTIONS if s["level"] == "critical"]
    warning = [s for s in SUGGESTIONS if s["level"] == "warning"]
    info = [s for s in SUGGESTIONS if s["level"] == "info"]
    for s in critical:
        _write_suggestion(f, s)
    for s in warning:
        _write_suggestion(f, s)
    for s in info:
        _write_suggestion(f, s)
    f.write("\n")


def _write_suggestion(f, s):
    """Escribe una sugerencia formateada al archivo"""
    icon = {"critical": "[X]", "warning": "[!]", "info": "[i]"}.get(s["level"], "[i]")
    f.write(f"   {icon} [{s['test_id']}] {s['test_name']}: {s['problem']}\n")
    f.write(f"      -> {s['suggestion']}\n")
    if s["command"]:
        f.write(f"      -> {s['command']}\n")


def analyze_test_1(results):
    """Test 1: Conectividad local"""
    gateway = results.get("gateway")
    gateway_ok = results.get("gateway_ok", False)
    local_ip = results.get("local_ip", "")

    if local_ip.startswith("169.254."):
        suggest(
            "critical",
            "1",
            "Conectividad Local",
            "APIPA detectada — DHCP falló",
            "La IP 169.254.x.x indica que no se obtuvo lease DHCP",
            f"{get_cmd('config_all')} && {get_cmd('config_all').replace('/all', '/release')} && {get_cmd('config_all').replace('/all', '/renew')}",
        )
    elif gateway is None:
        suggest(
            "critical",
            "1",
            "Conectividad Local",
            "Gateway no detectado",
            "Verificar que DHCP esté habilitado en el router, cables y adaptador",
            get_cmd("config_all"),
        )
    elif not gateway_ok:
        suggest(
            "critical",
            "1",
            "Conectividad Local",
            "Gateway inaccesible",
            "El gateway no responde. Verificar router, cables o reiniciar",
            f"Ping manual al gateway: ping {gateway}",
        )
    elif gateway_ok:
        gw_latency = results.get("gateway_latency", 0)
        if gw_latency > 10:
            suggest(
                "warning",
                "1",
                "Conectividad Local",
                f"Gateway lento ({gw_latency}ms)",
                "Latencia elevada al gateway. Verificar congestión LAN",
                "",
            )


def analyze_test_2(results):
    """Test 2: Internet y DNS"""
    internet_ok = results.get("internet_ok", False)
    dns_ok = results.get("dns_ok", False)
    dns_time = results.get("dns_time", 0)

    if not internet_ok and not dns_ok:
        suggest(
            "critical",
            "2",
            "Internet y DNS",
            "Sin conectividad",
            "Reiniciar módem y router. Si persiste, contactar ISP",
            "",
        )
    elif not internet_ok and dns_ok:
        suggest(
            "warning",
            "2",
            "Internet y DNS",
            "ICMP bloqueado",
            "Ping bloqueado por ISP (normal). Web debería funcionar",
            "",
        )
    elif internet_ok and not dns_ok:
        suggest(
            "critical",
            "2",
            "Internet y DNS",
            "DNS no resuelve",
            "Verificar DNS configurado. Probar 8.8.8.8",
            "",
        )

    # DNS lento
    if dns_ok and dns_time > 2000:
        suggest(
            "warning",
            "2",
            "DNS Lento",
            f"Resolución lenta ({dns_time:.0f}ms)",
            "Cambiar DNS a 8.8.8.8 o 1.1.1.1 para mejor velocidad",
            "",
        )
    elif internet_ok and not dns_ok:
        suggest(
            "critical",
            "2",
            "Internet y DNS",
            "DNS no resuelve",
            "Verificar configuración DNS. Probar nslookup",
            "nslookup google.com 8.8.8.8",
        )


def analyze_test_2b(results):
    """Test 2B: DNS configurados"""
    dns_servers = results.get("dns_servers", [])
    dns_open = results.get("dns_open", {})

    if not dns_servers:
        suggest(
            "critical",
            "2b",
            "DNS Configurados",
            "Sin servidores DNS",
            "Configurar DNS manualmente",
            get_cmd("dns_set").format(adapter="Ethernet", dns="8.8.8.8"),
        )
    else:
        closed = [d for d in dns_servers if dns_open.get(d, True) is False]
        if closed:
            suggest(
                "critical",
                "2b",
                "DNS Configurados",
                f"DNS caído: {closed[0]}",
                "Cambiar DNS primario a 8.8.8.8",
                get_cmd("dns_set").format(adapter="Ethernet", dns="8.8.8.8"),
            )
        if len(dns_servers) == 1:
            suggest(
                "warning",
                "2b",
                "DNS Configurados",
                "Sin redundancia DNS",
                "Agregar DNS secundario 1.1.1.1",
                get_cmd("dns_add").format(adapter="Ethernet", dns="1.1.1.1", index=2),
            )


def analyze_test_3(results):
    """Test 3: Puertos críticos"""
    port_443 = results.get("port_443", False)
    port_53 = results.get("port_53", False)

    if not port_443:
        suggest(
            "critical",
            "3",
            "Puertos",
            "Puerto 443 (HTTPS) cerrado",
            "Verificar firewall, proxy o ISP bloquea HTTPS",
            get_cmd("firewall_profiles"),
        )
    if not port_53:
        suggest(
            "critical",
            "3",
            "Puertos",
            "Puerto 53 (DNS) cerrado",
            "Firewall o ISP bloquea puerto 53",
            "",
        )
    if port_443 and not port_53:
        suggest(
            "warning",
            "3",
            "Puertos",
            "DNS interceptado por VPN",
            "Verificar si VPN está activa y intercepta DNS",
            "",
        )


def test_latency_target(ip, name, count=5):
    """Test de latencia a un target. Retorna dict con min/max/avg/jitter"""
    is_win = platform.system().lower() == "windows"
    param = "-n" if is_win else "-c"
    output = run_command(f"ping {param} {count} {ip}")

    result = {
        "ip": ip,
        "name": name,
        "min": 0,
        "max": 0,
        "avg": 0,
        "jitter": 0,
        "ok": False,
    }
    times = []

    for line in output.split("\n"):
        line_lower = line.lower()
        if "time=" in line_lower or "tiempo=" in line_lower:
            try:
                if "time=" in line_lower:
                    idx = line_lower.index("time=")
                    time_str = (
                        line[idx + 5 :].split()[0].replace("ms", "").replace("TTL", "")
                    )
                else:
                    idx = line_lower.index("tiempo=")
                    time_str = (
                        line[idx + 7 :].split()[0].replace("ms", "").replace("TTL", "")
                    )
                times.append(float(time_str))
            except:
                pass

    if times:
        result["ok"] = True
        result["min"] = min(times)
        result["max"] = max(times)
        result["avg"] = round(sum(times) / len(times), 1)
        result["jitter"] = round(result["max"] - result["min"], 1)

    return result


def analyze_test_4(results):
    """Test 4: Latencia"""
    latency_data = results.get("latency", [])

    for lat in latency_data:
        if not lat.get("ok", False):
            continue
        avg = lat.get("avg", 0)
        jitter = lat.get("jitter", 0)
        name = lat.get("name", lat.get("ip", ""))

        if avg > 500:
            suggest(
                "critical",
                "4",
                f"Latencia {name}",
                f"Latencia crítica ({avg}ms)",
                "Verificar línea; llamar ISP",
                get_cmd("traceroute").format(max_hops=30, host=lat["ip"]),
            )
        elif avg > 200:
            suggest(
                "warning",
                "4",
                f"Latencia {name}",
                f"Latencia alta ({avg}ms)",
                "Llamar ISP; verificar plan",
                "",
            )
        elif avg > 100:
            suggest(
                "warning",
                "4",
                f"Latencia {name}",
                f"Latencia elevada ({avg}ms)",
                "Verificar QoS del router",
                "",
            )

        if jitter > 100:
            suggest(
                "critical",
                "4",
                f"Inestabilidad {name}",
                f"Inestabilidad severa ({jitter}ms jitter)",
                "Verificar línea; considerar ISP alternativo",
                get_cmd("traceroute").format(max_hops=30, host=lat["ip"]),
            )
        elif jitter > 50:
            suggest(
                "warning",
                "4",
                f"Inestabilidad {name}",
                f"Inestabilidad moderada ({jitter}ms jitter)",
                "Verificar cableado, interferencia",
                "",
            )

        # Latencia base alta (>50ms)
        min_lat = lat.get("min", 0)
        if min_lat > 50:
            suggest(
                "info",
                "4",
                f"Latencia base {name}",
                f"Latencia base elevada ({min_lat}ms)",
                "Normal en área rural o ISP lento",
                "",
            )


def analyze_test_5(results):
    """Test 5: WiFi"""
    wifi_info = results.get("wifi_info", {})
    conn_type = results.get("conn_type", "")

    if conn_type != "wifi":
        return

    signal_str = wifi_info.get("Signal", "0%")

    signal_pct = 0
    try:
        signal_pct = int(signal_str.replace("%", ""))
    except:
        pass

    if signal_pct <= 20:
        suggest(
            "critical",
            "5",
            "WiFi",
            f"Señal muy débil ({signal_pct}%)",
            "Sin conexión estable. Mover router o cambiar posición",
            "",
        )
    elif signal_pct <= 50:
        suggest(
            "warning",
            "5",
            "WiFi",
            f"Señal débil ({signal_pct}%)",
            "Verificar obstrucciones, cambiar canal",
            "",
        )

    channel = wifi_info.get("Channel", "")
    if channel:
        try:
            chan_num = int(channel.split()[0])
            if chan_num in [1, 6, 11]:
                suggest(
                    "info",
                    "5",
                    "WiFi",
                    f"Canal {chan_num} puede estar saturado",
                    "Considerar cambiar a canal 5GHz o otro",
                    "",
                )
        except:
            pass


def analyze_test_6(results):
    """Test 6: ISP"""
    isp_info = results.get("isp_info", {})

    isp = isp_info.get("isp", "")
    city = isp_info.get("city", "")

    if not isp:
        suggest(
            "warning",
            "6",
            "ISP",
            "ISP desconocido",
            "Puede ser VPN o proxy. Verificar configuración",
            "",
        )

    if not city:
        suggest("info", "6", "ISP", "Geolocalización limitée", "No requiere acción", "")


def test_packet_loss(host, count=10):
    """Test de pérdida de paquetes"""
    is_windows = platform.system().lower() == "windows"
    param = "-n" if is_windows else "-c"
    result = subprocess.run(
        f"ping {param} {count} {host}", shell=True, capture_output=True, timeout=30
    )
    output = result.stdout.decode("cp437" if is_windows else "utf-8", errors="replace")
    packet_info = {}
    for line in output.split("\n"):
        if "paquetes" in line.lower() and "enviados" in line.lower():
            for part in line.split(","):
                if "enviados" in part.lower():
                    packet_info["enviados"] = part.split("=")[1].strip()
                elif "recibidos" in part.lower():
                    packet_info["recibidos"] = part.split("=")[1].strip()
                elif "perdidos" in part.lower():
                    packet_info["perdidos"] = part.split("=")[1].strip()
    if "enviados" in packet_info and "perdidos" in packet_info:
        try:
            pct = (int(packet_info["perdidos"]) / int(packet_info["enviados"])) * 100
            packet_info["% perda"] = f"{pct:.0f}%"
        except:
            pass
    return packet_info


def test_internet_speed(test_size_mb=20):
    """Test de velocidad de internet"""
    size = test_size_mb * 1024 * 1024
    test_data = b"X" * size
    download_results = []
    upload_results = []

    print(f"\n   📶 Download ({test_size_mb}MB):")
    start = time.time()
    subprocess.run(
        f'curl -L -k -s -o NUL "https://speed.cloudflare.com/__down?bytes={size}"',
        shell=True,
        capture_output=True,
        timeout=60,
    )
    dl_speed = test_size_mb * 8 / max(time.time() - start, 0.1)
    print(f"      Cloudflare: {dl_speed:.1f} Mbps")
    download_results.append(("Cloudflare", dl_speed, time.time() - start))

    print(f"\n   📶 Upload ({test_size_mb}MB):")
    with open("temp_upload.bin", "wb") as f:
        f.write(test_data)
    start = time.time()
    subprocess.run(
        'curl -k -s -X POST -F "file=@temp_upload.bin" "https://speed.cloudflare.com/__up"',
        shell=True,
        capture_output=True,
        timeout=60,
    )
    try:
        os.remove("temp_upload.bin")
    except:
        pass
    ul_speed = test_size_mb * 8 / max(time.time() - start, 0.1)
    print(f"      Cloudflare: {ul_speed:.1f} Mbps")
    upload_results.append(("Cloudflare", ul_speed, time.time() - start))

    return {"download": download_results, "upload": upload_results}


def run_traceroute(host, max_hops=30):
    """Ejecuta traceroute"""
    is_windows = platform.system().lower() == "windows"
    if is_windows:
        cmd = f"tracert -d -h {max_hops} {host}"
    else:
        cmd = f"traceroute -m {max_hops} -n {host}"

    result = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
    output = result.stdout.decode("cp437" if is_windows else "utf-8", errors="replace")

    hops_data = []
    for line in output.split("\n"):
        if line.strip() and (
            line.strip()[0].isdigit() or line.strip().startswith("1 ")
        ):
            line = line.strip()
            latency = 0
            times = []
            for part in line.split():
                if (
                    part.replace("ms", "")
                    .replace("<", "")
                    .replace("s", "")
                    .replace("m", "")
                    .isdigit()
                ):
                    try:
                        t = int(part.replace("ms", "").replace("<", ""))
                        times.append(t)
                    except:
                        pass
            if times:
                latency = sum(times) / len(times)

            ip_match = re.search(r"\d+\.\d+\.\d+\.\d+", line)
            hop_ip = ip_match.group(0) if ip_match else line[:20]
            hops_data.append({"ip": hop_ip, "latency": latency, "line": line})

    return hops_data[:15]


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
            return True
        else:
            print(f"         ⚠️ {dns_server}:53 (Puerto DNS cerrado)")
            return False
    except Exception as e:
        print(f"         ❌ {dns_server}:53 (Error: {str(e)[:30]})")
        return False


def check_linux_dependencies():
    """Verifica que las dependencias opcionales estén instaladas en Linux"""
    if IS_WINDOWS:
        return {}

    deps = {}
    for cmd in LINUX_DEPS:
        result = subprocess.run(f"which {cmd}", shell=True, capture_output=True)
        deps[cmd] = result.returncode == 0

    return deps


def print_dependencies_warning(deps):
    """Imprime advertencia sobre dependencias faltantes en Linux"""
    if IS_WINDOWS:
        return

    missing = [cmd for cmd, installed in deps.items() if not installed]
    if missing:
        print("\n⚠️  ADVERTENCIA: Dependencias opcionales faltantes en Linux:")
        for cmd in missing:
            feature = LINUX_FEATURES.get(cmd, cmd)
            print(f"   - {cmd}: {feature}")
        print("   Instalar con: sudo apt install " + " ".join(missing))
        print()


# ==============================================================================
# FUNCIONES DE CONFIGURACIÓN
# ==============================================================================


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
        epilog="""
Ejemplos:
  %(prog)s                           # Ejecutar todos los tests
  %(prog)s --tests 1                 # Solo test de conectividad
  %(prog)s --tests 1,2,3             # Tests 1, 2 y 3
  %(prog)s --tests 1-5               # Tests del 1 al 5
  %(prog)s --tests internet          # Por nombre (equivale a test 2)
  %(prog)s --tests 2b                # Test de DNS configurados
  %(prog)s --tests 1-16              # Todos los tests disponibles
  %(prog)s --no-speed                # Omite test de velocidad
  %(prog)s --no-isp                  # Omite consulta al ISP
  %(prog)s -i                        # Menú interactivo
  %(prog)s --parallel                # Tests independientes en paralelo
  %(prog)s --format json -o out.json # Output en JSON
  %(prog)s --speed-size 10           # Test de velocidad con 10MB
  %(prog)s -v                         # Output detallado
  %(prog)s --version                 # Mostrar versión

Tests disponibles:
  1  - Conectividad local      | 9  - Firewall
  2  - Internet y DNS          | 10 - Traceroute
  2b - DNS configurados        | 11 - Velocidad internet
  3  - Puertos críticos        | 12 - DHCP
  4  - Latencia                | 13 - Bufferbloat (QoS)
  5  - WiFi                    | 14 - MTU
  6  - ISP                     | 15 - DNS alternativos
  7  - Pérdida de paquetes     | 16 - Conexiones simultáneas
  8  - Interfaz de red

Nombres alternativos: connectivity, internet, dns-configured, ports, latency,
                      wifi, isp, packet-loss, interface, firewall, traceroute,
                      speed, dhcp, simul-connections
""",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Abrir menú interactivo para seleccionar tests",
    )
    parser.add_argument(
        "--tests",
        metavar="TESTS",
        help="Tests a ejecutar (ej: 1,2,5-7 o internet,dns,wifi). "
        "Use números (1,2,3), rangos (1-5), o nombres (internet,latency)",
    )
    parser.add_argument(
        "--no-speed",
        action="store_true",
        help="Omitir test de velocidad (test 11)",
    )
    parser.add_argument(
        "--no-isp",
        action="store_true",
        help="Omitir consulta al ISP (test 6)",
    )
    parser.add_argument(
        "--format",
        choices=["txt", "json"],
        default="txt",
        metavar="{txt,json}",
        help="Formato de output (default: txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Archivo de output (default: automático)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Output detallado",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Mostrar versión del programa",
    )
    parser.add_argument(
        "--save-prefs",
        action="store_true",
        help="Guardar preferencias actuales como defecto",
    )
    parser.add_argument(
        "--speed-size",
        type=int,
        default=20,
        metavar="MB",
        help="Tamaño del test de velocidad en MB (default: 20)",
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

        # Manejo especial para "2b"
        if part.lower() == "2b":
            tests.add("2b")
            i += 1
            continue

        # Si ya es un número, usarlo directamente
        if part.isdigit():
            tests.add(part)
            i += 1
            continue

        # Verificar rango (ej: 5-7)
        if i + 1 < len(parts) and parts[i + 1].isdigit():
            start = TESTS_MAP.get(part, part)
            if isinstance(start, str) and start.lower() == "2b":
                start_num = 2
            elif isinstance(start, str) and start.isdigit():
                start_num = int(start)
            elif isinstance(start, int):
                start_num = start
            else:
                start_num = TESTS_MAP.get(start, part)
                if isinstance(start_num, str) and not start_num.isdigit():
                    start_num = 1
                else:
                    start_num = int(start_num)
            for n in range(start_num, int(parts[i + 1]) + 1):
                tests.add(str(n))
            i += 2
        else:
            # Test individual o nombre
            num = TESTS_MAP.get(part, part)
            if num.isdigit():
                tests.add(num)
            elif num in ("2b", "dns-configured"):
                tests.add("2b")
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

        if is_win and ("ipconfig" in command or "netsh" in command):
            result = subprocess.run(
                ["cmd", "/c", command],
                capture_output=True,
                timeout=10,
            )
        else:
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
    """Test ping a un host. Retorna (ok, latency_ms)"""
    is_win = platform.system().lower() == "windows"
    param = "-n" if is_win else "-c"
    command = f"ping {param} 4 {host}"

    print(f"\n🔍 Testing {name or host}...")

    latency = 0
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
                try:
                    for line in output.split("\n"):
                        line_lower = line.lower()
                        if "time=" in line_lower or "tiempo=" in line_lower:
                            for part in line.split():
                                if "time=" in part.lower() or "tiempo=" in part.lower():
                                    time_val = (
                                        part.split("=")[1]
                                        .replace("ms", "")
                                        .replace("tiempo=", "")
                                    )
                                    latency = float(time_val)
                                    break
                    if latency == 0 and lines:
                        line = lines[-1]
                        for part in line.split():
                            if "time=" in part.lower():
                                latency = float(part.split("=")[1].replace("ms", ""))
                except:
                    pass
            return True, latency
        else:
            print(f"   ❌ {name or host} - NO RESPONDE")
            return False, 0
    except:
        return False, 0


def test_dns(domain):
    """Test resolución DNS. Retorna (ok, ip, tiempo_ms)"""
    print(f"\n🔍 Resolviendo DNS: {domain}")
    start_time = time.time()
    try:
        ip = socket.gethostbyname(domain)
        elapsed_ms = (time.time() - start_time) * 1000
        print(f"   ✅ {domain} → {ip}")
        if elapsed_ms > 500:
            print(f"      ⚠️ Tiempo: {elapsed_ms:.0f}ms")
        return True, ip, elapsed_ms
    except:
        elapsed_ms = (time.time() - start_time) * 1000
        print(f"   ❌ No se pudo resolver {domain}")
        return False, None, elapsed_ms


def test_port(host, port, service_name=""):
    """Test si un puerto está abierto. Retorna True si abierto."""
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
        print(f"   ❌ Puerto {port} ({service_name}) ERROR")
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


def analyze_test_7(results):
    """Test 7: Pérdida de paquetes"""
    packet_results = results.get("packets", [])

    for pkt in packet_results:
        loss_pct = pkt.get("pct", 0)
        name = pkt.get("name", "Paquetes")

        if loss_pct > 20:
            suggest(
                "critical",
                "7",
                f"Pérdida {name}",
                f"Pérdida severa ({loss_pct}%)",
                "traceroute para identificar hop problemático",
                get_cmd("traceroute").format(
                    max_hops=30, host=pkt.get("host", "8.8.8.8")
                ),
            )
        elif loss_pct >= 5:
            suggest(
                "warning",
                "7",
                f"Pérdida {name}",
                f"Pérdida moderada ({loss_pct}%)",
                "Verificar router, línea ISP",
                "",
            )
        elif loss_pct > 0:
            suggest(
                "info",
                "7",
                f"Pérdida {name}",
                f"Pérdida leve ({loss_pct}%)",
                "Normal en horas pico",
                "",
            )


def get_network_interface_details():
    """Obtiene detalles del interfaz de red"""
    import platform
    import subprocess
    import os

    is_windows = platform.system().lower() == "windows"
    details = {}

    if is_windows:
        try:
            pwsh_paths = [
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                r"C:\Program Files\PowerShell\7\pwsh.exe",
                "powershell.exe",
            ]
            pwsh_cmd = None
            for p in pwsh_paths:
                if os.path.exists(p) if "\\" in p or p == "powershell.exe" else True:
                    pwsh_cmd = p
                    break

            if not pwsh_cmd:
                pwsh_cmd = "powershell.exe"

            cmd = f'{pwsh_cmd} -Command "Get-NetAdapter | Where-Object Status -eq Up | Select-Object Name, InterfaceDescription, Status, MacAddress, LinkSpeed, FullDuplex | ConvertTo-Json"'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=15,
            )
            stdout = result.stdout.decode("utf-8", errors="replace")
            stderr = result.stderr.decode("utf-8", errors="replace")
            output = stdout
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
                details["Duplex"] = "Full" if data.get("FullDuplex", False) else "Half"
        except Exception as e:
            pass
    return details


def get_firewall_status():
    """Obtiene estado del firewall"""
    is_windows = platform.system().lower() == "windows"
    firewall_info = {}

    if is_windows:
        output = run_command("netsh advfirewall show allprofiles")
        for line in output.split("\n"):
            line_lower = line.lower()
            if "perfil de dominio" in line_lower or "domain" in line_lower:
                firewall_info["Dominio"] = "ON"
            elif "perfil privado" in line_lower or "private" in line_lower:
                firewall_info["Privado"] = "ON"
            elif "perfil público" in line_lower or "public" in line_lower:
                firewall_info["Publico"] = "ON"

        output = run_command("netsh advfirewall show rule name=all")
        reglas_count = len([l for l in output.split("\n") if "Regla" in l])
        firewall_info["Reglas activas"] = str(reglas_count)
    else:
        firewall_info["UFW"] = "N/A"
        firewall_info["iptables"] = "N/A"

    return firewall_info


def get_dhcp_lease_info():
    """Obtiene información del lease DHCP por cada interfaz de red"""
    import platform
    import subprocess

    is_windows = platform.system().lower() == "windows"
    lease_info = {}

    if is_windows:
        output = run_command("ipconfig /all")

        if not output or len(output) < 10:
            result = subprocess.run(
                ["C:\\Windows\\System32\\ipconfig", "/all"],
                capture_output=True,
                timeout=10,
            )
            output = result.stdout.decode("cp437", errors="replace")

        current_adapter = None
        adapter_data = {}
        skip_next = False

        for line in output.split("\n"):
            line_stripped = line.strip()
            line_lower = line_stripped.lower()

            if skip_next:
                skip_next = False
                continue

            if (
                line_lower.startswith("adaptador")
                or line_lower.startswith("adapter")
                or line_lower.startswith("ethernet")
                or line_lower.startswith("wireless")
            ):
                if current_adapter and adapter_data:
                    lease_info[current_adapter] = adapter_data
                current_adapter = line_stripped.split(":")[0].strip()
                if (
                    len(line_stripped.split(":")) > 1
                    and line_stripped.split(":", 1)[1].strip()
                ):
                    adapter_name = line_stripped.split(":", 1)[1].strip()
                    current_adapter = (
                        f"{line_stripped.split(':')[0].strip()}: {adapter_name}"
                    )
                adapter_data = {
                    "DHCP": "N/A",
                    "IP": "",
                    "Máscara": "",
                    "Gateway": "",
                    "DNS": "",
                }
                skip_next = True
                continue

            if current_adapter:
                if "dhcp habilitado" in line_lower or "dhcp enabled" in line_lower:
                    if (
                        " sí" in line_lower
                        or " yes" in line_lower
                        or "s" in line.split(":")[-1].strip()
                    ):
                        adapter_data["DHCP"] = "Habilitado"
                    else:
                        adapter_data["DHCP"] = "Deshabilitado (IP Estática)"

                if " ipv4" in line_lower and ":" in line_stripped:
                    ip_val = line_stripped.split(":")[1].strip()
                    if "(preferido)" in ip_val.lower():
                        ip_val = (
                            ip_val.lower()
                            .replace("(preferido)", "")
                            .strip()
                            .replace("  ", " ")
                        )
                    if ip_val:
                        adapter_data["IP"] = ip_val

                if " subred" in line_lower or " mascar" in line_lower:
                    if ":" in line_stripped:
                        mask = line_stripped.split(":")[1].strip()
                        if mask:
                            adapter_data["Máscara"] = mask

                if " gateway" in line_lower or " puerta" in line_lower:
                    if ":" in line_stripped:
                        gw = line_stripped.split(":")[1].strip()
                        if gw:
                            adapter_data["Gateway"] = gw

                if " dhcp server" in line_lower:
                    if ":" in line_stripped:
                        dhcp_server = line_stripped.split(":")[1].strip()
                        if dhcp_server:
                            adapter_data["Servidor DHCP"] = dhcp_server

                if (
                    "lease obtained" in line_lower
                    or "conexión obtained" in line_lower
                    or "concesión obtenida" in line_lower
                ):
                    if ":" in line_stripped:
                        lease_obtained = line_stripped.split(":")[1].strip()
                        if lease_obtained:
                            adapter_data["Lease Obtenido"] = lease_obtained

                if (
                    "lease expires" in line_lower
                    or "conexión expires" in line_lower
                    or "conexión expira" in line_lower
                ):
                    if ":" in line_stripped:
                        lease_expires = line_stripped.split(":")[1].strip()
                        if lease_expires:
                            adapter_data["Lease Expira"] = lease_expires

                if " dns servers" in line_lower:
                    if ":" in line_stripped:
                        dns = line_stripped.split(":")[1].strip()
                        if dns:
                            adapter_data["DNS"] = dns

        if current_adapter and adapter_data:
            lease_info[current_adapter] = adapter_data

    if not lease_info:
        lease_info["Sin información"] = {
            "DHCP": "No disponible",
            "IP": "",
            "Máscara": "",
            "Gateway": "",
            "DNS": "",
        }

    return lease_info


def analyze_test_8(results):
    """Test 8: Interfaz de red"""
    iface = results.get("interface_details", {})
    estado = iface.get("Estado", "").lower()

    if estado and estado != "up":
        suggest(
            "critical",
            "8",
            "Interfaz de Red",
            f"Interfaz caído ({estado})",
            "Habilitar interfaz",
            get_cmd("interface_set").format(name="Ethernet"),
        )

    velocidad = iface.get("Velocidad", "")
    if velocidad:
        speed_gbps = 0
        try:
            speed_gbps = int(velocidad.replace("Gbps", "").replace("Mbps", ""))
        except:
            pass
        if speed_gbps < 1:
            suggest(
                "info",
                "8",
                "Interfaz de Red",
                f"Velocidad link baja ({velocidad})",
                "Verificar cable o comparar con plan contratado",
                "",
            )

    # DetectHalf duplex
    duplex = iface.get("Duplex", "").lower()
    if duplex == "half":
        suggest(
            "warning",
            "8",
            "Interfaz de Red",
            "Half-duplex detectado",
            "Configurar full-duplex en el switch/router para mejor rendimiento",
            "",
        )


def analyze_test_9(results):
    """Test 9: Firewall"""
    fw = results.get("firewall_info", {})

    profiles = ["Dominio", "Privado", "Publico"]
    all_off = all(fw.get(p, "").lower() != "on" for p in profiles)

    if all_off:
        suggest(
            "warning",
            "9",
            "Firewall",
            "Todos los perfiles desactivados",
            "Considerar activar firewall",
            get_cmd("firewall_profiles").replace("show", "set allprofiles state on")
            if IS_WINDOWS
            else "sudo ufw enable",
        )


def analyze_test_10(results):
    """Test 10: Traceroute"""
    routes = results.get("routes", [])

    for route_name, hops in routes:
        if not hops:
            continue

        # Detectar timeouts
        if isinstance(hops[0], dict):
            timeouts = sum(1 for h in hops if h.get("latency", 0) == 0)
        else:
            timeouts = sum(1 for h in hops if "*" in h)

        if timeouts > 5:
            suggest(
                "warning",
                "10",
                f"Traceroute {route_name}",
                f"{timeouts} hops con timeout",
                "Ruta degradada, verificar conexión",
                "",
            )

        # Detectar aumento brusco de latencia (>50ms entre hops)
        if isinstance(hops[0], dict):
            for i in range(1, len(hops)):
                prev_lat = hops[i - 1].get("latency", 0)
                curr_lat = hops[i].get("latency", 0)
                if prev_lat > 0 and curr_lat > 0:
                    diff = curr_lat - prev_lat
                    if diff > 50:
                        suggest(
                            "warning",
                            "10",
                            f"Traceroute {route_name}",
                            f"Congestión en hop {i + 1} (+{diff:.0f}ms)",
                            "Verificar ISP de ese salto",
                            "",
                        )
                        break


def analyze_test_11(results):
    """Test 11: Velocidad"""
    dl = results.get("download", 0)
    ul = results.get("upload", 0)

    if dl > 0 and dl < 1:
        suggest(
            "critical",
            "11",
            "Velocidad Download",
            f"Velocidad muy baja ({dl} Mbps)",
            "Verificar línea; llamar ISP",
            "",
        )
    elif dl > 0 and dl < 10:
        suggest(
            "warning",
            "11",
            "Velocidad Download",
            f"Velocidad baja ({dl} Mbps)",
            "Verificar plan o congestión",
            "",
        )

    if ul > 0 and ul < 0.5:
        suggest(
            "warning",
            "11",
            "Velocidad Upload",
            f"Upload muy bajo ({ul} Mbps)",
            "Verificar QoS del ISP",
            "",
        )


def analyze_test_12(results):
    """Test 12: DHCP"""
    dhcp = results.get("dhcp_info", {})

    for adapter_name, adapter_data in dhcp.items():
        if adapter_name == "Sin información":
            continue

        dhcp_status = adapter_data.get("DHCP", "")

        if dhcp_status and "Deshabilitado" in dhcp_status:
            suggest(
                "info",
                "12",
                f"DHCP ({adapter_name})",
                "IP Estática",
                "Normal si es configuración intencional",
                "",
            )


def run_test_by_id(test_id, args, is_windows):
    """Ejecuta un test específico y retorna sus resultados"""
    results = {}

    if test_id == "1":
        loopback_ok, _ = test_ping("127.0.0.1", "Loopback (Interno)")

        gateway = None
        local_ip = None
        if is_windows:
            output = run_command("ipconfig")
            for line in output.split("\n"):
                if "dirección ipv4" in line.lower() or "ipv4 address" in line.lower():
                    if ":" in line:
                        local_ip = line.split(":")[1].strip()
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
            output = run_command("ip addr show")
            for line in output.split("\n"):
                if "inet " in line and "127." not in line:
                    local_ip = line.strip().split()[1].split("/")[0]

        gateway_ok = False
        gateway_latency = 0
        if gateway:
            gateway_ok, gateway_latency = test_ping(gateway, f"Gateway ({gateway})")

        results = {
            "gateway": gateway,
            "local_ip": local_ip,
            "loopback_ok": loopback_ok,
            "gateway_ok": gateway_ok,
            "gateway_latency": gateway_latency,
        }
        analyze_test_1(results)

    elif test_id == "2":
        internet_ok = test_ping("8.8.8.8", "Google DNS")
        dns_ok, dns_ip, dns_time = test_dns("google.com")
        results = {"internet_ok": internet_ok, "dns_ok": dns_ok, "dns_time": dns_time}
        analyze_test_2(results)

    elif test_id == "2b":
        dns_servers = get_configured_dns()
        dns_open = {}
        for dns in dns_servers:
            dns_open[dns] = test_dns_verification(dns)
        results = {"dns_servers": dns_servers, "dns_open": dns_open}
        analyze_test_2b(results)

    elif test_id == "3":
        port_443 = test_port("google.com", 443, "HTTPS")
        port_53 = test_port("8.8.8.8", 53, "DNS")
        results = {"port_443": port_443, "port_53": port_53}
        analyze_test_3(results)

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

    # Iniciar captura de output para archivo idéntico
    start_capture()

    # Si no hay tests seleccionados (compatibilidad atrás), ejecutar todos
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

    # Trackear tests ejecutados
    executed_tests = set()

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
        executed_tests.add("1")
        print_header("TEST 1: CONECTIVIDAD LOCAL")
        loopback_ok, _ = test_ping("127.0.0.1", "Loopback (Interno)")

        gateway = None
        local_ip = None
        if is_windows:
            output = run_command("ipconfig")
            for line in output.split("\n"):
                if "dirección ipv4" in line.lower() or "ipv4 address" in line.lower():
                    if ":" in line:
                        local_ip = line.split(":")[1].strip()
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
            output = run_command("ip addr show")
            for line in output.split("\n"):
                if "inet " in line and "127." not in line:
                    local_ip = line.strip().split()[1].split("/")[0]

        gateway_ok = False
        gateway_latency = 0
        if gateway:
            print(f"\n📍 Gateway detectado: {gateway}")
            gateway_ok, gateway_latency = test_ping(gateway, f"Gateway ({gateway})")
            analyze_test_1(
                {
                    "gateway": gateway,
                    "local_ip": local_ip,
                    "loopback_ok": loopback_ok,
                    "gateway_ok": gateway_ok,
                    "gateway_latency": gateway_latency,
                }
            )
        else:
            print("\n⚠️ No se detectó Gateway automáticamente.")
            analyze_test_1(
                {
                    "gateway": None,
                    "local_ip": local_ip,
                    "loopback_ok": loopback_ok,
                    "gateway_ok": False,
                    "gateway_latency": 0,
                }
            )

    # Test 2: Internet y DNS
    if "2" in selected_tests:
        executed_tests.add("2")
        print_header("TEST 2: INTERNET Y DNS")

        internet_ok, _ = test_ping("8.8.8.8", "Google DNS")
        dns_ok, dns_ip, dns_time = test_dns("google.com")
        analyze_test_2(
            {"internet_ok": internet_ok, "dns_ok": dns_ok, "dns_time": dns_time}
        )

    # Test 2B: DNS configurados
    if "2b" in selected_tests:
        executed_tests.add("2b")
        print_header("TEST 2B: SERVIDORES DNS CONFIGURADOS")
        dns_servers = get_configured_dns()
        dns_open = {}
        if dns_servers:
            print(f"   📋 Servidores DNS configurados ({len(dns_servers)}):")
            for dns in dns_servers:
                print(f"      - {dns}")
                dns_open[dns] = test_dns_verification(dns)
        else:
            print("   ⚠️ No se detectaron servidores DNS configurados")
        analyze_test_2b({"dns_servers": dns_servers, "dns_open": dns_open})

    # Test 3: Puertos
    if "3" in selected_tests:
        executed_tests.add("3")
        print_header("TEST 3: PUERTOS CRÍTICOS")
        port_443 = test_port("google.com", 443, "HTTPS")
        port_53 = test_port("8.8.8.8", 53, "DNS")
        analyze_test_3({"port_443": port_443, "port_53": port_53})

    # Test 4: Latencia
    if "4" in selected_tests:
        executed_tests.add("4")
        print_header("TEST 4: ESTADÍSTICAS DE LATENCIA")
        targets = [("8.8.8.8", "Google"), ("1.1.1.1", "Cloudflare")]
        latency_results = []
        for ip, name in targets:
            print(f"\n📡 {name}:")
            lat = test_latency_target(ip, name, 5)
            latency_results.append(lat)
            if lat.get("ok"):
                print(
                    f"   min={lat['min']}ms, max={lat['max']}ms, avg={lat['avg']}ms, jitter={lat['jitter']}ms"
                )
            else:
                print(f"   ❌ Error al medir latencia")

        analyze_test_4({"latency": latency_results})

    # Test 5: WiFi
    if "5" in selected_tests:
        executed_tests.add("5")
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

        analyze_test_5({"conn_type": conn_type, "wifi_info": wifi_info or {}})

    # Test 6: ISP
    if "6" in selected_tests and not args.no_isp:
        executed_tests.add("6")
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

        analyze_test_6({"isp_info": isp_info or {}})

    # Test 7: Pérdida de paquetes
    if "7" in selected_tests:
        executed_tests.add("7")
        print_header("TEST 7: PÉRDIDA DE PAQUETES")
        hosts = [("8.8.8.8", "Google DNS"), ("1.1.1.1", "Cloudflare")]
        packet_loss_results = []
        packets_list = []

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

                pct = 0
                try:
                    pct_str = packet_info.get("% perda", "0%").replace("%", "")
                    pct = float(pct_str)
                except:
                    pass
                packets_list.append(
                    {"host": host, "name": name, "pct": pct, "info": packet_info}
                )
            else:
                print(f"   ⚠️ No se pudo obtener información de {name}")
                packet_loss_results.append((name, None))

        analyze_test_7({"packets": packets_list})

    # Test 8: Interfaz de red
    if "8" in selected_tests:
        executed_tests.add("8")
        print_header("TEST 8: DETALLES DEL INTERFAZ DE RED")
        interface_details = get_network_interface_details()
        if interface_details:
            print(f"   📡 Información del interfaz de red:")
            for key, value in interface_details.items():
                print(f"      {key}: {value}")
            analyze_test_8({"interface_details": interface_details})
        else:
            print("   ⚠️ No se pudo obtener información del interfaz")

    # Test 9: Firewall
    if "9" in selected_tests:
        executed_tests.add("9")
        print_header("TEST 9: ESTADO DEL FIREWALL")
        firewall_info = get_firewall_status()
        if firewall_info:
            print(f"   🔥 Estado del firewall:")
            for key, value in firewall_info.items():
                print(f"      {key}: {value}")
            analyze_test_9({"firewall_info": firewall_info})
        else:
            print("   ⚠️ No se pudo obtener información del firewall")

    # Test 10: Traceroute
    if "10" in selected_tests:
        executed_tests.add("10")
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

        analyze_test_10({"routes": traceroute_results})

    # Test 11: Velocidad (simplificado con fallback automático)
    if "11" in selected_tests and not args.no_speed:
        executed_tests.add("11")
        speed_size = args.speed_size if args.speed_size else 20

        print_header("TEST 11: VELOCIDAD DE INTERNET")
        speed_results = test_internet_speed(speed_size)

        dl = 0
        ul = 0
        if speed_results.get("download") or speed_results.get("upload"):
            print("\n   📊 Resumen:")
            if speed_results.get("download"):
                name, speed, elapsed = speed_results["download"][0]
                dl = speed
                print(f"      Download ({name}): {speed:.1f} Mbps")
            if speed_results.get("upload"):
                name, speed, elapsed = speed_results["upload"][0]
                ul = speed
                print(f"      Upload ({name}): {speed:.1f} Mbps")
            analyze_test_11({"download": dl, "upload": ul})
        else:
            print("   ⚠️ No se pudo obtener información de velocidad")

    # Test 12: DHCP
    if "12" in selected_tests:
        executed_tests.add("12")
        print_header("TEST 12: INFORMACIÓN DHCP")
        dhcp_info = get_dhcp_lease_info()
        if dhcp_info:
            print(f"   📋 Información del lease DHCP:")
            for adapter_name, adapter_data in dhcp_info.items():
                if adapter_name == "Sin información":
                    print(f"      ⚠️ No se pudo obtener información DHCP")
                    continue
                has_ip = bool(adapter_data.get("IP", "").strip())
                if not has_ip:
                    continue
                print(f"   📺 {adapter_name}:")
                for key, value in adapter_data.items():
                    if value:
                        print(f"      {key}: {value}")
            analyze_test_12({"dhcp_info": dhcp_info})
        else:
            print("   ⚠️ No se pudo obtener información DHCP")

    # Test 13: Bufferbloat (QoS)
    if "13" in selected_tests:
        executed_tests.add("13")
        print_header("TEST 13: BUFFERBLOAT (QoS)")
        bb_result = test_bufferbloat()
        analyze_bufferbloat(bb_result)

    # Test 14: MTU
    if "14" in selected_tests:
        executed_tests.add("14")
        print_header("TEST 14: MTU")
        mtu_result = test_mtu()
        analyze_mtu(mtu_result)

    # Test 15: DNS Alternativos
    if "15" in selected_tests:
        executed_tests.add("15")
        print_header("TEST 15: DNS ALTERNATIVOS")
        dns_result = test_dns_alternatives()
        analyze_dns_alternatives(dns_result)

    # Test 16: Conexiones Simultáneas
    if "16" in selected_tests:
        executed_tests.add("16")
        print_header("TEST 16: CONEXIONES SIMULTÁNEAS")
        simul_result = test_simultaneous_connections()
        analyze_simul_connections(simul_result)

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

    # Mostrar sugerencias de troubleshooting ANTES de guardar (para que se capturen)
    print(f"\n💾 Resultados guardados en: {nombre_archivo}")
    print_all_suggestions()

    # ========== PIE DE PÁGINA ==========
    print("\n" + "=" * 60)
    print("Diagnóstico completado")
    print(f"Autor: Xabier Pereira - Modificado por Ignacio Peroni")
    print("github.com/xabierpereira |  github.com/iperoni")
    print("=" * 60)

    # GUARDAR RESULTADOS (ahora sí incluye sugerencias y pie)
    end_capture(ruta_archivo)


# ==============================================================================
# TEST de BUFFERBLOAT (QoS) - Mejora Pendiente
# ==============================================================================


def measure_ping(host="8.8.8.8"):
    """Medir latencia simple (retorna ms)"""
    is_windows = platform.system().lower() == "windows"
    param = "-n" if is_windows else "-c"

    try:
        result = subprocess.run(
            f"ping {param} 1 {host}",
            shell=True,
            capture_output=True,
            timeout=5,
        )
        output = result.stdout.decode(
            "cp437" if is_windows else "utf-8", errors="replace"
        )

        for word in output.split():
            word_lower = word.lower()
            if "time=" in word_lower or "tiempo=" in word_lower:
                ms = word.split("=")[-1].replace("ms", "").replace("TTL", "").strip()
                return float(ms)
    except:
        pass
    return None


def test_bufferbloat():
    """Test de Bufferbloat (QoS)"""
    results = {}

    # 1. Medir latencia base (sin carga)
    print(" Mediendo latencia base...")
    base_samples = []
    for i in range(5):
        lat = measure_ping("8.8.8.8")
        if lat:
            base_samples.append(lat)
        time.sleep(0.5)

    if not base_samples:
        print(" No se pudo medir latencia base")
        return {"error": True}

    results["base_latency"] = sum(base_samples) / len(base_samples)

    # 2. Iniciar download en background
    print(" Midiendo latencia bajo carga...")
    download_proc = subprocess.Popen(
        'curl -L -k -s -o NUL "https://speed.cloudflare.com/__down?bytes=50000000"',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    time.sleep(2)

    # 3. Medir latencia durante descarga
    load_samples = []
    for i in range(10):
        lat = measure_ping("8.8.8.8")
        if lat:
            load_samples.append(lat)
        time.sleep(0.3)

    download_proc.wait(timeout=60)

    if not load_samples:
        print(" No se pudo medir latencia bajo carga")
        return {"error": True}

    results["load_latency"] = sum(load_samples) / len(load_samples)
    results["bloat"] = results["load_latency"] - results["base_latency"]

    print(f"   Base: {results['base_latency']:.1f}ms")
    print(f"   Carga: {results['load_latency']:.1f}ms")
    print(f"   Bufferbloat: {results['bloat']:.1f}ms")

    return results


def analyze_bufferbloat(results):
    """Analizar resultados del test de Bufferbloat"""
    if results.get("error"):
        return

    bloat = results.get("bloat", 0)

    if bloat > 100:
        suggest(
            "critical",
            "qos",
            "Bufferbloat Severo",
            f"+{bloat:.0f}ms bajo carga",
            "Configurar QoS/SQM en el router. Usar Cake o fq_codel.",
            "",
        )
    elif bloat > 50:
        suggest(
            "warning",
            "qos",
            "Bufferbloat Moderado",
            f"+{bloat:.0f}ms bajo carga",
            "Verificar configuración QoS del router",
            "",
        )
    elif bloat > 20:
        suggest(
            "info",
            "qos",
            "Bufferbloat Leve",
            f"+{bloat:.0f}ms bajo carga",
            "Aceptable para mayoría de usos",
            "",
        )


# ==============================================================================
# TEST DE MTU (Mejora 3)
# ==============================================================================


def parse_tracepath(output):
    """Extraer IPs de tracepath/tracert"""
    ips = []
    for line in output.split("\n"):
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
        if match:
            ips.append(match.group(1))
    return ips


def test_mtu(host="8.8.8.8"):
    """Test de MTU - fragmentación"""
    is_windows = platform.system().lower() == "windows"
    results = {}

    test_sizes = [1472, 1400, 1300, 1200]

    for size in test_sizes:
        if is_windows:
            cmd = f"ping -n 1 -f -l {size} {host}"
        else:
            cmd = f"ping -M do -s {size} -c 1 {host}"

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            output = result.stdout.decode(
                "cp437" if is_windows else "utf-8", errors="replace"
            )

            if "packets need to be fragmented" in output.lower():
                results[size] = False
            else:
                results[size] = True
                print(f"   {size + 28} bytes: OK")
        except:
            results[size] = False

        time.sleep(0.5)

    working = [k for k, v in results.items() if v]
    max_mtu = (max(working) + 28) if working else 0

    print(f"   MTU máximo: {max_mtu} bytes")

    # Parte 2: tracepath
    print("   Analizando ruta...")
    cmd = f"tracert -d -h 30 {host}" if is_windows else f"tracepath -n {host}"

    path_ips = []
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
        output = result.stdout.decode(
            "cp437" if is_windows else "utf-8", errors="replace"
        )
        path_ips = parse_tracepath(output)
        print(f"   Ruta: {len(path_ips)} saltos")
        for ip in path_ips[:5]:
            print(f"      {ip}")
    except Exception as e:
        print("   Ruta: Error al obtener")

    return {"mtu": max_mtu, "details": results, "path": path_ips}


def analyze_mtu(results):
    """Analizar resultados MTU"""
    mtu = results.get("mtu", 0)
    path = results.get("path", [])

    if mtu == 0:
        suggest(
            "critical",
            "mtu",
            "MTU Fallo",
            "No se pudo determinar MTU",
            "Verificar conectividad a Internet",
            "",
        )
        return

    if mtu == 1500:
        suggest(
            "info",
            "mtu",
            "MTU Óptimo",
            f"MTU = {mtu} bytes - sin fragmentación",
            "",
            "",
        )
        return

    if mtu > 1500:
        suggest(
            "warning",
            "mtu",
            "MTU Alto",
            f"MTU = {mtu} bytes (puede causar fragmentación)",
            "Verificar configuración del router",
            "",
        )
        return

    if mtu <= 1280:
        suggest(
            "warning",
            "mtu",
            "MTU Muy Bajo",
            f"MTU = {mtu} bytes",
            "Posible VPN o tunnel activo. Verificar configuración",
            "",
        )
        return

    if mtu > 1280 and mtu < 1500:
        suggest(
            "info",
            "mtu",
            "MTU Subóptimo",
            f"MTU = {mtu} bytes",
            "MTU reducido. Verificar router o ISP",
            "",
        )
        return

    if not path:
        suggest(
            "warning",
            "mtu",
            "Ruta No Disponible",
            "No se pudo analizar la ruta",
            "Verificar conectividad",
            "",
        )


# ==============================================================================
# TEST DE DNS ALTERNATIVOS (Mejora 5)
# ==============================================================================


def test_dns_speed(dns_ip):
    """Medir tiempo de respuesta de un DNS"""
    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((dns_ip, 53))
        sock.close()
        return (time.time() - start) * 1000
    except:
        return None


def test_dns_alternatives():
    """Test de servidores DNS alternativos vs configurados"""
    dns_servers = [
        ("1.1.1.1", "Cloudflare"),
        ("8.8.8.8", "Google"),
        ("9.9.9.9", "Quad9"),
        ("208.67.222.222", "OpenDNS"),
    ]

    results = []
    configured_results = []

    # Obtener DNS configurados
    configured_dns = get_configured_dns()
    print("\n   DNS configurados:")
    for dns in configured_dns:
        t = test_dns_speed(dns)
        if t:
            print(f"      {dns}: {t:.0f}ms")
            configured_results.append((dns, "Configurado", t))
        else:
            print(f"      {dns}: ERROR")

    print("\n   DNS alternativos:")
    for dns_ip, provider in dns_servers:
        elapsed = test_dns_speed(dns_ip)
        if elapsed:
            results.append((dns_ip, provider, elapsed, True))
            print(f"   {provider} ({dns_ip}): {elapsed:.0f}ms")
        else:
            results.append((dns_ip, provider, 0, False))
            print(f"   {provider} ({dns_ip}): NO DISPONIBLE")

    # Comparar mejor alternativo con mejor configurado
    working_alt = [(ip, name, t) for ip, name, t, ok in results if ok]
    working_cfg = [
        (ip, name, t) for ip, name, t in configured_results if t is not None and t > 0
    ]

    comparison = {}
    if working_alt and working_cfg:
        best_alt = min(working_alt, key=lambda x: x[2])
        best_cfg = min(working_cfg, key=lambda x: x[2])
        diff = best_cfg[2] - best_alt[2]
        comparison = {
            "best_alt": best_alt,
            "best_cfg": best_cfg,
            "difference": diff,
        }

    return {
        "dns_results": results,
        "configured_results": configured_results,
        "comparison": comparison,
    }


def analyze_dns_alternatives(results):
    """Analizar resultados de DNS alternativos"""
    dns_list = results.get("dns_results", [])
    comparison = results.get("comparison", {})
    configured_results = results.get("configured_results", [])

    working = [(ip, name, t) for ip, name, t, ok in dns_list if ok]

    if not working and not configured_results:
        suggest(
            "warning",
            "dns_alt",
            "DNS Alternativos",
            "Ningún DNS funciona",
            "Verificar conectividad",
            "",
        )
        return

    if comparison and comparison.get("difference", 0) > 10:
        best_alt = comparison["best_alt"]
        best_cfg = comparison["best_cfg"]
        diff = comparison["difference"]

        suggest(
            "success",
            "dns_alt",
            "DNS Más Rápido Disponible",
            f"{best_alt[1]} ({best_alt[0]}) es {diff:.0f}ms más rápido",
            f"Cambiar de {best_cfg[0]} a {best_alt[0]}",
            f'netsh interface ip set dns name="Wi-Fi" static {best_alt[0]}',
        )
        return

    if comparison:
        best_cfg = comparison["best_cfg"]
        suggest(
            "success",
            "dns_alt",
            "DNS Óptimos",
            f"Tus DNS configurados ({best_cfg[0]}) son buenos",
            "No es necesario cambiarlos",
            "",
        )
        return

    working.sort(key=lambda x: x[2])

    best = working[0]

    if best[2] > 100:
        suggest(
            "info",
            "dns_alt",
            "DNS Lento",
            f"Mejor DNS: {best[1]} ({best[0]}) - {best[2]:.0f}ms",
            f"Considerar usar: {best[0]}",
            "",
        )


# ==============================================================================
# TEST DE CONEXIONES SIMULTÁNEAS (Test 16)
# ==============================================================================


def test_tcp_connection(host, port, timeout=5):
    """Probar conexión TCP a un servidor"""
    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return {"success": True, "time": (time.time() - start) * 1000}
    except Exception as e:
        return {"success": False, "time": None, "error": str(e)}


def test_http_download(url, timeout=15):
    """Descargar archivo pequeño vía HTTP"""
    start = time.time()
    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "NetworkDiagnostic/1.0")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read(1024 * 500)  # Leer hasta 500KB
            elapsed = time.time() - start
            bytes_received = len(data)
            return {
                "success": True,
                "time": elapsed * 1000,
                "bytes": bytes_received,
                "speed_mbps": (bytes_received * 8) / (elapsed * 1_000_000)
                if elapsed > 0
                else 0,
            }
    except Exception as e:
        return {"success": False, "time": None, "error": str(e)}


def test_simultaneous_connections():
    """Test de conexiones simultáneas TCP + HTTP"""
    print("\n   Probando conexiones TCP simultáneas...")

    tcp_servers = [
        ("8.8.8.8", 443, "Google"),
        ("1.1.1.1", 443, "Cloudflare"),
        ("9.9.9.9", 443, "Quad9"),
    ]

    tcp_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            name: executor.submit(test_tcp_connection, host, port)
            for host, port, name in tcp_servers
        }
        for name, future in futures.items():
            result = future.result()
            tcp_results.append((name, result))
            if result["success"]:
                print(f"      {name}: {result['time']:.0f}ms")
            else:
                print(f"      {name}: FALLO")

    print("\n   Probando descargas HTTP concurrentes...")
    http_urls = [
        ("https://speed.cloudflare.com/__down?bytes=5000000", "Cloudflare"),
        ("https://httpbin.org/stream-bytes/5000000", "HTTPBin"),
    ]

    http_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            name: executor.submit(test_http_download, url) for url, name in http_urls
        }
        for name, future in futures.items():
            result = future.result()
            http_results.append((name, result))
            if result["success"]:
                print(
                    f"      {name}: {result['speed_mbps']:.1f} Mbps ({result['bytes']} bytes)"
                )
            else:
                print(f"      {name}: FALLO")

    return {
        "tcp_results": tcp_results,
        "http_results": http_results,
    }


def analyze_simul_connections(results):
    """Analizar resultados de conexiones simultáneas"""
    tcp_results = results.get("tcp_results", [])
    http_results = results.get("http_results", [])

    tcp_success = sum(1 for _, r in tcp_results if r.get("success", False))
    http_success = sum(1 for _, r in http_results if r.get("success", False))
    total_tcp = len(tcp_results)

    if tcp_success == 0 and http_success == 0:
        suggest(
            "warning",
            "simul",
            "Conexiones Simultáneas",
            "Todas las conexiones fallaron",
            "Verificar conectividad a Internet",
            "",
        )
        return

    if tcp_success < total_tcp * 0.5:
        suggest(
            "warning",
            "simul",
            "Conexiones TCP Lentas",
            f"Solo {tcp_success}/{total_tcp} conexiones TCP exitosas",
            "Verificar latencia y límites del ISP",
            "",
        )
        return

    if tcp_success == total_tcp:
        tcp_times = [r["time"] for _, r in tcp_results if r.get("success")]
        avg_tcp = sum(tcp_times) / len(tcp_times) if tcp_times else 0
        print(f"\n   📊 TCP promedio: {avg_tcp:.0f}ms")

    if http_success > 0:
        speeds = [r["speed_mbps"] for _, r in http_results if r.get("success")]
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            print(f"   📊 HTTP concurrente promedio: {avg_speed:.1f} Mbps")
    else:
        suggest(
            "info",
            "simul",
            "Conexiones Múltiples",
            f"{tcp_success}/{total_tcp} conexiones TCP OK",
            "Descarga HTTP no disponible",
            "",
        )
        return

    suggest(
        "info",
        "simul",
        "Conexiones Múltiples",
        f"{tcp_success} TCP, {http_success} HTTP concurrentes OK",
        "La conexión maneja bien múltiples conexiones",
        "",
    )


if __name__ == "__main__":
    main()
