from app_flask import BASE_DATOS, EMAIL_REGEX
from app_flask.config.mysqlconnection import connectToMySQL


class Cliente:

    def __init__(self, data):

        self.id_cliente = data["id_cliente"]
        self.nombre = data["nombre"]
        self.telefono = data.get("telefono")
        self.correo = data.get("correo")
        self.observaciones = data.get("observaciones")
        self.activo = data["activo"]
        self.fecha_registro = data.get("fecha_registro")

        # Para el listado
        self.total_mascotas = data.get("total_mascotas", 0)

    ####################################################
    # OBTENER TODOS
    ####################################################

    @classmethod
    def obtener_todos(cls, termino=""):

        query = """
            SELECT
                c.*,
                COUNT(m.id_mascota) AS total_mascotas

            FROM clientes c

            LEFT JOIN mascotas m
                ON c.id_cliente = m.id_cliente
                AND m.activo = 1

            WHERE

                c.nombre LIKE %(buscar)s

                OR IFNULL(c.telefono,'')
                LIKE %(buscar)s

                OR IFNULL(c.correo,'')
                LIKE %(buscar)s

            GROUP BY c.id_cliente

            ORDER BY
                c.activo DESC,
                c.nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(
            query,
            {
                "buscar": f"%{termino}%"
            }
        )

        if not resultados:
            return []

        return [cls(cliente) for cliente in resultados]

    ####################################################
    # OBTENER UNO
    ####################################################

    @classmethod
    def obtener_por_id(cls, data):

        query = """
            SELECT *
            FROM clientes
            WHERE id_cliente=%(id_cliente)s
            LIMIT 1;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, data)

        if not resultado:
            return None

        return cls(resultado[0])

    ####################################################
    # CREAR
    ####################################################

    @classmethod
    def crear(cls, data):

        query = """
            INSERT INTO clientes(

                nombre,
                telefono,
                correo,
                observaciones,
                activo

            )

            VALUES(

                %(nombre)s,
                %(telefono)s,
                %(correo)s,
                %(observaciones)s,
                1

            );
        """

        return connectToMySQL(BASE_DATOS).query_db(query, data)

    ####################################################
    # ACTUALIZAR
    ####################################################

    @classmethod
    def actualizar(cls, data):

        query = """
            UPDATE clientes

            SET

                nombre=%(nombre)s,
                telefono=%(telefono)s,
                correo=%(correo)s,
                observaciones=%(observaciones)s

            WHERE id_cliente=%(id_cliente)s;
        """

        return connectToMySQL(BASE_DATOS).query_db(query, data)

    ####################################################
    # CAMBIAR ESTADO
    ####################################################

    @classmethod
    def cambiar_estado(cls, data):

        query = """
            UPDATE clientes

            SET activo=%(activo)s

            WHERE id_cliente=%(id_cliente)s;
        """

        return connectToMySQL(BASE_DATOS).query_db(query, data)

    ####################################################
    # VALIDAR
    ####################################################

    @staticmethod
    def validar(formulario):

        errores = []

        nombre = formulario["nombre"].strip()
        telefono = formulario["telefono"].strip()
        correo = formulario["correo"].strip()

        if len(nombre) < 3:
            errores.append(
                "El nombre debe tener al menos 3 caracteres."
            )

        if telefono:

            if len(telefono) < 8:

                errores.append(
                    "El teléfono parece ser incorrecto."
                )

        if correo:

            if not EMAIL_REGEX.match(correo):

                errores.append(
                    "El correo electrónico no es válido."
                )

        return errores