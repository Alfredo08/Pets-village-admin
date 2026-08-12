from app_flask.config.mysqlconnection import connectToMySQL
from app_flask.helpers.horarios import bloques_ocupados
from app_flask import BASE_DATOS


class OrdenServicio:
    ESTADOS_VALIDOS = {
        "pendiente",
        "confirmada",
        "en_proceso",
        "finalizada",
        "cancelada",
        "no_asistio"
    }
    def __init__(self, data):
        self.id_orden = data["id_orden"]
        self.folio = data["folio"]
        self.id_cliente = data["id_cliente"]
        self.id_mascota = data["id_mascota"]
        self.id_servicio = data["id_servicio"]
        self.id_usuario = data["id_usuario"]
        self.fecha = data["fecha"]
        self.hora_inicio = data["hora_inicio"]
        self.duracion_minutos = data["duracion_minutos"]
        self.estado = data["estado"]
        self.notas = data["notas"]
        self.id_venta = data["id_venta"]
        self.fecha_creacion = data["fecha_creacion"]
        self.fecha_actualizacion = data["fecha_actualizacion"]

    ####################################################
    # CREAR ORDEN
    ####################################################

    @classmethod
    def crear(cls, data):

        query = """
            INSERT INTO ordenes_servicio
            (
                folio,
                id_cliente,
                id_mascota,
                id_servicio,
                id_usuario,
                fecha,
                hora_inicio,
                duracion_minutos,
                estado,
                notas
            )
            VALUES
            (
                '',
                %(id_cliente)s,
                %(id_mascota)s,
                %(id_servicio)s,
                %(id_usuario)s,
                %(fecha)s,
                %(hora_inicio)s,
                %(duracion_minutos)s,
                %(estado)s,
                %(notas)s
            );
        """

        id_orden = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )

        if not id_orden:
            return False

        folio = f"OS-{id_orden:06d}"

        query = """
            UPDATE ordenes_servicio

            SET folio=%(folio)s

            WHERE id_orden=%(id_orden)s;
        """

        connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "folio": folio,
                "id_orden": id_orden
            }
        )

        return {
            "exito": True,
            "id_orden": id_orden,
            "folio": folio
        }

    ####################################################
    # OBTENER POR ID
    ####################################################

    @classmethod
    def obtener_por_id(cls, data):
        query = """
            SELECT
                os.*,

                c.nombre AS nombre_cliente,
                c.telefono AS telefono_cliente,
                c.correo AS correo_cliente,

                m.nombre AS nombre_mascota,
                m.numero_expediente,
                m.raza,
                m.tamano,
                m.tipo_pelo,

                s.nombre AS nombre_servicio,

                u.nombre AS nombre_estilista,
                u.color_agenda

            FROM ordenes_servicio os

            INNER JOIN clientes c
                ON c.id_cliente = os.id_cliente

            INNER JOIN mascotas m
                ON m.id_mascota = os.id_mascota

            INNER JOIN servicios s
                ON s.id_servicio = os.id_servicio

            INNER JOIN usuarios u
                ON u.id_usuario = os.id_usuario

            WHERE os.id_orden = %(id_orden)s

            LIMIT 1;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(
            query,
            data
        )

        if not resultado:
            return None

        return resultado[0]

    ####################################################
    # OBTENER HOY
    ####################################################

    @classmethod
    def obtener_hoy(cls):

        query = """
            SELECT

                os.*,

                c.nombre AS nombre_cliente,

                m.nombre AS nombre_mascota,

                s.nombre AS nombre_servicio,

                u.nombre AS nombre_estilista,

                u.color_agenda

            FROM ordenes_servicio os

            INNER JOIN clientes c

                ON c.id_cliente=os.id_cliente

            INNER JOIN mascotas m

                ON m.id_mascota=os.id_mascota

            INNER JOIN servicios s

                ON s.id_servicio=os.id_servicio

            INNER JOIN usuarios u

                ON u.id_usuario=os.id_usuario

            WHERE os.fecha=CURDATE()

            ORDER BY

                os.hora_inicio,

                u.nombre;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query
        )

        if not resultado:

            return []

        return resultado

    ####################################################
    # OBTENER POR FECHA
    ####################################################

    @classmethod
    def obtener_por_fecha(cls, fecha):
        query = """
            SELECT
                os.*,

                c.nombre AS nombre_cliente,
                c.correo AS correo_cliente,
                m.nombre AS nombre_mascota,
                s.nombre AS nombre_servicio,

                u.nombre AS nombre_estilista,
                u.color_agenda

            FROM ordenes_servicio os

            INNER JOIN clientes c
                ON c.id_cliente = os.id_cliente

            INNER JOIN mascotas m
                ON m.id_mascota = os.id_mascota

            INNER JOIN servicios s
                ON s.id_servicio = os.id_servicio

            INNER JOIN usuarios u
                ON u.id_usuario = os.id_usuario

            WHERE os.fecha = %(fecha)s
            AND os.estado NOT IN (
                'cancelada',
                'no_asistio'
            )

            ORDER BY
                os.hora_inicio,
                u.orden_agenda,
                os.id_orden;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(
            query,
            {
                "fecha": fecha
            }
        )

        return resultado or []

    ####################################################
    # CAMBIAR ESTADO
    ####################################################

    @classmethod
    def cambiar_estado(cls, data):
        if data["estado"] not in cls.ESTADOS_VALIDOS:
            return False

        query = """
            UPDATE ordenes_servicio
            SET estado = %(estado)s
            WHERE id_orden = %(id_orden)s;
        """

        return connectToMySQL(BASE_DATOS).query_db(
            query,
            data
        )

    ####################################################
    # OBTENER ESTILISTAS DISPONIBLES
    ####################################################
    @classmethod
    def obtener_estilistas_disponibles(
        cls,
        fecha,
        hora_inicio,
        duracion_minutos,
        id_orden_ignorar=None
    ):
        bloques_solicitados = bloques_ocupados(
            hora_inicio,
            duracion_minutos
        )

        query = """
            SELECT
                id_usuario,
                nombre,
                color_agenda,
                orden_agenda
            FROM usuarios
            WHERE rol = 'estilista'
            AND activo = 1
            ORDER BY orden_agenda, nombre;
        """

        estilistas = connectToMySQL(BASE_DATOS).query_db(query)

        if not estilistas:
            return []

        query = """
            SELECT
                id_orden,
                id_usuario,
                hora_inicio,
                duracion_minutos
            FROM ordenes_servicio
            WHERE fecha = %(fecha)s
            AND estado NOT IN (
                'cancelada',
                'no_asistio'
            )
        """

        data_query = {
            "fecha": fecha
        }

        if id_orden_ignorar is not None:
            query += """
            AND id_orden <> %(id_orden_ignorar)s
            """

            data_query["id_orden_ignorar"] = id_orden_ignorar

        query += ";"

        ordenes = connectToMySQL(BASE_DATOS).query_db(
            query,
            data_query
        )

        if not ordenes:
            ordenes = []

        ocupacion = {}

        for orden in ordenes:
            hora_orden = normalizar_hora(
                orden["hora_inicio"]
            )

            bloques = bloques_ocupados(
                hora_orden,
                orden["duracion_minutos"]
            )

            id_usuario = orden["id_usuario"]

            if id_usuario not in ocupacion:
                ocupacion[id_usuario] = []

            ocupacion[id_usuario].extend(bloques)

        disponibles = []

        for estilista in estilistas:
            bloques_estilista = ocupacion.get(
                estilista["id_usuario"],
                []
            )

            conflicto = any(
                bloque in bloques_estilista
                for bloque in bloques_solicitados
            )

            if not conflicto:
                disponibles.append(estilista)

        return disponibles
    
    ####################################################
    # VALIDAR SI UN ESTILISTA ESTÁ DISPONIBLE
    ####################################################
    @classmethod
    def estilista_disponible(
        cls,
        id_usuario,
        fecha,
        hora_inicio,
        duracion_minutos,
        id_orden_ignorar=None
    ):
        disponibles = cls.obtener_estilistas_disponibles(
            fecha,
            hora_inicio,
            duracion_minutos,
            id_orden_ignorar
        )

        return any(
            usuario["id_usuario"] == id_usuario
            for usuario in disponibles
        )

    ####################################################
    # ACTUALIZAR ORDEN
    ####################################################

    @classmethod
    def actualizar(cls, data):
        query = """
            UPDATE ordenes_servicio
            SET
                id_cliente = %(id_cliente)s,
                id_mascota = %(id_mascota)s,
                id_servicio = %(id_servicio)s,
                id_usuario = %(id_usuario)s,
                fecha = %(fecha)s,
                hora_inicio = %(hora_inicio)s,
                duracion_minutos = %(duracion_minutos)s,
                estado = %(estado)s,
                notas = %(notas)s
            WHERE id_orden = %(id_orden)s;
        """

        return connectToMySQL(BASE_DATOS).query_db(
            query,
            data
        )

    ####################################################
    # OBTENER ORDEN PARA EL POS
    ####################################################

    @classmethod
    def obtener_para_pos(cls, data):
        query = """
            SELECT
                os.id_orden,
                os.folio,
                os.id_cliente,
                os.id_mascota,
                os.id_servicio,
                os.id_usuario,
                os.fecha,
                os.hora_inicio,
                os.duracion_minutos,
                os.estado,
                os.notas,
                os.id_venta,

                c.nombre AS nombre_cliente,
                c.telefono AS telefono_cliente,
                c.correo AS correo_cliente,

                m.nombre AS nombre_mascota,
                m.numero_expediente,
                m.raza,
                m.tamano,
                m.tipo_pelo,

                s.nombre AS nombre_servicio,
                s.descripcion AS descripcion_servicio,

                u.nombre AS nombre_estilista

            FROM ordenes_servicio os

            INNER JOIN clientes c
                ON c.id_cliente = os.id_cliente

            INNER JOIN mascotas m
                ON m.id_mascota = os.id_mascota

            INNER JOIN servicios s
                ON s.id_servicio = os.id_servicio

            INNER JOIN usuarios u
                ON u.id_usuario = os.id_usuario

            WHERE os.id_orden = %(id_orden)s

            LIMIT 1;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(
            query,
            data
        )

        if not resultado:
            return None

        return resultado[0]

    ####################################################
    # VALIDAR ORDEN
    ####################################################

    @classmethod
    def validar(cls, formulario):
        errores = []

        id_cliente = formulario.get("id_cliente", "").strip()
        id_mascota = formulario.get("id_mascota", "").strip()
        id_servicio = formulario.get("id_servicio", "").strip()
        id_usuario = formulario.get("id_usuario", "").strip()

        fecha = formulario.get("fecha", "").strip()
        hora_inicio = formulario.get("hora_inicio", "").strip()
        duracion_texto = formulario.get(
            "duracion_minutos",
            ""
        ).strip()

        estados_validos = {
            "pendiente",
            "confirmada"
        }

        estado = formulario.get(
            "estado",
            "pendiente"
        ).strip()

        if not id_cliente.isdigit():
            errores.append("Selecciona un cliente válido.")

        if not id_mascota.isdigit():
            errores.append("Selecciona una mascota válida.")

        if not id_servicio.isdigit():
            errores.append("Selecciona un servicio válido.")

        if not id_usuario.isdigit():
            errores.append("Selecciona un estilista válido.")

        if not fecha:
            errores.append("Selecciona la fecha de la orden.")

        horarios_validos = {
            "10:00",
            "10:30",
            "11:00",
            "11:30",
            "12:00",
            "12:30",
            "13:00",
            "13:30",
            "14:00",
            "14:30",
            "15:00",
            "15:30",
            "16:00",
            "16:30"
        }

        if hora_inicio not in horarios_validos:
            errores.append(
                "Selecciona un horario válido entre 10:00 y 16:30."
            )

        try:
            duracion = int(duracion_texto)

            if duracion <= 0:
                errores.append(
                    "La duración debe ser mayor que cero."
                )

            if duracion % 30 != 0:
                errores.append(
                    "La duración debe expresarse en bloques de 30 minutos."
                )

        except (ValueError, TypeError):
            errores.append(
                "La duración de la orden no es válida."
            )

        if estado not in estados_validos:
            errores.append(
                "El estado inicial de la orden no es válido."
            )

        return errores

    ####################################################
    # OBTENER CITAS DE UNA MASCOTA
    ####################################################

    @classmethod
    def obtener_citas_mascota(cls, data):
        query = """
            SELECT
                os.id_orden,
                os.folio,
                os.fecha,
                os.hora_inicio,
                os.duracion_minutos,
                os.estado,
                os.notas,

                s.nombre AS nombre_servicio,

                u.nombre AS nombre_estilista,
                u.color_agenda,

                v.id_venta,
                v.folio AS folio_venta

            FROM ordenes_servicio os

            INNER JOIN servicios s
                ON s.id_servicio = os.id_servicio

            INNER JOIN usuarios u
                ON u.id_usuario = os.id_usuario

            LEFT JOIN ventas v
                ON v.id_venta = os.id_venta

            WHERE os.id_mascota = %(id_mascota)s

            ORDER BY
                os.fecha DESC,
                os.hora_inicio DESC,
                os.id_orden DESC;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )

        return resultado or []

    ####################################################
    # VERIFICAR ORDEN DUPLICADA
    ####################################################

    @classmethod
    def existe_orden_duplicada(cls, data):
        query = """
            SELECT id_orden
            FROM ordenes_servicio
            WHERE id_cliente = %(id_cliente)s
            AND id_mascota = %(id_mascota)s
            AND id_servicio = %(id_servicio)s
            AND id_usuario = %(id_usuario)s
            AND fecha = %(fecha)s
            AND hora_inicio = %(hora_inicio)s
            AND estado NOT IN (
                'cancelada',
                'no_asistio'
            )
            LIMIT 1;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(
            query,
            data
        )

        return bool(resultado)

    ####################################################
    # OBTENER ÓRDENES DISPONIBLES PARA POS
    ####################################################

    @classmethod
    def obtener_pendientes_pos(cls, fecha=None, termino=""):
        data = {
            "termino": f"%{termino.strip()}%"
        }

        filtro_fecha = ""

        if fecha:
            filtro_fecha = """
                AND os.fecha = %(fecha)s
            """

            data["fecha"] = fecha

        query = f"""
            SELECT
                os.id_orden,
                os.folio,
                os.id_cliente,
                os.id_mascota,
                os.id_servicio,
                os.id_usuario,
                os.fecha,
                os.hora_inicio,
                os.duracion_minutos,
                os.estado,
                os.notas,
                os.id_venta,

                c.nombre AS nombre_cliente,
                c.telefono AS telefono_cliente,

                m.nombre AS nombre_mascota,
                m.numero_expediente,

                s.nombre AS nombre_servicio,

                u.nombre AS nombre_estilista,
                u.color_agenda

            FROM ordenes_servicio os

            INNER JOIN clientes c
                ON c.id_cliente = os.id_cliente

            INNER JOIN mascotas m
                ON m.id_mascota = os.id_mascota

            INNER JOIN servicios s
                ON s.id_servicio = os.id_servicio

            INNER JOIN usuarios u
                ON u.id_usuario = os.id_usuario

            WHERE os.estado IN (
                'confirmada',
                'en_proceso'
            )

            AND os.id_venta IS NULL

            AND (
                os.folio LIKE %(termino)s
                OR c.nombre LIKE %(termino)s
                OR c.telefono LIKE %(termino)s
                OR m.nombre LIKE %(termino)s
                OR m.numero_expediente LIKE %(termino)s
                OR s.nombre LIKE %(termino)s
                OR u.nombre LIKE %(termino)s
            )

            {filtro_fecha}

            ORDER BY
                os.fecha ASC,
                os.hora_inicio ASC,
                u.nombre ASC;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )

        return resultado or []
    
from datetime import time, timedelta


def normalizar_hora(valor):
    """
    Convierte una hora proveniente de MySQL a formato HH:MM.

    PyMySQL puede devolver TIME como:
    - datetime.timedelta
    - datetime.time
    - str
    """

    if isinstance(valor, timedelta):
        segundos_totales = int(valor.total_seconds())
        horas = segundos_totales // 3600
        minutos = (segundos_totales % 3600) // 60

        return f"{horas:02d}:{minutos:02d}"

    if isinstance(valor, time):
        return valor.strftime("%H:%M")

    if isinstance(valor, str):
        return valor[:5]

    raise ValueError(
        f"No se pudo interpretar el valor de hora: {valor!r}"
    )
