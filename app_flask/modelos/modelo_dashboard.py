from app_flask import BASE_DATOS
from app_flask.config.mysqlconnection import connectToMySQL


class Dashboard:

    ####################################################
    # INDICADORES GENERALES DEL DÍA
    ####################################################

    @classmethod
    def obtener_resumen_dia(cls, fecha):
        query = """
            SELECT
                (
                    SELECT COUNT(*)
                    FROM ventas
                    WHERE DATE(fecha_creacion) = %(fecha)s
                      AND estado = 'completada'
                ) AS cantidad_ventas,

                (
                    SELECT COALESCE(SUM(total), 0)
                    FROM ventas
                    WHERE DATE(fecha_creacion) = %(fecha)s
                      AND estado = 'completada'
                ) AS total_vendido,

                (
                    SELECT COUNT(*)
                    FROM ordenes_servicio
                    WHERE fecha = %(fecha)s
                      AND estado NOT IN (
                          'cancelada',
                          'no_asistio'
                      )
                ) AS citas_programadas,

                (
                    SELECT COUNT(*)
                    FROM ordenes_servicio
                    WHERE fecha = %(fecha)s
                      AND estado = 'pendiente'
                ) AS ordenes_pendientes,

                (
                    SELECT COUNT(*)
                    FROM ordenes_servicio
                    WHERE fecha = %(fecha)s
                      AND estado = 'confirmada'
                ) AS ordenes_confirmadas,

                (
                    SELECT COUNT(*)
                    FROM ordenes_servicio
                    WHERE fecha = %(fecha)s
                      AND estado = 'en_proceso'
                ) AS ordenes_en_proceso,

                (
                    SELECT COUNT(*)
                    FROM ordenes_servicio
                    WHERE fecha = %(fecha)s
                      AND estado = 'finalizada'
                ) AS ordenes_finalizadas;
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
                "citas_programadas": 0,
                "ordenes_pendientes": 0,
                "ordenes_confirmadas": 0,
                "ordenes_en_proceso": 0,
                "ordenes_finalizadas": 0
            }

        return resultado[0]

    ####################################################
    # PRÓXIMAS CITAS
    ####################################################

    @classmethod
    def obtener_proximas_citas(cls, fecha, limite=6):
        query = """
            SELECT
                os.id_orden,
                os.folio,
                os.fecha,

                TIME_FORMAT(
                    os.hora_inicio,
                    '%%H:%%i'
                ) AS hora_inicio,

                os.estado,
                os.duracion_minutos,

                c.nombre AS nombre_cliente,

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

              AND os.estado IN (
                  'pendiente',
                  'confirmada',
                  'en_proceso'
              )

            ORDER BY
                os.hora_inicio ASC,
                u.nombre ASC

            LIMIT %(limite)s;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "fecha": fecha,
                "limite": limite
            }
        )

        return resultado or []

    ####################################################
    # PRODUCTOS CON STOCK BAJO
    ####################################################

    @classmethod
    def obtener_productos_stock_bajo(cls, limite=6):
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
              AND p.stock_actual <= p.stock_minimo

            ORDER BY
                p.stock_actual ASC,
                p.nombre ASC

            LIMIT %(limite)s;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "limite": limite
            }
        )

        return resultado or []

    ####################################################
    # VENTAS RECIENTES
    ####################################################

    @classmethod
    def obtener_ventas_recientes(cls, limite=6):
        query = """
            SELECT
                v.id_venta,
                v.folio,
                v.tipo_venta,
                v.total,
                v.fecha_creacion,

                COALESCE(
                    c.nombre,
                    v.nombre_cliente_rapido,
                    'Público general'
                ) AS nombre_cliente,

                m.nombre AS nombre_mascota,

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

            LEFT JOIN clientes c
                ON c.id_cliente = v.id_cliente

            LEFT JOIN mascotas m
                ON m.id_mascota = v.id_mascota

            LEFT JOIN pagos p
                ON p.id_venta = v.id_venta

            WHERE v.estado = 'completada'

            GROUP BY
                v.id_venta,
                v.folio,
                v.tipo_venta,
                v.total,
                v.fecha_creacion,
                c.nombre,
                v.nombre_cliente_rapido,
                m.nombre

            ORDER BY
                v.fecha_creacion DESC

            LIMIT %(limite)s;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            {
                "limite": limite
            }
        )

        return resultado or []