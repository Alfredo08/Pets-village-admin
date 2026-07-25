from decimal import Decimal, InvalidOperation

from app_flask import BASE_DATOS
from app_flask.config.mysqlconnection import connectToMySQL


class Producto:
    CAMPOS_REQUERIDOS = (
        "nombre",
        "precio_compra",
        "precio_venta",
        "stock_minimo",
    )

    def __init__(self, data):
        self.id_producto = data["id_producto"]
        self.id_categoria = data.get("id_categoria")
        self.nombre = data["nombre"]
        self.descripcion = data.get("descripcion")
        self.codigo_barras = data.get("codigo_barras")
        self.precio_compra = data["precio_compra"]
        self.precio_venta = data["precio_venta"]
        self.stock_actual = data["stock_actual"]
        self.stock_minimo = data["stock_minimo"]
        self.activo = data["activo"]
        self.fecha_creacion = data.get("fecha_creacion")
        self.nombre_categoria = data.get("nombre_categoria")

    @classmethod
    def obtener_todos(cls, termino=""):
        data = {
            "termino": f"%{termino.strip()}%"
        }

        query = """
            SELECT
                p.id_producto,
                p.id_categoria,
                p.nombre,
                p.descripcion,
                p.codigo_barras,
                p.precio_compra,
                p.precio_venta,
                p.stock_actual,
                p.stock_minimo,
                p.activo,
                p.fecha_creacion,
                c.nombre AS nombre_categoria
            FROM productos p
            LEFT JOIN categorias_productos c
                ON c.id_categoria = p.id_categoria
            WHERE (
                p.nombre LIKE %(termino)s
                OR p.codigo_barras LIKE %(termino)s
                OR c.nombre LIKE %(termino)s
            )
            ORDER BY p.activo DESC, p.nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(query, data)

        if not resultados:
            return []

        return [cls(producto) for producto in resultados]

    @classmethod
    def obtener_por_id(cls, data):
        query = """
            SELECT
                p.id_producto,
                p.id_categoria,
                p.nombre,
                p.descripcion,
                p.codigo_barras,
                p.precio_compra,
                p.precio_venta,
                p.stock_actual,
                p.stock_minimo,
                p.activo,
                p.fecha_creacion,
                c.nombre AS nombre_categoria
            FROM productos p
            LEFT JOIN categorias_productos c
                ON c.id_categoria = p.id_categoria
            WHERE p.id_producto = %(id_producto)s
            LIMIT 1;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, data)

        if not resultado:
            return None

        return cls(resultado[0])

    @classmethod
    def obtener_por_codigo_barras(cls, data):
        query = """
            SELECT
                p.id_producto,
                p.id_categoria,
                p.nombre,
                p.descripcion,
                p.codigo_barras,
                p.precio_compra,
                p.precio_venta,
                p.stock_actual,
                p.stock_minimo,
                p.activo,
                p.fecha_creacion
            FROM productos p
            WHERE p.codigo_barras = %(codigo_barras)s
            LIMIT 1;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, data)

        if not resultado:
            return None

        return cls(resultado[0])

    @classmethod
    def crear(cls, data):
        query = """
            INSERT INTO productos (
                id_categoria,
                nombre,
                descripcion,
                codigo_barras,
                precio_compra,
                precio_venta,
                stock_actual,
                stock_minimo,
                activo
            )
            VALUES (
                %(id_categoria)s,
                %(nombre)s,
                %(descripcion)s,
                %(codigo_barras)s,
                %(precio_compra)s,
                %(precio_venta)s,
                0,
                %(stock_minimo)s,
                1
            );
        """

        return connectToMySQL(BASE_DATOS).query_db(query, data)

    @classmethod
    def actualizar(cls, data):
        query = """
            UPDATE productos
            SET
                id_categoria = %(id_categoria)s,
                nombre = %(nombre)s,
                descripcion = %(descripcion)s,
                codigo_barras = %(codigo_barras)s,
                precio_compra = %(precio_compra)s,
                precio_venta = %(precio_venta)s,
                stock_minimo = %(stock_minimo)s
            WHERE id_producto = %(id_producto)s;
        """

        return connectToMySQL(BASE_DATOS).query_db(query, data)

    @classmethod
    def cambiar_estado(cls, data):
        query = """
            UPDATE productos
            SET activo = %(activo)s
            WHERE id_producto = %(id_producto)s;
        """

        return connectToMySQL(BASE_DATOS).query_db(query, data)

    ####################################################
    # OBTENER PRODUCTOS DISPONIBLES PARA EL POS
    ####################################################

    @classmethod
    def obtener_disponibles_pos(cls):
        query = """
            SELECT
                p.id_producto,
                p.id_categoria,
                p.nombre,
                p.descripcion,
                p.codigo_barras,
                p.precio_compra,
                p.precio_venta,
                p.stock_actual,
                p.stock_minimo,
                p.activo,
                p.fecha_creacion,
                c.nombre AS nombre_categoria
            FROM productos p
            LEFT JOIN categorias_productos c
                ON c.id_categoria = p.id_categoria
            WHERE p.activo = 1
            AND p.stock_actual > 0
            ORDER BY
                c.nombre ASC,
                p.nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        if not resultados:
            return []

        return resultados

    @staticmethod
    def validar(formulario, producto_actual=None):
        errores = []

        nombre = formulario.get("nombre", "").strip()
        codigo_barras = formulario.get("codigo_barras", "").strip()
        precio_compra = formulario.get("precio_compra", "").strip()
        precio_venta = formulario.get("precio_venta", "").strip()
        stock_minimo = formulario.get("stock_minimo", "").strip()

        if len(nombre) < 2:
            errores.append(
                "El nombre del producto debe tener al menos 2 caracteres."
            )

        try:
            compra = Decimal(precio_compra)

            if compra < 0:
                errores.append(
                    "El precio de compra no puede ser negativo."
                )
        except (InvalidOperation, TypeError):
            errores.append("El precio de compra no es válido.")

        try:
            venta = Decimal(precio_venta)

            if venta < 0:
                errores.append(
                    "El precio de venta no puede ser negativo."
                )
        except (InvalidOperation, TypeError):
            errores.append("El precio de venta no es válido.")

        try:
            minimo = int(stock_minimo)

            if minimo < 0:
                errores.append(
                    "El stock mínimo no puede ser negativo."
                )
        except (ValueError, TypeError):
            errores.append("El stock mínimo debe ser un número entero.")

        if codigo_barras:
            producto_codigo = Producto.obtener_por_codigo_barras({
                "codigo_barras": codigo_barras
            })

            if producto_codigo:
                es_el_mismo = (
                    producto_actual
                    and producto_codigo.id_producto
                    == producto_actual.id_producto
                )

                if not es_el_mismo:
                    errores.append(
                        "El código de barras ya pertenece a otro producto."
                    )

        return errores