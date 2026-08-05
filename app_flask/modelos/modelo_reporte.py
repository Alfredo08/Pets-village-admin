from app_flask import BASE_DATOS
from app_flask.config.mysqlconnection import connectToMySQL


class Reporte:

    ####################################################
    # INVENTARIO ACTUAL
    ####################################################

    @classmethod
    def obtener_inventario(cls):
        query = """
            SELECT
                p.id_producto,
                p.nombre,
                p.codigo_barras,
                p.stock_actual,
                p.stock_minimo,
                p.precio_compra,
                p.precio_venta,
                p.activo,

                c.nombre AS nombre_categoria

            FROM productos p

            LEFT JOIN categorias_productos c
                ON c.id_categoria = p.id_categoria

            WHERE p.activo = 1

            ORDER BY
                c.nombre ASC,
                p.nombre ASC;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(query)

        return resultado or []


    ####################################################
    # RESUMEN DE INVENTARIO
    ####################################################

    @classmethod
    def obtener_resumen_inventario(cls):
        query = """
            SELECT
                COUNT(*) AS productos_activos,

                COALESCE(
                    SUM(
                        CASE
                            WHEN stock_actual = 0
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS productos_sin_stock,

                COALESCE(
                    SUM(
                        CASE
                            WHEN stock_actual > 0
                             AND stock_actual <= stock_minimo
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS productos_stock_bajo,

                COALESCE(
                    SUM(stock_actual),
                    0
                ) AS unidades_totales,

                COALESCE(
                    SUM(
                        stock_actual * precio_compra
                    ),
                    0
                ) AS valor_compra,

                COALESCE(
                    SUM(
                        stock_actual * precio_venta
                    ),
                    0
                ) AS valor_venta

            FROM productos

            WHERE activo = 1;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(query)

        if not resultado:
            return {
                "productos_activos": 0,
                "productos_sin_stock": 0,
                "productos_stock_bajo": 0,
                "unidades_totales": 0,
                "valor_compra": 0,
                "valor_venta": 0
            }

        return resultado[0]

    ####################################################
    # VENTAS POR RANGO DE FECHAS
    ####################################################

    @classmethod
    def obtener_ventas(
        cls,
        fecha_inicio,
        fecha_fin
    ):
        query = """
            SELECT
                v.id_venta,
                v.folio,
                v.tipo_venta,
                v.subtotal,
                v.descuento,
                v.impuestos,
                v.total,
                v.estado,
                v.fecha_creacion,

                os.folio AS folio_orden,

                COALESCE(
                    c.nombre,
                    v.nombre_cliente_rapido,
                    'Público general'
                ) AS nombre_cliente,

                m.nombre AS nombre_mascota,

                u.nombre AS nombre_usuario,

                GROUP_CONCAT(
                    DISTINCT
                    CASE p.metodo
                        WHEN 'efectivo'
                            THEN 'Efectivo'
                        WHEN 'tarjeta'
                            THEN 'Tarjeta'
                        WHEN 'transferencia'
                            THEN 'Transferencia'
                        ELSE p.metodo
                    END

                    ORDER BY FIELD(
                        p.metodo,
                        'efectivo',
                        'tarjeta',
                        'transferencia'
                    )

                    SEPARATOR ' + '
                ) AS metodos_pago

            FROM ventas v

            LEFT JOIN ordenes_servicio os
                ON os.id_orden = v.id_orden

            LEFT JOIN clientes c
                ON c.id_cliente = v.id_cliente

            LEFT JOIN mascotas m
                ON m.id_mascota = v.id_mascota

            INNER JOIN usuarios u
                ON u.id_usuario = v.id_usuario

            LEFT JOIN pagos p
                ON p.id_venta = v.id_venta

            WHERE DATE(v.fecha_creacion)
                BETWEEN %(fecha_inicio)s
                AND %(fecha_fin)s

            AND v.estado = 'completada'

            GROUP BY
                v.id_venta,
                v.folio,
                v.tipo_venta,
                v.subtotal,
                v.descuento,
                v.impuestos,
                v.total,
                v.estado,
                v.fecha_creacion,
                os.folio,
                c.nombre,
                v.nombre_cliente_rapido,
                m.nombre,
                u.nombre

            ORDER BY
                v.fecha_creacion DESC,
                v.id_venta DESC;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            }
        )

        return resultado or []


    ####################################################
    # RESUMEN DE VENTAS
    ####################################################

    @classmethod
    def obtener_resumen_ventas(
        cls,
        fecha_inicio,
        fecha_fin
    ):
        query = """
            SELECT
                COUNT(*) AS cantidad_ventas,

                COALESCE(
                    SUM(total),
                    0
                ) AS total_vendido,

                COALESCE(
                    AVG(total),
                    0
                ) AS promedio_venta,

                COALESCE(
                    SUM(
                        CASE
                            WHEN tipo_venta = 'servicio'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS cantidad_servicios,

                COALESCE(
                    SUM(
                        CASE
                            WHEN tipo_venta = 'servicio'
                            THEN total
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_servicios,

                COALESCE(
                    SUM(
                        CASE
                            WHEN tipo_venta = 'rapida'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS cantidad_ventas_rapidas,

                COALESCE(
                    SUM(
                        CASE
                            WHEN tipo_venta = 'rapida'
                            THEN total
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_ventas_rapidas,

                COALESCE(
                    SUM(descuento),
                    0
                ) AS descuentos_totales,

                COALESCE(
                    SUM(impuestos),
                    0
                ) AS impuestos_totales

            FROM ventas

            WHERE DATE(fecha_creacion)
                BETWEEN %(fecha_inicio)s
                AND %(fecha_fin)s

            AND estado = 'completada';
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            }
        )

        if not resultado:
            return {
                "cantidad_ventas": 0,
                "total_vendido": 0,
                "promedio_venta": 0,
                "cantidad_servicios": 0,
                "total_servicios": 0,
                "cantidad_ventas_rapidas": 0,
                "total_ventas_rapidas": 0,
                "descuentos_totales": 0,
                "impuestos_totales": 0
            }

        return resultado[0]


    ####################################################
    # RESUMEN POR MÉTODO DE PAGO
    ####################################################

    @classmethod
    def obtener_resumen_metodos_pago(
        cls,
        fecha_inicio,
        fecha_fin
    ):
        query = """
            SELECT
                COALESCE(
                    SUM(
                        CASE
                            WHEN p.metodo = 'efectivo'
                            THEN p.monto
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_efectivo,

                COUNT(
                    DISTINCT
                    CASE
                        WHEN p.metodo = 'efectivo'
                        THEN p.id_venta
                    END
                ) AS operaciones_efectivo,

                COALESCE(
                    SUM(
                        CASE
                            WHEN p.metodo = 'tarjeta'
                            THEN p.monto
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_tarjeta,

                COUNT(
                    DISTINCT
                    CASE
                        WHEN p.metodo = 'tarjeta'
                        THEN p.id_venta
                    END
                ) AS operaciones_tarjeta,

                COALESCE(
                    SUM(
                        CASE
                            WHEN p.metodo = 'transferencia'
                            THEN p.monto
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_transferencia,

                COUNT(
                    DISTINCT
                    CASE
                        WHEN p.metodo = 'transferencia'
                        THEN p.id_venta
                    END
                ) AS operaciones_transferencia

            FROM pagos p

            INNER JOIN ventas v
                ON v.id_venta = p.id_venta

            WHERE DATE(v.fecha_creacion)
                BETWEEN %(fecha_inicio)s
                AND %(fecha_fin)s

            AND v.estado = 'completada';
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            }
        )

        if not resultado:
            return {
                "total_efectivo": 0,
                "operaciones_efectivo": 0,
                "total_tarjeta": 0,
                "operaciones_tarjeta": 0,
                "total_transferencia": 0,
                "operaciones_transferencia": 0
            }

        return resultado[0]

    ####################################################
    # RESUMEN DE CAJA DEL DÍA
    ####################################################

    @classmethod
    def obtener_resumen_caja(cls, fecha):
        query = """
            SELECT
                COUNT(*) AS cantidad_ventas,

                COALESCE(
                    SUM(total),
                    0
                ) AS total_vendido,

                COALESCE(
                    AVG(total),
                    0
                ) AS promedio_venta,

                COALESCE(
                    SUM(
                        CASE
                            WHEN tipo_venta = 'servicio'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS ventas_servicio,

                COALESCE(
                    SUM(
                        CASE
                            WHEN tipo_venta = 'servicio'
                            THEN total
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_servicio,

                COALESCE(
                    SUM(
                        CASE
                            WHEN tipo_venta = 'rapida'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS ventas_rapidas,

                COALESCE(
                    SUM(
                        CASE
                            WHEN tipo_venta = 'rapida'
                            THEN total
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_ventas_rapidas,

                COALESCE(
                    SUM(descuento),
                    0
                ) AS descuentos_totales,

                COALESCE(
                    SUM(impuestos),
                    0
                ) AS impuestos_totales

            FROM ventas

            WHERE DATE(fecha_creacion) = %(fecha)s
            AND estado = 'completada';
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "fecha": fecha
            }
        )

        if not resultado:
            return {
                "cantidad_ventas": 0,
                "total_vendido": 0,
                "promedio_venta": 0,
                "ventas_servicio": 0,
                "total_servicio": 0,
                "ventas_rapidas": 0,
                "total_ventas_rapidas": 0,
                "descuentos_totales": 0,
                "impuestos_totales": 0
            }

        return resultado[0]


    ####################################################
    # MÉTODOS DE PAGO DE CAJA
    ####################################################

    @classmethod
    def obtener_metodos_pago_caja(cls, fecha):
        query = """
            SELECT
                COALESCE(
                    SUM(
                        CASE
                            WHEN p.metodo = 'efectivo'
                            THEN p.monto
                            ELSE 0
                        END
                    ),
                    0
                ) AS efectivo,

                COUNT(
                    DISTINCT
                    CASE
                        WHEN p.metodo = 'efectivo'
                        THEN p.id_venta
                    END
                ) AS operaciones_efectivo,

                COALESCE(
                    SUM(
                        CASE
                            WHEN p.metodo = 'tarjeta'
                            THEN p.monto
                            ELSE 0
                        END
                    ),
                    0
                ) AS tarjeta,

                COUNT(
                    DISTINCT
                    CASE
                        WHEN p.metodo = 'tarjeta'
                        THEN p.id_venta
                    END
                ) AS operaciones_tarjeta,

                COALESCE(
                    SUM(
                        CASE
                            WHEN p.metodo = 'transferencia'
                            THEN p.monto
                            ELSE 0
                        END
                    ),
                    0
                ) AS transferencia,

                COUNT(
                    DISTINCT
                    CASE
                        WHEN p.metodo = 'transferencia'
                        THEN p.id_venta
                    END
                ) AS operaciones_transferencia

            FROM pagos p

            INNER JOIN ventas v
                ON v.id_venta = p.id_venta

            WHERE DATE(v.fecha_creacion) = %(fecha)s
            AND v.estado = 'completada';
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "fecha": fecha
            }
        )

        if not resultado:
            return {
                "efectivo": 0,
                "operaciones_efectivo": 0,
                "tarjeta": 0,
                "operaciones_tarjeta": 0,
                "transferencia": 0,
                "operaciones_transferencia": 0
            }

        return resultado[0]


    ####################################################
    # CONCEPTOS VENDIDOS EN CAJA
    ####################################################

    @classmethod
    def obtener_conceptos_caja(cls, fecha):
        query = """
            SELECT
                COALESCE(
                    SUM(
                        CASE
                            WHEN vd.tipo = 'servicio'
                            THEN vd.cantidad
                            ELSE 0
                        END
                    ),
                    0
                ) AS cantidad_servicios,

                COALESCE(
                    SUM(
                        CASE
                            WHEN vd.tipo = 'servicio'
                            THEN vd.subtotal
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_servicios,

                COALESCE(
                    SUM(
                        CASE
                            WHEN vd.tipo = 'producto'
                            THEN vd.cantidad
                            ELSE 0
                        END
                    ),
                    0
                ) AS cantidad_productos,

                COALESCE(
                    SUM(
                        CASE
                            WHEN vd.tipo = 'producto'
                            THEN vd.subtotal
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_productos

            FROM venta_detalles vd

            INNER JOIN ventas v
                ON v.id_venta = vd.id_venta

            WHERE DATE(v.fecha_creacion) = %(fecha)s
            AND v.estado = 'completada';
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "fecha": fecha
            }
        )

        if not resultado:
            return {
                "cantidad_servicios": 0,
                "total_servicios": 0,
                "cantidad_productos": 0,
                "total_productos": 0
            }

        return resultado[0]


    ####################################################
    # DETALLE DE CAJA DEL DÍA
    ####################################################

    @classmethod
    def obtener_ventas_caja(cls, fecha):
        query = """
            SELECT
                v.id_venta,
                v.folio,
                v.tipo_venta,
                v.total,
                v.fecha_creacion,

                os.folio AS folio_orden,

                COALESCE(
                    c.nombre,
                    v.nombre_cliente_rapido,
                    'Público general'
                ) AS nombre_cliente,

                m.nombre AS nombre_mascota,

                u.nombre AS nombre_usuario,

                GROUP_CONCAT(
                    DISTINCT
                    CASE p.metodo
                        WHEN 'efectivo'
                            THEN 'Efectivo'
                        WHEN 'tarjeta'
                            THEN 'Tarjeta'
                        WHEN 'transferencia'
                            THEN 'Transferencia'
                        ELSE p.metodo
                    END

                    ORDER BY FIELD(
                        p.metodo,
                        'efectivo',
                        'tarjeta',
                        'transferencia'
                    )

                    SEPARATOR ' + '
                ) AS metodos_pago

            FROM ventas v

            LEFT JOIN ordenes_servicio os
                ON os.id_orden = v.id_orden

            LEFT JOIN clientes c
                ON c.id_cliente = v.id_cliente

            LEFT JOIN mascotas m
                ON m.id_mascota = v.id_mascota

            INNER JOIN usuarios u
                ON u.id_usuario = v.id_usuario

            LEFT JOIN pagos p
                ON p.id_venta = v.id_venta

            WHERE DATE(v.fecha_creacion) = %(fecha)s
            AND v.estado = 'completada'

            GROUP BY
                v.id_venta,
                v.folio,
                v.tipo_venta,
                v.total,
                v.fecha_creacion,
                os.folio,
                c.nombre,
                v.nombre_cliente_rapido,
                m.nombre,
                u.nombre

            ORDER BY
                v.fecha_creacion ASC,
                v.id_venta ASC;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "fecha": fecha
            }
        )

        return resultado or []


    ####################################################
    # PRODUCTOS VENDIDOS EN CAJA
    ####################################################

    @classmethod
    def obtener_productos_vendidos_caja(cls, fecha):
        query = """
            SELECT
                vd.descripcion,

                SUM(vd.cantidad) AS cantidad,

                SUM(vd.subtotal) AS total

            FROM venta_detalles vd

            INNER JOIN ventas v
                ON v.id_venta = vd.id_venta

            WHERE DATE(v.fecha_creacion) = %(fecha)s
            AND v.estado = 'completada'
            AND vd.tipo = 'producto'

            GROUP BY
                vd.id_producto,
                vd.descripcion

            ORDER BY
                cantidad DESC,
                vd.descripcion ASC;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "fecha": fecha
            }
        )

        return resultado or []


    ####################################################
    # SERVICIOS VENDIDOS EN CAJA
    ####################################################

    @classmethod
    def obtener_servicios_vendidos_caja(cls, fecha):
        query = """
            SELECT
                vd.descripcion,

                SUM(vd.cantidad) AS cantidad,

                SUM(vd.subtotal) AS total

            FROM venta_detalles vd

            INNER JOIN ventas v
                ON v.id_venta = vd.id_venta

            WHERE DATE(v.fecha_creacion) = %(fecha)s
            AND v.estado = 'completada'
            AND vd.tipo = 'servicio'

            GROUP BY
                vd.id_servicio,
                vd.descripcion

            ORDER BY
                cantidad DESC,
                vd.descripcion ASC;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "fecha": fecha
            }
        )

        return resultado or []