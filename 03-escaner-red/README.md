# Escáner de red local

Escáner TCP de la red propia, en Python puro. Detecta equipos y puertos abiertos y puede
identificar el servicio que escucha detrás de cada puerto.

> **Aviso legal:** usalo solo en tu red o con permiso escrito del dueño. Escanear redes
> ajenas es ilegal. El script exige el flag `--autorizado` justamente para que lo tengas presente.

## Requisitos

- Python 3.9 o superior
- Linux (usa el comando `ip` para detectar tu red)
- Sin dependencias externas

## Uso

```bash
# escanear tu red con los puertos más comunes
python3 escaner_red.py --autorizado

# puertos concretos
python3 escaner_red.py --autorizado --puertos 22,80,443

# un rango de puertos y otra red
python3 escaner_red.py --autorizado --red 192.168.0.0/24 --puertos 1-1024

# identificar servicios y guardar resultados
python3 escaner_red.py --autorizado --banners --json resultados.json
```

## Opciones

| Opción | Qué hace |
|---|---|
| `--autorizado` | Obligatorio: confirmás que la red es tuya |
| `--red` | Red en formato CIDR (por defecto: tu /24) |
| `--puertos` | `22,80,443` o rangos `1-1024` |
| `--timeout` | Segundos de espera por puerto (0.5) |
| `--hilos` | Conexiones en paralelo (100) |
| `--banners` | Lee el banner del servicio |
| `--json` | Guarda los resultados en JSON |

## Ejemplo de salida

```
  abierto  192.168.1.1:53/tcp    dns
  abierto  192.168.1.1:80/tcp    http  [HTTP/1.0 200 OK]
  abierto  192.168.1.10:22/tcp   ssh   [SSH-2.0-OpenSSH_9.6]

Resumen: 2 equipo(s) con puertos abiertos, 3 puerto(s) abiertos.
Duración: 4.2s
```

## Seguridad

- Limita a 1024 direcciones por escaneo para no saturar la red.
- Usa TCP connect (no necesita permisos de root).
- Todo el tráfico es hacia tu propia red local.
