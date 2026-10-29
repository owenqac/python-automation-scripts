#!/usr/bin/env python3
"""Organizador de archivos por tipo y fecha, con modo simulación y deshacer."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

CATEGORIAS: dict[str, set[str]] = {
    "Imagenes": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".tiff", ".heic"},
    "Documentos": {".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".xls", ".xlsx", ".ods", ".ppt", ".pptx", ".csv", ".md"},
    "Audio": {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".opus"},
    "Video": {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv"},
    "Comprimidos": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Codigo": {".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".sh", ".json", ".yml", ".yaml", ".sql", ".php"},
    "Instaladores": {".deb", ".rpm", ".appimage", ".exe", ".msi", ".apk", ".pkg"},
}

LOG_NAME = ".organizador_log.json"


def categoria_de(archivo: Path) -> str:
    sufijo = archivo.suffix.lower()
    for nombre, extensiones in CATEGORIAS.items():
        if sufijo in extensiones:
            return nombre
    return "Otros"


def ruta_libre(destino: Path) -> Path:
    if not destino.exists():
        return destino
    contador = 1
    while True:
        candidato = destino.with_name(f"{destino.stem} ({contador}){destino.suffix}")
        if not candidato.exists():
            return candidato
        contador += 1


def destino_de(archivo: Path, base: Path, args: argparse.Namespace) -> Path:
    destino = Path(args.destino).expanduser().resolve() if args.destino else base
    carpeta = destino / categoria_de(archivo)
    if args.por_fecha:
        fecha = datetime.fromtimestamp(archivo.stat().st_mtime)
        carpeta = carpeta / f"{fecha.year:04d}" / f"{fecha.month:02d}"
    return ruta_libre(carpeta / archivo.name)


def archivos_a_ordenar(base: Path) -> list[Path]:
    resultado = []
    for entrada in sorted(base.iterdir()):
        if entrada.name == LOG_NAME or entrada.name.startswith(".organizador"):
            continue
        if entrada.is_file():
            resultado.append(entrada)
    return resultado


def guardar_log(movimientos: list[dict[str, str]]) -> None:
    ruta = Path(LOG_NAME)
    previos: list[dict[str, str]] = []
    if ruta.exists():
        previos = json.loads(ruta.read_text(encoding="utf-8"))
    ruta.write_text(json.dumps(previos + movimientos, indent=2, ensure_ascii=False), encoding="utf-8")


def ordenar(args: argparse.Namespace) -> int:
    base = Path(args.ruta).expanduser().resolve()
    if not base.is_dir():
        print(f"Error: {base} no es una carpeta.", file=sys.stderr)
        return 1

    archivos = archivos_a_ordenar(base)
    if not archivos:
        print("No hay archivos para ordenar.")
        return 0

    prefijo = "[simulación] " if args.simular and not args.copiar else ""
    movimientos: list[dict[str, str]] = []

    for archivo in archivos:
        destino = destino_de(archivo, base, args)
        if destino.parent == archivo.parent:
            continue
        accion = "copiar" if args.copiar else "mover"
        print(f"{prefijo}{accion}: {archivo.relative_to(base)} -> {destino.relative_to(base) if destino.is_relative_to(base) else destino}")
        if args.simular:
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        if args.copiar:
            shutil.copy2(archivo, destino)
        else:
            shutil.move(str(archivo), str(destino))
        movimientos.append({"origen": str(archivo), "destino": str(destino)})

    if movimientos:
        guardar_log(movimientos)
        print(f"\n{len(movimientos)} archivo(s) procesados. Usá --deshacer para revertir.")
    elif not args.simular:
        print("\nNada para mover: ya estaba todo ordenado.")
    return 0


def deshacer() -> int:
    ruta = Path(LOG_NAME)
    if not ruta.exists():
        print("No hay registro de movimientos para deshacer.", file=sys.stderr)
        return 1

    movimientos = json.loads(ruta.read_text(encoding="utf-8"))
    revertidos = 0
    for movimiento in reversed(movimientos):
        origen = Path(movimiento["origen"])
        destino = Path(movimiento["destino"])
        if not destino.exists():
            continue
        origen.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(destino), str(ruta_libre(origen)))
        revertidos += 1
        for padre in (destino.parent, destino.parent.parent):
            if padre.is_dir() and not any(padre.iterdir()):
                padre.rmdir()
    ruta.unlink()
    print(f"{revertidos} archivo(s) devueltos a su lugar.")
    return 0


def parsear_argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ordena archivos por tipo (y opcionalmente por año/mes).",
        epilog="Ejemplo: python3 organizador.py ~/Descargas --simular",
    )
    parser.add_argument("ruta", nargs="?", default=".", help="carpeta a ordenar (por defecto: la actual)")
    parser.add_argument("--destino", help="carpeta donde guardar lo ordenado (por defecto: la misma)")
    parser.add_argument("--por-fecha", action="store_true", help="separar además en año/mes")
    parser.add_argument("--copiar", action="store_true", help="copiar en vez de mover")
    parser.add_argument("--simular", action="store_true", help="mostrar qué haría sin tocar nada")
    parser.add_argument("--deshacer", action="store_true", help="revertir el último ordenamiento")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parsear_argumentos(argv)
    if args.deshacer:
        return deshacer()
    return ordenar(args)


if __name__ == "__main__":
    raise SystemExit(main())
