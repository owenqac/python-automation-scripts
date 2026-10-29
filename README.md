# Scripts de automatización en Python

Colección de herramientas de línea de comandos escritas en Python, sin dependencias externas,
para automatizar tareas repetitivas del día a día.

## Proyectos

### 1. Organizador de archivos
Ordena una carpeta por tipo de archivo (imágenes, documentos, audio, video, etc.) y
opcionalmente por año/mes.

```bash
python3 01-ordenador-archivos/organizador.py ~/Descargas --simular
python3 01-ordenador-archivos/organizador.py ~/Descargas
```

Características: modo simulación, protección contra sobrescritura, registro de movimientos
y opción de deshacer.

### 2. Limpiador de CSV
Limpia archivos CSV desordenados: recorta espacios, elimina duplicados y filas/columnas
vacías, detecta el separador automáticamente y maneja el BOM de Excel.

```bash
python3 02-limpiador-csv/limpiador_csv.py ventas.csv
python3 02-limpiador-csv/limpiador_csv.py ventas.csv --simular
```

## Requisitos

- Python 3.9+
- Biblioteca estándar únicamente

## Autor

Owen ([@owenqac](https://github.com/owenqac))

## Licencia

MIT
