from app_flask.config.mysqlconnection import connectToMySQL
from app_flask import BASE_DATOS, EMAIL_REGEX


class Usuario:

    ROLES_VALIDOS = {
        "admin",
        "recepcion",
        "estilista"
    }

    def __init__(self, data):
        self.id_usuario = data["id_usuario"]
        self.nombre = data["nombre"]
        self.correo = data["correo"]
        self.password_hash = data.get("password_hash")
        self.rol = data["rol"]
        self.activo = data["activo"]
        self.fecha_creacion = data.get("fecha_creacion")

        self.es_estilista = data.get(
            "es_estilista",
            0
        )

        self.color_agenda = data.get(
            "color_agenda"
        )

        self.orden_agenda = data.get(
            "orden_agenda",
            0
        )

    ####################################################
    # CREAR USUARIO
    ####################################################

    @classmethod
    def crear(cls, data):
        query = """
            INSERT INTO usuarios (
                nombre,
                correo,
                password_hash,
                rol,
                activo,
                es_estilista,
                color_agenda,
                orden_agenda
            )
            VALUES (
                %(nombre)s,
                %(correo)s,
                %(password_hash)s,
                %(rol)s,
                1,
                %(es_estilista)s,
                %(color_agenda)s,
                %(orden_agenda)s
            );
        """

        return connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )

    @classmethod
    def obtener_por_correo(cls, data):
        query = """
            SELECT *
            FROM usuarios
            WHERE correo = %(correo)s
            LIMIT 1;
        """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, data)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_por_id(cls, data):
        query = """
            SELECT *
            FROM usuarios
            WHERE id_usuario = %(id_usuario)s
            LIMIT 1;
        """
        resultado = connectToMySQL(BASE_DATOS).query_db(query, data)

        if len(resultado) < 1:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_estilistas(cls):
        query = """
            SELECT
                id_usuario,
                nombre,
                correo,
                password_hash,
                rol,
                activo,
                fecha_creacion,
                es_estilista,
                color_agenda,
                orden_agenda
            FROM usuarios
            WHERE es_estilista = 1
            AND activo = 1
            ORDER BY
                COALESCE(orden_agenda, 999),
                nombre ASC;
        """

        resultados = connectToMySQL(
            BASE_DATOS
        ).query_db(query)

        if not resultados:
            return []

        return [
            cls(usuario)
            for usuario in resultados
        ]

    @staticmethod
    def validar_registro(data):
        errores = []

        if len(data["nombre"]) < 2:
            errores.append("El nombre debe tener al menos 2 caracteres.")

        if not EMAIL_REGEX.match(data["correo"]):
            errores.append("El correo electrónico no es válido.")

        if len(data["password"]) < 6:
            errores.append("La contraseña debe tener al menos 6 caracteres.")

        if data["password"] != data["confirmar_password"]:
            errores.append("Las contraseñas no coinciden.")

        if data["rol"] not in ["admin", "recepcion", "estilista"]:
            errores.append("El rol seleccionado no es válido.")

        usuario_existente = Usuario.obtener_por_correo({
            "correo": data["correo"]
        })

        if usuario_existente:
            errores.append("El correo ya está registrado.")

        return errores

    ####################################################
    # OBTENER TODOS LOS USUARIOS
    ####################################################

    @classmethod
    def obtener_todos(cls, termino=""):
        data = {
            "termino": f"%{termino.strip()}%"
        }

        query = """
            SELECT
                id_usuario,
                nombre,
                correo,
                password_hash,
                rol,
                activo,
                fecha_creacion,
                es_estilista,
                color_agenda,
                orden_agenda
            FROM usuarios
            WHERE (
                nombre LIKE %(termino)s
                OR correo LIKE %(termino)s
                OR rol LIKE %(termino)s
            )
            ORDER BY
                activo DESC,
                CASE rol
                    WHEN 'admin' THEN 1
                    WHEN 'recepcion' THEN 2
                    WHEN 'estilista' THEN 3
                    ELSE 4
                END,
                nombre ASC;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )

        if not resultado:
            return []

        return [
            cls(usuario)
            for usuario in resultado
        ]

    ####################################################
    # OBTENER USUARIO POR ID
    ####################################################

    @classmethod
    def obtener_por_id(cls, data):
        query = """
            SELECT
                id_usuario,
                nombre,
                correo,
                password_hash,
                rol,
                activo,
                fecha_creacion,
                es_estilista,
                color_agenda,
                orden_agenda
            FROM usuarios
            WHERE id_usuario = %(id_usuario)s
            LIMIT 1;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )

        if not resultado:
            return None

        return cls(resultado[0])

    ####################################################
    # VALIDAR CORREO REGISTRADO
    ####################################################

    @classmethod
    def correo_registrado(cls, correo):
        query = """
            SELECT id_usuario
            FROM usuarios
            WHERE correo = %(correo)s
            LIMIT 1;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "correo": correo
            }
        )

        return bool(resultado)

    ####################################################
    # VALIDAR CREACIÓN DE USUARIO
    ####################################################

    @classmethod
    def validar_creacion(cls, formulario):
        errores = []

        nombre = formulario.get(
            "nombre",
            ""
        ).strip()

        correo = formulario.get(
            "correo",
            ""
        ).strip().lower()

        password = formulario.get(
            "password",
            ""
        )

        confirmar_password = formulario.get(
            "confirmar_password",
            ""
        )

        rol = formulario.get(
            "rol",
            ""
        ).strip()

        es_estilista = (
            formulario.get("es_estilista") == "1"
        )

        color_agenda = formulario.get(
            "color_agenda",
            ""
        ).strip()

        orden_agenda = formulario.get(
            "orden_agenda",
            ""
        ).strip()

        if len(nombre) < 2:
            errores.append(
                "El nombre debe tener al menos 2 caracteres."
            )

        if not EMAIL_REGEX.match(correo):
            errores.append(
                "El correo electrónico no es válido."
            )

        elif cls.correo_registrado(correo):
            errores.append(
                "El correo electrónico ya está registrado."
            )

        if len(password) < 6:
            errores.append(
                "La contraseña debe tener al menos 6 caracteres."
            )

        if password != confirmar_password:
            errores.append(
                "Las contraseñas no coinciden."
            )

        if rol not in cls.ROLES_VALIDOS:
            errores.append(
                "El rol seleccionado no es válido."
            )

        if es_estilista:
            if not color_agenda:
                errores.append(
                    "Selecciona un color para el estilista."
                )

            try:
                orden = int(orden_agenda)

                if orden < 1:
                    errores.append(
                        "El orden de agenda debe ser mayor que cero."
                    )

            except (TypeError, ValueError):
                errores.append(
                    "El orden de agenda no es válido."
                )

        return errores

    ####################################################
    # VALIDAR CORREO EN OTRO USUARIO
    ####################################################

    @classmethod
    def correo_registrado_por_otro(cls, correo, id_usuario):
        query = """
            SELECT id_usuario
            FROM usuarios
            WHERE correo = %(correo)s
            AND id_usuario <> %(id_usuario)s
            LIMIT 1;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "correo": correo,
                "id_usuario": id_usuario
            }
        )

        return bool(resultado)

    ####################################################
    # VALIDAR EDICIÓN DE USUARIO
    ####################################################

    @classmethod
    def validar_edicion(cls, formulario, id_usuario):
        errores = []

        nombre = formulario.get(
            "nombre",
            ""
        ).strip()

        correo = formulario.get(
            "correo",
            ""
        ).strip().lower()

        rol = formulario.get(
            "rol",
            ""
        ).strip()

        es_estilista = (
            formulario.get("es_estilista") == "1"
            or rol == "estilista"
        )

        color_agenda = formulario.get(
            "color_agenda",
            ""
        ).strip()

        orden_agenda = formulario.get(
            "orden_agenda",
            ""
        ).strip()

        if len(nombre) < 2:
            errores.append(
                "El nombre debe tener al menos 2 caracteres."
            )

        if not EMAIL_REGEX.match(correo):
            errores.append(
                "El correo electrónico no es válido."
            )

        elif cls.correo_registrado_por_otro(
            correo,
            id_usuario
        ):
            errores.append(
                "El correo electrónico pertenece a otro usuario."
            )

        if rol not in cls.ROLES_VALIDOS:
            errores.append(
                "El rol seleccionado no es válido."
            )

        if es_estilista:
            if not color_agenda:
                errores.append(
                    "Selecciona un color para el estilista."
                )

            try:
                orden = int(orden_agenda)

                if orden < 1:
                    errores.append(
                        "El orden de agenda debe ser mayor que cero."
                    )

            except (TypeError, ValueError):
                errores.append(
                    "El orden de agenda no es válido."
                )

        return errores

    ####################################################
    # ACTUALIZAR USUARIO
    ####################################################

    @classmethod
    def actualizar(cls, data):
        query = """
            UPDATE usuarios
            SET
                nombre = %(nombre)s,
                correo = %(correo)s,
                rol = %(rol)s,
                es_estilista = %(es_estilista)s,
                color_agenda = %(color_agenda)s,
                orden_agenda = %(orden_agenda)s
            WHERE id_usuario = %(id_usuario)s;
        """

        return connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )

    ####################################################
    # CAMBIAR ESTADO DEL USUARIO
    ####################################################

    @classmethod
    def cambiar_estado(cls, data):
        query = """
            UPDATE usuarios
            SET activo = %(activo)s
            WHERE id_usuario = %(id_usuario)s;
        """

        return connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )

    ####################################################
    # CONTAR ADMINISTRADORES ACTIVOS
    ####################################################

    @classmethod
    def contar_administradores_activos(cls):
        query = """
            SELECT COUNT(*) AS total
            FROM usuarios
            WHERE rol = 'admin'
            AND activo = 1;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(query)

        if not resultado:
            return 0

        return resultado[0]["total"]

    ####################################################
    # ACTUALIZAR CONTRASEÑA
    ####################################################

    @classmethod
    def actualizar_password(cls, data):
        query = """
            UPDATE usuarios
            SET password_hash = %(password_hash)s
            WHERE id_usuario = %(id_usuario)s;
        """

        return connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )