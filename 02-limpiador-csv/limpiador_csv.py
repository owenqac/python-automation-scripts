#!/usr/bin/env python3
"""Limpia archivos CSV: recorta espacios, elimina duplicados y filas/columnas vacías."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

DELIMITADORES = ",;\t|"


def detectar_delimitador(muestra: str) -> str:
    try:
        return csv.Sniffer().sniff(muestra, delimiters=DELIMITADORES).delimiter
    except csv.Error:
        return ","


def leer_csv(ruta: Path, delimitador: str | None) -> tuple[list[list[str]], str]:
    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        muestra = archivo.read(4096)
        archivo.seek(0)
        separador = delimitador or detectar_delimitador(muestra)
        filas = list(csv.reader(archivo, delimiter=separador))
    return filas, separador


def limpiar(
    filas: list[list[str]],
    recortar: bool = True,
    deduplicar: bool = True,
    quitar_vacias: bool = True,
) -> tuple[list[list[str]], dict[str, int]]:
    estadisticas = {
        "filas_entrada": max(len(filas) - 1, 0),
        "celdas_recortadas": 0,
        "filas_vacias": 0,
        "columnas_vacias": 0,
        "duplicados": 0,
        "filas_salida": 0,
    }
    if not filas:
        return [], estadisticas

    encabezado = filas[0]
    cuerpo = filas[1:]

    if recortar:
        encabezado = [celda.strip() for celda in encabezado]
        nuevo_cuerpo = []
        for fila in cuerpo:
            limpia = [celda.strip() for celda in fila]
            estadisticas["celdas_recortadas"] += sum(
                1 for original, actual in zip(fila, limpia) if original != actual
            )
            nuevo_cuerpo.append(limpia)
        cuerpo = nuevo_cuerpo

    ancho = max(len(encabezado), max((len(fila) for fila in cuerpo), default=0))
    encabezado = encabezado + [""] * (ancho - len(encabezado))
    cuerpo = [fila + [""] * (ancho - len(fila)) for fila in cuerpo]

    if quitar_vacias:
        antes = len(cuerpo)
        cuerpo = [fila for fila in cuerpo if any(fila)]
        estadisticas["filas_vacias"] = antes - len(cuerpo)

        columnas_llenas = [False] * ancho
        for indice in range(ancho):
            if encabezado[indice]:
                columnas_llenas[indice] = True
            elif any(fila[indice] for fila in cuerpo):
                columnas_llenas[indice] = True
        estadisticas["columnas_vacias"] = columnas_llenas.count(False)
        if False in columnas_llenas:
            encabezado = [celda for celda, llena in zip(encabezado, columnas_llenas) if llena]
            cuerpo = [
                [celda for celda, llena in zip(fila, columnas_llenas) if llena] for fila in cuerpo
            ]

    if deduplicar:
        vistos: set[tuple[str, ...]] = set()
        sin_duplicados = []
        for fila in cuerpo:
            clave = tuple(fila)
            if clave in vistos:
                estadisticas["duplicados"] += 1
                continue
            vistos.add(clave)
            sin_duplicados.append(fila)
        cuerpo = sin_duplicados

    estadisticas["filas_salida"] = len(cuerpo)
    return [encabezado] + cuerpo, estadisticas


def escribir_csv(ruta: Path, filas: list[list[str]], separador: str) -> None:
    with ruta.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo, delimiter=separador, quoting=csv.QUOTE_MINIMAL)
        escritor.writerows(filas)


def mostrar_resumen(estadisticas: dict[str, int], separador: str, salida: Path | None, simular: bool) -> None:
    print(f"Separador detectado: {separador!r}")
    print(f"Filas de entrada:    {estadisticas['filas_entrada']}")
    print(f"Filas de salida:     {estadisticas['filas_salida']}")
    print(f"Celdas recortadas:   {estadisticas['celdas_recortadas']}")
    print(f"Filas vacías:        {estadisticas['filas_vacias']}")
    print(f"Columnas vacías:     {estadisticas['columnas_vacias']}")
    print(f"Duplicados:          {estadisticas['duplicados']}")
    if simular:
        print("\n[simulación] No se escribió ningún archivo.")
    elif salida:
        print(f"\nGuardado en: {salida}")


def parsear_argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Limpia un CSV: recorta espacios, saca duplicados y filas/columnas vacías.",
        epilog="Ejemplo: python3 limpiador_csv.py ventas.csv -o ventas_limpias.csv",
    )
    parser.add_argument("entrada", help="archivo CSV de entrada")
    parser.add_argument("-o", "--salida", help="archivo de salida (por defecto: <entrada>_limpio.csv)")
    parser.add_argument("--delimitador", help="forzar separador (por defecto se detecta solo)")
    parser.add_argument("--no-recortar", action="store_true", help="no quitar espacios sobrantes")
    parser.add_argument("--mantener-duplicados", action="store_true", help="no eliminar filas repetidas")
    parser.add_argument("--mantener-vacias", action="store_true", help="no eliminar filas/columnas vacías")
    parser.add_argument("--simular", action="store_true", help="mostrar el resumen sin escribir el archivo")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parsear_argumentos(argv)
    entrada = Path(args.entrada).expanduser()
    if not entrada.is_file():
        print(f"Error: no existe el archivo {entrada}", file=sys.stderr)
        return 1

    filas, separador = leer_csv(entrada, args.delimitador)
    if not filas:
        print("El archivo está vacío.", file=sys.stderr)
        return 1

    filas_limpias, estadisticas = limpiar(
        filas,
        recortar=not args.no_recortar,
        deduplicar=not args.mantener_duplicados,
        quitar_vacias=not args.mantener_vacias,
    )

    salida = Path(args.salida).expanduser() if args.salida else entrada.with_name(f"{entrada.stem}_limpio.csv")

    if not args.simular:
        escribir_csv(salida, filas_limpias, separador)

    mostrar_resumen(estadisticas, separador, salida, args.simular)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
