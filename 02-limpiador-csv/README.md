# Limpiador de CSV

Script en Python que limpia archivos CSV sucios: recorta espacios, elimina filas duplicadas,
quita filas y columnas vacías y detecta el separador automáticamente.

## Requisitos

- Python 3.9 o superior
- Sin dependencias externas (solo biblioteca estándar)

## Uso

```bash
python3 limpiador_csv.py ventas.csv                      # genera ventas_limpio.csv
python3 limpiador_csv.py ventas.csv -o salida.csv        # nombre de salida propio
python3 limpiador_csv.py ventas.csv --simular            # solo ver el resumen
python3 limpiador_csv.py datos.csv --delimitador ';'     # forzar separador
python3 limpiador_csv.py datos.csv --mantener-duplicados # no borrar repetidos
```

## Qué limpia

| Problema | Qué hace |
|---|---|
| Espacios sobrantes (`" juan "`) | Los recorta (`"juan"`) |
| Filas duplicadas | Deja solo la primera |
| Filas vacías | Las elimina |
| Columnas vacías | Las elimina |
| Separador `,` `;` tab `\|` | Lo detecta solo |
| BOM de Excel | Lo interpreta y lo escribe correctamente |

Al terminar muestra un resumen con filas de entrada/salida y cuántas cosas cambió.

## Seguridad

- `--simular` muestra el resumen sin escribir nada.
- El archivo original **nunca** se modifica: siempre escribe uno nuevo.
- La salida se guarda en UTF-8 con BOM, que es lo que Excel abre sin romper acentos.
