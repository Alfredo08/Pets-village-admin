from app_flask.config.mysqlconnection import connectToMySQL
from app_flask import BASE_DATOS, EMAIL_REGEX


class Usuario:
    def __init__(self, data):
        self.id_usuario = data["id_usuario"]
        self.nombre = data["nombre"]
        self.correo = data["correo"]
        self.password_hash = data["password_hash"]
        self.rol = data["rol"]
        self.activo = data["activo"]
        self.es_estilista = data["es_estilista"]
        self.color_agenda = data["color_agenda"]
        self.orden_agenda = data.get("orden_agenda", 0)
        self.fecha_creacion = data["fecha_creacion"]

    @classmethod
    def crear(cls, data):
        query = """
            INSERT INTO usuarios (nombre, correo, password_hash, rol)
            VALUES (%(nombre)s, %(correo)s, %(password_hash)s, %(rol)s);
        """
        return connectToMySQL(BASE_DATOS).query_db(query, data)

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
                rol,
                activo,
                es_estilista,
                color_agenda,
                orden_agenda
            FROM usuarios
            WHERE rol = 'estilista'
            AND activo = 1
            ORDER BY orden_agenda ASC, nombre ASC;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(query)

        if not resultado:
            return []

        return resultado

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