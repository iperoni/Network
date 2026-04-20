#!/usr/bin/env python3
"""
Network Diagnostic Tool (v0.4)
Diagnóstico completo de conectividad de red mejorado para Windows/Linux

Autor: Xabier Pereira - Modificado por Ignacio Peroni
"""

import socket
import subprocess
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

        # RESULTADO FINAL
        f.write("\n" + "=" * 60 + "\n")
        f.write("   RESULTADO FINAL\n")
        f.write("=" * 60 + "\n")
        f.write(f"Estado: {status}\n")
        f.write(f"Puntuación: {puntos}/3\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write(f"Autor: Xabier Pereira\n")
        f.write("=" * 60 + "\n")

    print(f"\n💾 Resultados guardados en: {nombre_archivo}")

    # ========== PIE DE PÁGINA ==========
    print("\n" + "=" * 60)
    print("Diagnóstico completado")
    print(f"Autor: Xabier Pereira - Modificado por Ignacio Peroni | github.com/xabierpereira")
    print("=" * 60)


if __name__ == "__main__":
    main()
