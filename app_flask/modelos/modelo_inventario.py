from app_flask import BASE_DATOS
from app_flask.config.mysqlconnection import connectToMySQL


class MovimientoInventario:
    def __init__(self, data):
        self.id_movimiento = data["id_movimiento"]
        self.id_producto = data["id_producto"]
        self.id_usuario = data["id_usuario"]
        self.tipo_movimiento = data["tipo_movimiento"]
        self.cantidad = data["cantidad"]
        self.motivo = data.get("motivo")
        self.id_orden = data.get("id_orden")
        self.fecha_movimiento = data["fecha_movimiento"]
        self.observaciones = data.get("observaciones")

        self.nombre_producto = data.get("nombre_producto")
        self.codigo_barras = data.get("codigo_barras")
        self.nombre_usuario = data.get("nombre_usuario")

    @classmethod
    def obtener_movimientos(cls, termino=""):
        query = """
            SELECT
                im.id_movimiento,
                im.id_producto,
                im.id_usuario,
                im.tipo_movimiento,
                im.cantidad,
                im.motivo,
                im.id_orden,
                im.fecha_movimiento,
                im.observaciones,
                p.nombre AS nombre_producto,
                p.codigo_barras,
                u.nombre AS nombre_usuario
            FROM inventario_movimientos im
            INNER JOIN productos p
                ON p.id_producto = im.id_producto
            INNER JOIN usuarios u
                ON u.id_usuario = im.id_usuario
            WHERE (
                p.nombre LIKE %(termino)s
                OR p.codigo_barras LIKE %(termino)s
                OR im.motivo LIKE %(termino)s
            )
            ORDER BY im.fecha_movimiento DESC,
                     im.id_movimiento DESC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(
            query,
            {"termino": f"%{termino.strip()}%"}
        )

        if not resultados:
            return []

        return [cls(movimiento) for movimiento in resultados]

    @classmethod
    def obtener_resumen_productos(cls):
        query = """
            SELECT
                p.id_producto,
                p.nombre,
                p.codigo_barras,
                p.stock_actual,
                p.stock_minimo,
                c.nombre AS nombre_categoria
            FROM productos p
            LEFT JOIN categorias_productos c
                ON c.id_categoria = p.id_categoria
            WHERE p.activo = 1
            ORDER BY p.nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        return resultados if resultados else []

    @classmethod
    def registrar(cls, data):
        """
        Registra el movimiento y modifica el stock en una sola transacción.
        """

        conexion_mysql = connectToMySQL(BASE_DATOS)
        conexion = conexion_mysql.connection

        try:
            conexion.begin()

            with conexion.cursor() as cursor:
                # Bloquea temporalmente el producto para impedir que dos
                # movimientos modifiquen el stock al mismo tiempo.
                query_producto = """
                    SELECT id_producto, nombre, stock_actual
                    FROM productos
                    WHERE id_producto = %(id_producto)s
                      AND activo = 1
                    FOR UPDATE;
                """

                cursor.execute(query_producto, {
                    "id_producto": data["id_producto"]
                })

                producto = cursor.fetchone()

                if not producto:
                    conexion.rollback()

                    return {
                        "exito": False,
                        "mensaje": "El producto no existe o está inactivo."
                    }

                stock_actual = producto["stock_actual"]
                cantidad = data["cantidad"]
                tipo = data["tipo_movimiento"]

                if tipo == "entrada":
                    nuevo_stock = stock_actual + cantidad

                elif tipo == "salida":
                    if cantidad > stock_actual:
                        conexion.rollback()

                        return {
                            "exito": False,
                            "mensaje": (
                                f"No hay existencia suficiente. "
                                f"Stock actual: {stock_actual}."
                            )
                        }

                    nuevo_stock = stock_actual - cantidad

                elif tipo == "ajuste":
                    # En un ajuste, cantidad puede ser positiva o negativa.
                    nuevo_stock = stock_actual + cantidad

                    if nuevo_stock < 0:
                        conexion.rollback()

                        return {
                            "exito": False,
                            "mensaje": (
                                "El ajuste dejaría el producto "
                                "con existencia negativa."
                            )
                        }

                else:
                    conexion.rollback()

                    return {
                        "exito": False,
                        "mensaje": "El tipo de movimiento no es válido."
                    }

                query_movimiento = """
                    INSERT INTO inventario_movimientos (
                        id_producto,
                        id_usuario,
                        tipo_movimiento,
                        cantidad,
                        motivo,
                        id_orden,
                        observaciones
                    )
                    VALUES (
                        %(id_producto)s,
                        %(id_usuario)s,
                        %(tipo_movimiento)s,
                        %(cantidad)s,
                        %(motivo)s,
                        NULL,
                        %(observaciones)s
                    );
                """

                cursor.execute(query_movimiento, data)
                id_movimiento = cursor.lastrowid

                query_stock = """
                    UPDATE productos
                    SET stock_actual = %(nuevo_stock)s
                    WHERE id_producto = %(id_producto)s;
                """

                cursor.execute(query_stock, {
                    "nuevo_stock": nuevo_stock,
                    "id_producto": data["id_producto"]
                })

            conexion.commit()

            return {
                "exito": True,
                "id_movimiento": id_movimiento,
                "nuevo_stock": nuevo_stock
            }

        except Exception as error:
            conexion.rollback()
            print("Error en movimiento de inventario:", error)

            return {
                "exito": False,
                "mensaje": "No fue posible registrar el movimiento."
            }

        finally:
            conexion.close()

    @staticmethod
    def validar(formulario):
        errores = []

        tipo = formulario.get("tipo_movimiento", "").strip()
        cantidad_texto = formulario.get("cantidad", "").strip()
        id_producto = formulario.get("id_producto", "").strip()
        motivo = formulario.get("motivo", "").strip()

        if not id_producto.isdigit():
            errores.append("Selecciona un producto válido.")

        if tipo not in ("entrada", "salida", "ajuste"):
            errores.append("Selecciona un tipo de movimiento válido.")

        try:
            cantidad = int(cantidad_texto)

            if tipo in ("entrada", "salida") and cantidad <= 0:
                errores.append(
                    "La cantidad debe ser mayor que cero."
                )

            if tipo == "ajuste" and cantidad == 0:
                errores.append(
                    "La cantidad del ajuste no puede ser cero."
                )

        except (ValueError, TypeError):
            errores.append(
                "La cantidad debe ser un número entero."
            )

        if len(motivo) < 3:
            errores.append(
                "Indica el motivo del movimiento."
            )

        return errores