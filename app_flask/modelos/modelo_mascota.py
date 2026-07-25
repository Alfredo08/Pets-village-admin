from datetime import date
from decimal import Decimal, InvalidOperation

from app_flask import BASE_DATOS
from app_flask.config.mysqlconnection import connectToMySQL


class Mascota:
    ESPECIES_VALIDAS = {
        "perro",
        "gato",
        "otro"
    }

    SEXOS_VALIDOS = {
        "Macho",
        "Hembra",
        "No especificado"
    }

    TAMANOS_VALIDOS = {
        "toy_chico",
        "mediano",
        "grande",
        "extra_grande"
    }

    TIPOS_PELO_VALIDOS = {
        "corto",
        "largo"
    }

    def __init__(self, data):
        self.id_mascota = data["id_mascota"]
        self.numero_expediente = data.get("numero_expediente")
        self.foto = data.get("foto")

        self.id_cliente = data["id_cliente"]
        self.nombre = data["nombre"]
        self.especie = data.get("especie")
        self.raza = data.get("raza")
        self.tamano = data.get("tamano")
        self.tipo_pelo = data.get("tipo_pelo")

        self.sexo = data.get("sexo")
        self.fecha_nacimiento = data.get("fecha_nacimiento")
        self.peso = data.get("peso")
        self.color = data.get("color")
        self.esterilizado = data.get("esterilizado")
        self.alergias = data.get("alergias")

        self.observaciones = data.get("observaciones")
        self.notas_especiales = data.get("notas_especiales")
        self.activo = data["activo"]
        self.fecha_creacion = data.get("fecha_creacion")

        self.nombre_cliente = data.get("nombre_cliente")

    @classmethod
    def obtener_por_cliente(cls, data):
        query = """
            SELECT
                m.*,
                c.nombre AS nombre_cliente
            FROM mascotas m
            INNER JOIN clientes c
                ON c.id_cliente = m.id_cliente
            WHERE m.id_cliente = %(id_cliente)s
            ORDER BY m.activo DESC, m.nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, data)

        if not resultados:
            return []

        return [cls(mascota) for mascota in resultados]

    @classmethod
    def obtener_activas_por_cliente(cls, data):
        query = """
            SELECT
                m.*,
                c.nombre AS nombre_cliente
            FROM mascotas m
            INNER JOIN clientes c
                ON c.id_cliente = m.id_cliente
            WHERE m.id_cliente = %(id_cliente)s
              AND m.activo = 1
            ORDER BY m.nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, data)

        if not resultados:
            return []

        return [cls(mascota) for mascota in resultados]

    @classmethod
    def obtener_por_id(cls, data):
        query = """
            SELECT
                m.*,
                c.nombre AS nombre_cliente
            FROM mascotas m
            INNER JOIN clientes c
                ON c.id_cliente = m.id_cliente
            WHERE m.id_mascota = %(id_mascota)s
            LIMIT 1;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, data)

        if not resultado:
            return None

        return cls(resultado[0])

    @classmethod
    def crear(cls, data):
        query = """
            INSERT INTO mascotas (
                id_cliente,
                nombre,
                especie,
                raza,
                tamano,
                tipo_pelo,
                sexo,
                fecha_nacimiento,
                peso,
                color,
                esterilizado,
                alergias,
                observaciones,
                notas_especiales,
                activo
            )
            VALUES (
                %(id_cliente)s,
                %(nombre)s,
                %(especie)s,
                %(raza)s,
                %(tamano)s,
                %(tipo_pelo)s,
                %(sexo)s,
                %(fecha_nacimiento)s,
                %(peso)s,
                %(color)s,
                %(esterilizado)s,
                %(alergias)s,
                %(observaciones)s,
                %(notas_especiales)s,
                1
            );
        """

        id_mascota = connectToMySQL(BASE_DATOS).query_db(query, data)

        if not id_mascota:
            return False

        expediente = f"PV-{id_mascota:05d}"

        query_expediente = """
            UPDATE mascotas
            SET numero_expediente = %(numero_expediente)s
            WHERE id_mascota = %(id_mascota)s;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(
            query_expediente,
            {
                "numero_expediente": expediente,
                "id_mascota": id_mascota
            }
        )

        if resultado is False:
            return False

        return id_mascota

    @classmethod
    def actualizar(cls, data):
        query = """
            UPDATE mascotas
            SET
                nombre = %(nombre)s,
                especie = %(especie)s,
                raza = %(raza)s,
                tamano = %(tamano)s,
                tipo_pelo = %(tipo_pelo)s,
                sexo = %(sexo)s,
                fecha_nacimiento = %(fecha_nacimiento)s,
                peso = %(peso)s,
                color = %(color)s,
                esterilizado = %(esterilizado)s,
                alergias = %(alergias)s,
                observaciones = %(observaciones)s,
                notas_especiales = %(notas_especiales)s
            WHERE id_mascota = %(id_mascota)s;
        """

        return connectToMySQL(BASE_DATOS).query_db(query, data)

    @classmethod
    def cambiar_estado(cls, data):
        query = """
            UPDATE mascotas
            SET activo = %(activo)s
            WHERE id_mascota = %(id_mascota)s;
        """

        return connectToMySQL(BASE_DATOS).query_db(query, data)

    @classmethod
    def obtener_todas(cls, termino=""):

        query = """
            SELECT

                m.*,

                c.nombre AS nombre_cliente

            FROM mascotas m

            INNER JOIN clientes c

                ON c.id_cliente = m.id_cliente

            WHERE

                (

                    m.nombre LIKE %(buscar)s

                    OR

                    IFNULL(m.numero_expediente,'')
                    LIKE %(buscar)s

                    OR

                    IFNULL(m.raza,'')
                    LIKE %(buscar)s

                    OR

                    c.nombre LIKE %(buscar)s

                )

            ORDER BY

                m.activo DESC,

                m.nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(

            query,

            {
                "buscar": f"%{termino}%"
            }

        )

        if not resultados:
            return []

        return [cls(mascota) for mascota in resultados]

    ####################################################
    # VALIDAR MASCOTA Y CLIENTE
    ####################################################

    @classmethod
    def pertenece_a_cliente(cls, id_mascota, id_cliente):
        query = """
            SELECT id_mascota
            FROM mascotas
            WHERE id_mascota = %(id_mascota)s
            AND id_cliente = %(id_cliente)s
            AND activo = 1
            LIMIT 1;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(
            query,
            {
                "id_mascota": id_mascota,
                "id_cliente": id_cliente
            }
        )

        return bool(resultado)

    ####################################################
    # OBTENER TODAS LAS MASCOTAS ACTIVAS
    ####################################################

    @classmethod
    def obtener_todas_activas(cls):
        query = """
            SELECT
                m.*,
                c.nombre AS nombre_cliente
            FROM mascotas m
            INNER JOIN clientes c
                ON c.id_cliente = m.id_cliente
            WHERE m.activo = 1
            AND c.activo = 1
            ORDER BY c.nombre ASC, m.nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        if not resultados:
            return []

        return [cls(mascota) for mascota in resultados]

    @classmethod
    def validar(cls, formulario):
        errores = []

        nombre = formulario.get("nombre", "").strip()
        especie = formulario.get("especie", "").strip()
        sexo = formulario.get("sexo", "").strip()
        tamano = formulario.get("tamano", "").strip()
        tipo_pelo = formulario.get("tipo_pelo", "").strip()
        fecha_nacimiento = formulario.get(
            "fecha_nacimiento",
            ""
        ).strip()
        peso_texto = formulario.get("peso", "").strip()
        esterilizado = formulario.get("esterilizado", "").strip()

        if len(nombre) < 2:
            errores.append(
                "El nombre de la mascota debe tener al menos 2 caracteres."
            )

        if especie not in cls.ESPECIES_VALIDAS:
            errores.append("Selecciona una especie válida.")

        if sexo not in cls.SEXOS_VALIDOS:
            errores.append("Selecciona un sexo válido.")

        if tamano not in cls.TAMANOS_VALIDOS:
            errores.append(
                "Selecciona el tamaño de la mascota."
            )

        if tipo_pelo not in cls.TIPOS_PELO_VALIDOS:
            errores.append(
                "Selecciona el tipo de pelo de la mascota."
            )

        if fecha_nacimiento:
            try:
                fecha = date.fromisoformat(fecha_nacimiento)

                if fecha > date.today():
                    errores.append(
                        "La fecha de nacimiento no puede estar en el futuro."
                    )

            except ValueError:
                errores.append(
                    "La fecha de nacimiento no es válida."
                )

        if peso_texto:
            try:
                peso = Decimal(peso_texto)

                if peso <= 0:
                    errores.append(
                        "El peso debe ser mayor que cero."
                    )

                if peso > 200:
                    errores.append(
                        "El peso registrado parece demasiado alto."
                    )

            except (InvalidOperation, ValueError):
                errores.append(
                    "El peso debe ser un número válido."
                )

        if esterilizado not in {"", "1", "0"}:
            errores.append(
                "Selecciona una opción válida para esterilización."
            )

        return errores