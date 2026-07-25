from app_flask import BASE_DATOS
from app_flask.config.mysqlconnection import connectToMySQL


class CategoriaProducto:
    def __init__(self, data):
        self.id_categoria = data["id_categoria"]
        self.nombre = data["nombre"]
        self.activo = data["activo"]

    @classmethod
    def obtener_activas(cls):
        query = """
            SELECT id_categoria, nombre, activo
            FROM categorias_productos
            WHERE activo = 1
            ORDER BY nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        if not resultados:
            return []

        return [cls(categoria) for categoria in resultados]

    @classmethod
    def obtener_todas(cls):
        query = """
            SELECT id_categoria, nombre, activo
            FROM categorias_productos
            ORDER BY nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        if not resultados:
            return []

        return [cls(categoria) for categoria in resultados]

    @classmethod
    def crear(cls, data):
        query = """
            INSERT INTO categorias_productos (nombre, activo)
            VALUES (%(nombre)s, 1);
        """

        return connectToMySQL(BASE_DATOS).query_db(query, data)