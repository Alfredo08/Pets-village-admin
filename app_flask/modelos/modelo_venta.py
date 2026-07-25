from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from app_flask import BASE_DATOS
from app_flask.config.mysqlconnection import connectToMySQL


class Venta:

    METODOS_PAGO_VALIDOS = {
        "efectivo",
        "tarjeta",
        "transferencia"
    }

    DOS_DECIMALES = Decimal("0.01")

    ####################################################
    # CONVERTIR A DECIMAL
    ####################################################

    @classmethod
    def convertir_decimal(cls, valor):
        try:
            return Decimal(str(valor)).quantize(
                cls.DOS_DECIMALES,
                rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError, TypeError):
            return None

    ####################################################
    # VALIDAR INFORMACIÓN DEL COBRO
    ####################################################

    @classmethod
    def validar_cobro(cls, data):
        errores = []

        orden = data.get("orden")
        servicio = data.get("servicio")
        productos = data.get("productos", [])
        pagos = data.get("pagos", [])

        if not orden:
            errores.append(
                "No se recibió una orden de servicio válida."
            )

        if not servicio:
            errores.append(
                "No se recibió el servicio principal."
            )

        if not isinstance(productos, list):
            errores.append(
                "La lista de productos no es válida."
            )

        if not isinstance(pagos, list) or not pagos:
            errores.append(
                "Debes registrar al menos un pago."
            )

        for producto in productos:
            id_producto = str(
                producto.get("id_producto", "")
            )

            try:
                cantidad = int(
                    producto.get("cantidad", 0)
                )
            except (ValueError, TypeError):
                cantidad = 0

            if not id_producto.isdigit():
                errores.append(
                    "Uno de los productos seleccionados no es válido."
                )

            if cantidad <= 0:
                errores.append(
                    "La cantidad de un producto debe ser mayor que cero."
                )

        for pago in pagos:
            metodo = pago.get("metodo", "").strip()
            monto = cls.convertir_decimal(
                pago.get("monto")
            )

            if metodo not in cls.METODOS_PAGO_VALIDOS:
                errores.append(
                    "Uno de los métodos de pago no es válido."
                )

            if monto is None or monto <= 0:
                errores.append(
                    "Todos los pagos deben tener un monto mayor que cero."
                )

        return errores

    ####################################################
    # REGISTRAR VENTA COMPLETA
    ####################################################

    @classmethod
    def registrar(cls, data):
        """
        data esperado:

        {
            "id_orden": 1,
            "id_usuario": 1,

            "servicio": {
                "id_servicio": 1,
                "id_tarifa": 2
            },

            "productos": [
                {
                    "id_producto": 4,
                    "cantidad": 2
                }
            ],

            "pagos": [
                {
                    "metodo": "efectivo",
                    "monto": "500.00",
                    "referencia": None
                }
            ],

            "descuento": "0.00",
            "impuestos": "0.00"
        }
        """

        conexion_mysql = connectToMySQL(BASE_DATOS)
        conexion = conexion_mysql.connection

        try:
            conexion.begin()

            with conexion.cursor() as cursor:

                # ======================================
                # 1. BLOQUEAR Y OBTENER LA ORDEN
                # ======================================

                query = """
                    SELECT
                        os.id_orden,
                        os.id_cliente,
                        os.id_mascota,
                        os.id_servicio,
                        os.estado,
                        os.id_venta,

                        s.nombre AS nombre_servicio

                    FROM ordenes_servicio os

                    INNER JOIN servicios s
                        ON s.id_servicio = os.id_servicio

                    WHERE os.id_orden = %(id_orden)s

                    LIMIT 1

                    FOR UPDATE;
                """

                cursor.execute(
                    query,
                    {
                        "id_orden": data["id_orden"]
                    }
                )

                orden = cursor.fetchone()

                if not orden:
                    raise ValueError(
                        "La orden de servicio no existe."
                    )

                if orden["id_venta"]:
                    raise ValueError(
                        "Esta orden ya tiene una venta registrada."
                    )

                if orden["estado"] not in {
                    "confirmada",
                    "en_proceso"
                }:
                    raise ValueError(
                        "La orden no se encuentra disponible para cobrar."
                    )

                # ======================================
                # 2. OBTENER TARIFA DEL SERVICIO
                # ======================================

                query = """
                    SELECT
                        st.id_tarifa,
                        st.id_servicio,
                        st.precio
                    FROM servicio_tarifas st
                    WHERE st.id_tarifa = %(id_tarifa)s
                      AND st.id_servicio = %(id_servicio)s
                      AND st.activo = 1
                    LIMIT 1

                    FOR UPDATE;
                """

                cursor.execute(
                    query,
                    {
                        "id_tarifa": (
                            data["servicio"]["id_tarifa"]
                        ),
                        "id_servicio": orden["id_servicio"]
                    }
                )

                tarifa = cursor.fetchone()

                if not tarifa:
                    raise ValueError(
                        "La tarifa seleccionada no es válida."
                    )

                precio_servicio = cls.convertir_decimal(
                    tarifa["precio"]
                )

                if precio_servicio is None:
                    raise ValueError(
                        "El precio del servicio no es válido."
                    )

                detalles = []

                detalles.append({
                    "tipo": "servicio",
                    "id_servicio": orden["id_servicio"],
                    "id_tarifa": tarifa["id_tarifa"],
                    "id_producto": None,
                    "descripcion": orden["nombre_servicio"],
                    "cantidad": Decimal("1.00"),
                    "precio_unitario": precio_servicio,
                    "subtotal": precio_servicio
                })

                subtotal = precio_servicio

                # ======================================
                # 3. VALIDAR PRODUCTOS Y STOCK
                # ======================================

                productos_solicitados = (
                    data.get("productos", [])
                )

                ids_vistos = set()

                for producto_solicitado in productos_solicitados:

                    id_producto = int(
                        producto_solicitado["id_producto"]
                    )

                    cantidad = int(
                        producto_solicitado["cantidad"]
                    )

                    if id_producto in ids_vistos:
                        raise ValueError(
                            "El carrito contiene un producto duplicado."
                        )

                    ids_vistos.add(id_producto)

                    query = """
                        SELECT
                            id_producto,
                            nombre,
                            precio_venta,
                            stock_actual,
                            activo
                        FROM productos
                        WHERE id_producto = %(id_producto)s
                        LIMIT 1

                        FOR UPDATE;
                    """

                    cursor.execute(
                        query,
                        {
                            "id_producto": id_producto
                        }
                    )

                    producto = cursor.fetchone()

                    if not producto:
                        raise ValueError(
                            "Uno de los productos ya no existe."
                        )

                    if not producto["activo"]:
                        raise ValueError(
                            (
                                f"El producto "
                                f"{producto['nombre']} está inactivo."
                            )
                        )

                    if producto["stock_actual"] < cantidad:
                        raise ValueError(
                            (
                                f"No hay suficiente stock de "
                                f"{producto['nombre']}."
                            )
                        )

                    precio_unitario = cls.convertir_decimal(
                        producto["precio_venta"]
                    )

                    cantidad_decimal = Decimal(cantidad)

                    subtotal_producto = (
                        precio_unitario * cantidad_decimal
                    ).quantize(
                        cls.DOS_DECIMALES,
                        rounding=ROUND_HALF_UP
                    )

                    detalles.append({
                        "tipo": "producto",
                        "id_servicio": None,
                        "id_tarifa": None,
                        "id_producto": id_producto,
                        "descripcion": producto["nombre"],
                        "cantidad": cantidad_decimal,
                        "precio_unitario": precio_unitario,
                        "subtotal": subtotal_producto
                    })

                    subtotal += subtotal_producto

                subtotal = subtotal.quantize(
                    cls.DOS_DECIMALES,
                    rounding=ROUND_HALF_UP
                )

                # ======================================
                # 4. CALCULAR TOTALES
                # ======================================

                descuento = cls.convertir_decimal(
                    data.get("descuento", "0")
                )

                impuestos = cls.convertir_decimal(
                    data.get("impuestos", "0")
                )

                if descuento is None or descuento < 0:
                    raise ValueError(
                        "El descuento no es válido."
                    )

                if impuestos is None or impuestos < 0:
                    raise ValueError(
                        "El importe de impuestos no es válido."
                    )

                if descuento > subtotal:
                    raise ValueError(
                        "El descuento no puede superar el subtotal."
                    )

                total = (
                    subtotal - descuento + impuestos
                ).quantize(
                    cls.DOS_DECIMALES,
                    rounding=ROUND_HALF_UP
                )

                if total <= 0:
                    raise ValueError(
                        "El total de la venta debe ser mayor que cero."
                    )

                # ======================================
                # 5. VALIDAR PAGOS
                # ======================================

                pagos = data.get("pagos", [])

                if not pagos:
                    raise ValueError(
                        "Debes registrar al menos un pago."
                    )

                pagos_normalizados = []
                total_pagado = Decimal("0.00")

                for pago in pagos:
                    metodo = pago.get(
                        "metodo",
                        ""
                    ).strip()

                    if metodo not in cls.METODOS_PAGO_VALIDOS:
                        raise ValueError(
                            "Uno de los métodos de pago no es válido."
                        )

                    monto = cls.convertir_decimal(
                        pago.get("monto")
                    )

                    if monto is None or monto <= 0:
                        raise ValueError(
                            "El monto de un pago no es válido."
                        )

                    referencia = (
                        pago.get("referencia", "").strip()
                        or None
                    )

                    pagos_normalizados.append({
                        "metodo": metodo,
                        "monto": monto,
                        "referencia": referencia
                    })

                    total_pagado += monto

                total_pagado = total_pagado.quantize(
                    cls.DOS_DECIMALES,
                    rounding=ROUND_HALF_UP
                )

                if total_pagado < total:
                    raise ValueError(
                        "El total pagado es menor que el total de la venta."
                    )

                # El excedente solo es cambio cuando existe
                # al menos un pago en efectivo.
                cambio = (
                    total_pagado - total
                ).quantize(
                    cls.DOS_DECIMALES,
                    rounding=ROUND_HALF_UP
                )

                tiene_efectivo = any(
                    pago["metodo"] == "efectivo"
                    for pago in pagos_normalizados
                )

                if cambio > 0 and not tiene_efectivo:
                    raise ValueError(
                        "Solo un pago en efectivo puede generar cambio."
                    )

                # ======================================
                # 6. CREAR VENTA
                # ======================================

                query = """
                    INSERT INTO ventas (
                        folio,
                        id_orden,
                        id_cliente,
                        id_mascota,
                        id_usuario,
                        subtotal,
                        descuento,
                        impuestos,
                        total,
                        estado
                    )
                    VALUES (
                        NULL,
                        %(id_orden)s,
                        %(id_cliente)s,
                        %(id_mascota)s,
                        %(id_usuario)s,
                        %(subtotal)s,
                        %(descuento)s,
                        %(impuestos)s,
                        %(total)s,
                        'completada'
                    );
                """

                cursor.execute(
                    query,
                    {
                        "id_orden": orden["id_orden"],
                        "id_cliente": orden["id_cliente"],
                        "id_mascota": orden["id_mascota"],
                        "id_usuario": data["id_usuario"],
                        "subtotal": subtotal,
                        "descuento": descuento,
                        "impuestos": impuestos,
                        "total": total
                    }
                )

                id_venta = cursor.lastrowid
                folio = f"V-{id_venta:06d}"

                query = """
                    UPDATE ventas
                    SET folio = %(folio)s
                    WHERE id_venta = %(id_venta)s;
                """

                cursor.execute(
                    query,
                    {
                        "folio": folio,
                        "id_venta": id_venta
                    }
                )

                # ======================================
                # 7. CREAR DETALLES
                # ======================================

                query_detalle = """
                    INSERT INTO venta_detalles (
                        id_venta,
                        tipo,
                        id_servicio,
                        id_tarifa,
                        id_producto,
                        descripcion,
                        cantidad,
                        precio_unitario,
                        subtotal
                    )
                    VALUES (
                        %(id_venta)s,
                        %(tipo)s,
                        %(id_servicio)s,
                        %(id_tarifa)s,
                        %(id_producto)s,
                        %(descripcion)s,
                        %(cantidad)s,
                        %(precio_unitario)s,
                        %(subtotal)s
                    );
                """

                for detalle in detalles:
                    detalle["id_venta"] = id_venta
                    cursor.execute(
                        query_detalle,
                        detalle
                    )

                # ======================================
                # 8. CREAR PAGOS
                # ======================================

                query_pago = """
                    INSERT INTO pagos (
                        id_venta,
                        metodo,
                        monto,
                        referencia
                    )
                    VALUES (
                        %(id_venta)s,
                        %(metodo)s,
                        %(monto)s,
                        %(referencia)s
                    );
                """

                for pago in pagos_normalizados:
                    pago["id_venta"] = id_venta

                    cursor.execute(
                        query_pago,
                        pago
                    )

                # ======================================
                # 9. DESCONTAR Y REGISTRAR INVENTARIO
                # ======================================

                for detalle in detalles:
                    if detalle["tipo"] != "producto":
                        continue

                    id_producto = detalle["id_producto"]
                    cantidad = int(detalle["cantidad"])

                    query = """
                        SELECT
                            nombre,
                            stock_actual
                        FROM productos
                        WHERE id_producto = %(id_producto)s
                        LIMIT 1
                        FOR UPDATE;
                    """

                    cursor.execute(
                        query,
                        {
                            "id_producto": id_producto
                        }
                    )

                    producto_stock = cursor.fetchone()

                    if not producto_stock:
                        raise ValueError(
                            "No fue posible consultar el producto antes "
                            "de descontar su inventario."
                        )

                    stock_anterior = int(
                        producto_stock["stock_actual"]
                    )

                    if stock_anterior < cantidad:
                        raise ValueError(
                            f"No hay suficiente stock de "
                            f"{producto_stock['nombre']}."
                        )

                    stock_nuevo = stock_anterior - cantidad

                    query = """
                        UPDATE productos
                        SET stock_actual = %(stock_nuevo)s
                        WHERE id_producto = %(id_producto)s
                        AND stock_actual = %(stock_anterior)s;
                    """

                    cursor.execute(
                        query,
                        {
                            "stock_nuevo": stock_nuevo,
                            "id_producto": id_producto,
                            "stock_anterior": stock_anterior
                        }
                    )

                    if cursor.rowcount != 1:
                        raise ValueError(
                            f"No fue posible descontar el stock de "
                            f"{producto_stock['nombre']}."
                        )

                    query = """
                        INSERT INTO inventario_movimientos (
                            id_producto,
                            id_usuario,
                            tipo_movimiento,
                            cantidad,
                            motivo,
                            id_orden,
                            id_venta,
                            observaciones
                        )
                        VALUES (
                            %(id_producto)s,
                            %(id_usuario)s,
                            'salida',
                            %(cantidad)s,
                            'Venta',
                            NULL,
                            %(id_venta)s,
                            %(observaciones)s
                        );
                    """

                    cursor.execute(
                        query,
                        {
                            "id_producto": id_producto,
                            "id_usuario": data["id_usuario"],
                            "cantidad": cantidad,
                            "id_venta": id_venta,
                            "observaciones": (
                                f"Salida por venta {folio}. "
                                f"Orden de servicio: {orden['id_orden']}. "
                                f"Stock anterior: {stock_anterior}. "
                                f"Stock nuevo: {stock_nuevo}."
                            )
                        }
                    )

                # ======================================
                # 10. FINALIZAR Y ENLAZAR ORDEN
                # ======================================

                query = """
                    UPDATE ordenes_servicio
                    SET
                        id_venta = %(id_venta)s,
                        estado = 'finalizada'
                    WHERE id_orden = %(id_orden)s
                      AND id_venta IS NULL;
                """

                cursor.execute(
                    query,
                    {
                        "id_venta": id_venta,
                        "id_orden": orden["id_orden"]
                    }
                )

                if cursor.rowcount != 1:
                    raise ValueError(
                        "No fue posible finalizar la orden de servicio."
                    )

            conexion.commit()

            return {
                "exito": True,
                "id_venta": id_venta,
                "folio": folio,
                "subtotal": subtotal,
                "descuento": descuento,
                "impuestos": impuestos,
                "total": total,
                "total_pagado": total_pagado,
                "cambio": cambio
            }

        except Exception as error:
            conexion.rollback()

            print(
                "Error al registrar la venta:",
                error
            )

            return {
                "exito": False,
                "mensaje": str(error)
            }

        finally:
            conexion.close()


    ####################################################
    # OBTENER VENTA POR ID
    ####################################################

    @classmethod
    def obtener_por_id(cls, data):
        query = """
            SELECT
                v.*,

                c.nombre AS nombre_cliente,
                c.telefono AS telefono_cliente,

                m.nombre AS nombre_mascota,
                m.numero_expediente,

                os.folio AS folio_orden,

                u.nombre AS nombre_usuario

            FROM ventas v

            INNER JOIN clientes c
                ON c.id_cliente = v.id_cliente

            INNER JOIN mascotas m
                ON m.id_mascota = v.id_mascota

            INNER JOIN ordenes_servicio os
                ON os.id_orden = v.id_orden

            INNER JOIN usuarios u
                ON u.id_usuario = v.id_usuario

            WHERE v.id_venta = %(id_venta)s

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
    # OBTENER DETALLES
    ####################################################

    @classmethod
    def obtener_detalles(cls, data):
        query = """
            SELECT *
            FROM venta_detalles
            WHERE id_venta = %(id_venta)s
            ORDER BY id_detalle ASC;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(
            query,
            data
        )

        return resultado or []


    ####################################################
    # OBTENER PAGOS
    ####################################################

    @classmethod
    def obtener_pagos(cls, data):
        query = """
            SELECT *
            FROM pagos
            WHERE id_venta = %(id_venta)s
            ORDER BY id_pago ASC;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(
            query,
            data
        )

        return resultado or []

    ####################################################
    # HISTORIAL DE SERVICIOS DE UNA MASCOTA
    ####################################################

    @classmethod
    def obtener_historial_mascota(cls, data):

        query = """
            SELECT

                v.id_venta,
                v.folio,
                v.total,
                v.fecha_creacion,

                os.folio AS folio_orden,

                u.nombre AS estilista,

                vd.descripcion

            FROM ventas v

            INNER JOIN ordenes_servicio os
                ON os.id_orden = v.id_orden

            INNER JOIN usuarios u
                ON u.id_usuario = v.id_usuario

            INNER JOIN venta_detalles vd
                ON vd.id_venta = v.id_venta

            WHERE

                v.id_mascota = %(id_mascota)s

                AND vd.tipo='servicio'

            ORDER BY

                v.fecha_creacion DESC;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )

        return resultado or []

    ####################################################
    # PRODUCTOS COMPRADOS POR LA MASCOTA
    ####################################################

    @classmethod
    def obtener_compras_mascota(cls, data):

        query = """
            SELECT

                v.id_venta,
                v.folio,
                v.fecha_creacion,

                vd.descripcion,
                vd.cantidad,
                vd.precio_unitario,
                vd.subtotal

            FROM ventas v

            INNER JOIN venta_detalles vd
                ON vd.id_venta=v.id_venta

            WHERE

                v.id_mascota=%(id_mascota)s

                AND vd.tipo='producto'

            ORDER BY

                v.fecha_creacion DESC;
        """

        resultado = connectToMySQL(
            BASE_DATOS
        ).query_db(
            query,
            data
        )

        return resultado or []