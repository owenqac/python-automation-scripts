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

### 3. Escáner de red local
Detecta los equipos de tu red y sus puertos abiertos, con lectura de banners y salida JSON.
Solo para redes propias o con permiso.

```bash
python3 03-escaner-red/escaner_red.py --autorizado
python3 03-escaner-red/escaner_red.py --autorizado --puertos 1-1024 --banners
```

Características: TCP connect multihilo, detección automática de tu red, rangos de puertos,
banners de servicio, exportación JSON y flag `--autorizado` obligatorio.

## Requisitos

- Python 3.9+
- Biblioteca estándar únicamente

## Autor

Owen ([@owenqac](https://github.com/owenqac))

## Licencia

MIT
