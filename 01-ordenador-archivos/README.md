# Organizador de archivos

Script en Python que ordena una carpeta por tipo de archivo (y opcionalmente por año/mes).
Incluye modo simulación, protección contra sobrescritura y opción de deshacer.

## Requisitos

- Python 3.9 o superior
- Sin dependencias externas (solo biblioteca estándar)

## Uso

```bash
python3 organizador.py ~/Descargas --simular      # ver qué haría, sin tocar nada
python3 organizador.py ~/Descargas                 # mover archivos
python3 organizador.py ~/Descargas --por-fecha     # separar en año/mes
python3 organizador.py ~/Descargas --copiar        # copiar en vez de mover
python3 organizador.py . --deshacer                # revertir el último ordenamiento
```

## Categorías

| Carpeta | Extensiones |
|---|---|
| Imagenes | jpg, jpeg, png, gif, webp, svg, bmp, tiff, heic |
| Documentos | pdf, doc(x), txt, odt, rtf, xls(x), ods, ppt(x), csv, md |
| Audio | mp3, wav, flac, ogg, m4a, aac, opus |
| Video | mp4, mkv, avi, mov, webm, wmv, flv |
| Comprimidos | zip, rar, 7z, tar, gz, bz2, xz |
| Codigo | py, js, ts, html, css, java, c, cpp, h, go, rs, sh, json, yml, sql, php |
| Instaladores | deb, rpm, appimage, exe, msi, apk, pkg |
| Otros | todo lo demás |

## Seguridad

- Antes de mover, usá siempre `--simular`.
- Si un archivo con el mismo nombre ya existe, se renombra (`foto (1).jpg`) en lugar de sobrescribir.
- Cada ejecución guarda un registro en `.organizador_log.json`, que permite `--deshacer`.
