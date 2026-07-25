from datetime import datetime, timedelta

HORA_INICIO = "10:00"
HORA_FIN = "16:30"
INTERVALO_MINUTOS = 30


def obtener_bloques_horarios():
    """
    Devuelve todos los bloques horarios de la jornada.

    ['10:00','10:30',...,'16:30']
    """

    bloques = []

    hora = datetime.strptime(HORA_INICIO, "%H:%M")
    fin = datetime.strptime(HORA_FIN, "%H:%M")

    while hora <= fin:

        bloques.append(
            hora.strftime("%H:%M")
        )

        hora += timedelta(
            minutes=INTERVALO_MINUTOS
        )

    return bloques

def sumar_minutos(hora, minutos):
    """
    Recibe:

    10:30

    60

    Devuelve:

    11:30
    """

    hora = datetime.strptime(
        hora,
        "%H:%M"
    )

    hora += timedelta(
        minutes=minutos
    )

    return hora.strftime("%H:%M")

def bloques_ocupados(hora_inicio, duracion):
    """
    Devuelve los bloques ocupados por un servicio.

    bloques_ocupados("10:30",60)

    ↓

    ["10:30","11:00"]
    """

    bloques = []

    hora = datetime.strptime(
        hora_inicio,
        "%H:%M"
    )

    cantidad = duracion // 30

    for _ in range(cantidad):

        bloques.append(
            hora.strftime("%H:%M")
        )

        hora += timedelta(
            minutes=30
        )

    return bloques