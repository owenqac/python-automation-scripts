#!/usr/bin/env python3
"""Escáner TCP de la red local. Solo para redes propias o con permiso explícito."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass

SERVICIOS: dict[int, str] = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    139: "netbios",
    143: "imap",
    443: "https",
    445: "smb",
    1433: "mssql",
    3306: "mysql",
    3389: "rdp",
    5432: "postgresql",
    5900: "vnc",
    6379: "redis",
    8080: "http-alt",
    8443: "https-alt",
    27017: "mongodb",
}

PUERTOS_POR_DEFECTO = "21,22,23,25,53,80,110,139,143,443,445,1433,3306,3389,5432,5900,6379,8080,8443,27017"
MAX_HOSTS = 1024


@dataclass
class Resultado:
    ip: str
    puerto: int
    servicio: str
    banner: str


def obtener_ip_local() -> str:
    try:
        salida = subprocess.run(
            ["ip", "-4", "-o", "addr", "show", "scope", "global"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        raise RuntimeError("No se pudo obtener la IP local (¿está instalado el comando 'ip'?)")

    for linea in salida.splitlines():
        coincidencia = re.search(r"inet (\d+\.\d+\.\d+\.\d+/\d+)", linea)
        if not coincidencia:
            continue
        interfaz = ipaddress.ip_interface(coincidencia.group(1))
        if interfaz.ip.is_private:
            return str(interfaz.ip)
    raise RuntimeError("No se encontró una IP privada en este equipo.")


def parsear_puertos(texto: str) -> list[int]:
    puertos: set[int] = set()
    for parte in texto.split(","):
        parte = parte.strip()
        if not parte:
            continue
        if "-" in parte:
            inicio, fin = parte.split("-", 1)
            rango = range(int(inicio), int(fin) + 1)
        else:
            rango = [int(parte)]
        for puerto in rango:
            if not 1 <= puerto <= 65535:
                raise ValueError(f"Puerto fuera de rango: {puerto}")
            puertos.add(puerto)
    return sorted(puertos)


def escanear_puerto(ip: str, puerto: int, timeout: float, banners: bool) -> Resultado | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion:
            conexion.settimeout(timeout)
            if conexion.connect_ex((ip, puerto)) != 0:
                return None
            banner = ""
            if banners:
                conexion.settimeout(min(max(timeout, 0.3), 1.0))
                try:
                    datos = conexion.recv(1024)
                except OSError:
                    datos = b""
                if not datos and puerto in (80, 8080):
                    try:
                        conexion.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                        datos = conexion.recv(1024)
                    except OSError:
                        datos = b""
                if datos:
                    banner = datos.decode("utf-8", "replace").strip().splitlines()[0][:80]
            return Resultado(ip, puerto, SERVICIOS.get(puerto, "desconocido"), banner)
    except OSError:
        return None


def mostrar_aviso() -> None:
    print("=" * 60)
    print("AVISO: usá este escáner SOLO en tu propia red o con permiso escrito.")
    print("Escanear redes ajenas es ilegal en la mayoría de los países.")
    print("=" * 60)


def parsear_argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Escáner TCP de la red local (solo redes propias).",
        epilog="Ejemplo: python3 escaner_red.py --autorizado --puertos 22,80,443",
    )
    parser.add_argument("--autorizado", action="store_true", help="confirmás que la red es tuya o tenés permiso")
    parser.add_argument("--red", help="red a escanear en formato CIDR (por defecto: tu red /24)")
    parser.add_argument("--puertos", default=PUERTOS_POR_DEFECTO, help="puertos: '22,80' o '1-1024'")
    parser.add_argument("--timeout", type=float, default=0.5, help="segundos de espera por puerto (por defecto 0.5)")
    parser.add_argument("--hilos", type=int, default=100, help="conexiones en paralelo (por defecto 100)")
    parser.add_argument("--banners", action="store_true", help="intentar leer el banner del servicio")
    parser.add_argument("--json", dest="archivo_json", help="guardar resultados en un archivo JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parsear_argumentos(argv)
    mostrar_aviso()
    if not args.autorizado:
        print("\nFalta el flag --autorizado. No se escaneó nada.", file=sys.stderr)
        return 2

    try:
        if args.red:
            red = ipaddress.ip_network(args.red, strict=False)
        else:
            ip_local = obtener_ip_local()
            red = ipaddress.ip_network(f"{ip_local}/24", strict=False)
        puertos = parsear_puertos(args.puertos)
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if red.num_addresses > MAX_HOSTS:
        print(f"Error: la red es demasiado grande ({red.num_addresses} direcciones, máximo {MAX_HOSTS}).", file=sys.stderr)
        return 1

    anfitriones = list(red.hosts())
    if not anfitriones:
        anfitriones = [red.network_address]

    print(f"\nRed:      {red}")
    print(f"Equipos:  {len(anfitriones)}")
    print(f"Puertos:  {len(puertos)}")
    print(f"Timeout:  {args.timeout}s\n")

    inicio = time.monotonic()
    resultados: list[Resultado] = []

    with ThreadPoolExecutor(max_workers=max(1, args.hilos)) as ejecutor:
        tareas = [
            ejecutor.submit(escanear_puerto, str(ip), puerto, args.timeout, args.banners)
            for ip in anfitriones
            for puerto in puertos
        ]
        for tarea in as_completed(tareas):
            resultado = tarea.result()
            if resultado:
                resultados.append(resultado)
                extra = f"  [{resultado.banner}]" if resultado.banner else ""
                print(f"  abierto  {resultado.ip}:{resultado.puerto}/tcp  {resultado.servicio}{extra}", flush=True)

    duracion = time.monotonic() - inicio
    resultados.sort(key=lambda r: (ipaddress.ip_address(r.ip), r.puerto))

    equipos = {r.ip for r in resultados}
    print(f"\nResumen: {len(equipos)} equipo(s) con puertos abiertos, {len(resultados)} puerto(s) abiertos.")
    print(f"Duración: {duracion:.1f}s")

    if args.archivo_json:
        with open(args.archivo_json, "w", encoding="utf-8") as archivo:
            json.dump([asdict(r) for r in resultados], archivo, indent=2, ensure_ascii=False)
        print(f"Resultados guardados en: {args.archivo_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
