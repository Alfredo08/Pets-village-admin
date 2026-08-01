import os
import subprocess
import tempfile
import unicodedata
from decimal import Decimal


class ServicioImpresion:

    NOMBRE_IMPRESORA = (
        "STMicroelectronics_POS58_Printer_USB"
    )

    ANCHO_CARACTERES = 32

    # ==========================================
    # COMANDOS ESC/POS
    # ==========================================

    ESC = b"\x1b"
    GS = b"\x1d"

    INICIALIZAR = ESC + b"@"

    ALINEAR_IZQUIERDA = ESC + b"a\x00"
    ALINEAR_CENTRO = ESC + b"a\x01"
    ALINEAR_DERECHA = ESC + b"a\x02"

    NEGRITA_ACTIVA = ESC + b"E\x01"
    NEGRITA_INACTIVA = ESC + b"E\x00"

    TAMANO_NORMAL = GS + b"!\x00"
    TAMANO_DOBLE = GS + b"!\x11"

    AVANZAR_LINEAS = ESC + b"d\x05"

    # Corte parcial. Algunas impresoras de 58 mm
    # no tienen cortador y simplemente ignorarán
    # este comando.
    CORTE_PARCIAL = GS + b"V\x01"

    # Pulso para cajón de dinero.
    ABRIR_CAJON = ESC + b"p\x00\x19\xfa"

    @classmethod
    def limpiar_texto(cls, texto):
        """
        Convierte caracteres acentuados a una forma
        compatible con la mayoría de impresoras OEM.
        """

        texto = str(texto or "")

        texto = unicodedata.normalize(
            "NFKD",
            texto
        )

        return texto.encode(
            "ascii",
            "ignore"
        ).decode("ascii")

    @classmethod
    def dinero(cls, cantidad):
        cantidad = Decimal(str(cantidad or 0))

        return f"${cantidad:,.2f}"

    @classmethod
    def linea(cls, caracter="-"):
        return caracter * cls.ANCHO_CARACTERES

    @classmethod
    def centrar(cls, texto):
        texto = cls.limpiar_texto(texto)

        return texto.center(
            cls.ANCHO_CARACTERES
        )

    @classmethod
    def columnas(cls, izquierda, derecha):
        """
        Produce una línea con texto a la izquierda
        e importe o información a la derecha.
        """

        izquierda = cls.limpiar_texto(
            izquierda
        )

        derecha = cls.limpiar_texto(
            derecha
        )

        espacio = (
            cls.ANCHO_CARACTERES
            - len(izquierda)
            - len(derecha)
        )

        if espacio < 1:
            max_izquierda = (
                cls.ANCHO_CARACTERES
                - len(derecha)
                - 1
            )

            izquierda = izquierda[
                :max_izquierda
            ]

            espacio = 1

        return (
            izquierda
            + (" " * espacio)
            + derecha
        )

    @classmethod
    def dividir_texto(cls, texto, ancho=None):
        ancho = ancho or cls.ANCHO_CARACTERES

        palabras = cls.limpiar_texto(
            texto
        ).split()

        lineas = []
        linea_actual = ""

        for palabra in palabras:

            posible_linea = (
                f"{linea_actual} {palabra}".strip()
            )

            if len(posible_linea) <= ancho:
                linea_actual = posible_linea
            else:
                if linea_actual:
                    lineas.append(linea_actual)

                linea_actual = palabra

        if linea_actual:
            lineas.append(linea_actual)

        return lineas

    ####################################################
    # CONSTRUIR TICKET ESC/POS
    ####################################################

    @classmethod
    def construir_ticket(
        cls,
        venta,
        detalles,
        pagos,
        abrir_cajon=False
    ):
        contenido = bytearray()

        contenido.extend(cls.INICIALIZAR)

        # ==========================================
        # ENCABEZADO
        # ==========================================

        contenido.extend(cls.ALINEAR_CENTRO)
        contenido.extend(cls.NEGRITA_ACTIVA)
        contenido.extend(cls.TAMANO_DOBLE)

        contenido.extend(
            b"PETSVILLAGE\n"
        )

        contenido.extend(cls.TAMANO_NORMAL)
        contenido.extend(cls.NEGRITA_INACTIVA)

        contenido.extend(
            (
                cls.centrar(
                    "Gestion y estetica canina"
                )
                + "\n"
            ).encode()
        )

        contenido.extend(
            (
                cls.centrar(
                    "Gracias por su preferencia"
                )
                + "\n"
            ).encode()
        )

        contenido.extend(
            (
                cls.linea()
                + "\n"
            ).encode()
        )

        # ==========================================
        # INFORMACIÓN DE LA VENTA
        # ==========================================

        contenido.extend(cls.ALINEAR_IZQUIERDA)

        contenido.extend(
            (
                cls.columnas(
                    "Venta:",
                    venta["folio"]
                )
                + "\n"
            ).encode()
        )

        # Solo las ventas provenientes de una orden
        # de servicio tienen folio de orden.
        if venta.get("folio_orden"):
            contenido.extend(
                (
                    cls.columnas(
                        "Orden:",
                        venta["folio_orden"]
                    )
                    + "\n"
                ).encode()
            )

        fecha_creacion = venta.get(
            "fecha_creacion"
        )

        if hasattr(
            fecha_creacion,
            "strftime"
        ):
            fecha_texto = fecha_creacion.strftime(
                "%d/%m/%Y %H:%M"
            )
        else:
            fecha_texto = cls.limpiar_texto(
                fecha_creacion
            )

        contenido.extend(
            (
                cls.columnas(
                    "Fecha:",
                    fecha_texto
                )
                + "\n"
            ).encode()
        )

        tipo_venta = venta.get(
            "tipo_venta",
            "servicio"
        )

        if tipo_venta == "rapida":
            tipo_venta_texto = "Venta de productos"
        else:
            tipo_venta_texto = "Servicio"

        contenido.extend(
            (
                cls.columnas(
                    "Tipo:",
                    tipo_venta_texto
                )
                + "\n"
            ).encode()
        )

        contenido.extend(
            (
                cls.linea()
                + "\n"
            ).encode()
        )

        # ==========================================
        # CLIENTE Y MASCOTA
        # ==========================================

        nombre_cliente = (
            venta.get("nombre_cliente")
            or venta.get(
                "nombre_cliente_rapido"
            )
            or "Publico general"
        )

        for linea_cliente in cls.dividir_texto(
            f"Cliente: {nombre_cliente}"
        ):
            contenido.extend(
                (linea_cliente + "\n").encode()
            )

        # En ventas rápidas id_mascota será NULL.
        if venta.get("id_mascota"):
            nombre_mascota = (
                venta.get("nombre_mascota")
                or "Sin nombre"
            )

            for linea_mascota in cls.dividir_texto(
                f"Mascota: {nombre_mascota}"
            ):
                contenido.extend(
                    (linea_mascota + "\n").encode()
                )

        nombre_usuario = venta.get(
            "nombre_usuario"
        )

        if nombre_usuario:
            for linea_usuario in cls.dividir_texto(
                f"Atendio: {nombre_usuario}"
            ):
                contenido.extend(
                    (linea_usuario + "\n").encode()
                )

        contenido.extend(
            (
                cls.linea()
                + "\n"
            ).encode()
        )

        # ==========================================
        # DETALLES
        # ==========================================

        contenido.extend(cls.NEGRITA_ACTIVA)
        contenido.extend(b"CONCEPTOS\n")
        contenido.extend(cls.NEGRITA_INACTIVA)

        for detalle in detalles:

            descripcion = (
                detalle.get("descripcion")
                or "Concepto"
            )

            cantidad = Decimal(
                str(
                    detalle.get(
                        "cantidad",
                        0
                    )
                )
            )

            precio_unitario = Decimal(
                str(
                    detalle.get(
                        "precio_unitario",
                        0
                    )
                )
            )

            subtotal_detalle = Decimal(
                str(
                    detalle.get(
                        "subtotal",
                        0
                    )
                )
            )

            for linea_descripcion in cls.dividir_texto(
                descripcion
            ):
                contenido.extend(
                    (
                        linea_descripcion
                        + "\n"
                    ).encode()
                )

            cantidad_texto = (
                f"{cantidad:g} x "
                f"{cls.dinero(precio_unitario)}"
            )

            contenido.extend(
                (
                    cls.columnas(
                        cantidad_texto,
                        cls.dinero(
                            subtotal_detalle
                        )
                    )
                    + "\n"
                ).encode()
            )

        contenido.extend(
            (
                cls.linea()
                + "\n"
            ).encode()
        )

        # ==========================================
        # TOTALES
        # ==========================================

        subtotal_venta = Decimal(
            str(
                venta.get(
                    "subtotal",
                    0
                )
            )
        )

        descuento = Decimal(
            str(
                venta.get(
                    "descuento",
                    0
                )
            )
        )

        impuestos = Decimal(
            str(
                venta.get(
                    "impuestos",
                    0
                )
            )
        )

        total_venta = Decimal(
            str(
                venta.get(
                    "total",
                    0
                )
            )
        )

        contenido.extend(
            (
                cls.columnas(
                    "Subtotal:",
                    cls.dinero(
                        subtotal_venta
                    )
                )
                + "\n"
            ).encode()
        )

        if descuento > 0:
            contenido.extend(
                (
                    cls.columnas(
                        "Descuento:",
                        cls.dinero(
                            descuento
                        )
                    )
                    + "\n"
                ).encode()
            )

        if impuestos > 0:
            contenido.extend(
                (
                    cls.columnas(
                        "Impuestos:",
                        cls.dinero(
                            impuestos
                        )
                    )
                    + "\n"
                ).encode()
            )

        contenido.extend(cls.NEGRITA_ACTIVA)
        contenido.extend(cls.TAMANO_DOBLE)

        contenido.extend(
            (
                cls.columnas(
                    "TOTAL:",
                    cls.dinero(
                        total_venta
                    )
                )
                + "\n"
            ).encode()
        )

        contenido.extend(cls.TAMANO_NORMAL)
        contenido.extend(cls.NEGRITA_INACTIVA)

        contenido.extend(
            (
                cls.linea()
                + "\n"
            ).encode()
        )

        # ==========================================
        # PAGOS
        # ==========================================

        contenido.extend(cls.NEGRITA_ACTIVA)
        contenido.extend(b"PAGOS\n")
        contenido.extend(cls.NEGRITA_INACTIVA)

        total_pagado = Decimal("0.00")

        for pago in pagos:

            metodo = {
                "efectivo": "Efectivo",
                "tarjeta": "Tarjeta",
                "transferencia": (
                    "Transferencia"
                )
            }.get(
                pago.get("metodo"),
                str(
                    pago.get(
                        "metodo",
                        "Pago"
                    )
                ).capitalize()
            )

            monto = Decimal(
                str(
                    pago.get(
                        "monto",
                        0
                    )
                )
            )

            total_pagado += monto

            contenido.extend(
                (
                    cls.columnas(
                        f"{metodo}:",
                        cls.dinero(monto)
                    )
                    + "\n"
                ).encode()
            )

            referencia = (
                pago.get("referencia")
                or ""
            ).strip()

            if referencia:
                for linea_referencia in (
                    cls.dividir_texto(
                        f"Ref: {referencia}"
                    )
                ):
                    contenido.extend(
                        (
                            linea_referencia
                            + "\n"
                        ).encode()
                    )

        cambio = max(
            total_pagado - total_venta,
            Decimal("0.00")
        )

        if cambio > 0:
            contenido.extend(
                (
                    cls.columnas(
                        "Cambio:",
                        cls.dinero(
                            cambio
                        )
                    )
                    + "\n"
                ).encode()
            )

        contenido.extend(
            (
                cls.linea()
                + "\n"
            ).encode()
        )

        # ==========================================
        # PIE DEL TICKET
        # ==========================================

        contenido.extend(cls.ALINEAR_CENTRO)

        contenido.extend(
            (
                cls.centrar(
                    "Gracias por visitar PetsVillage"
                )
                + "\n"
            ).encode()
        )

        contenido.extend(
            (
                cls.centrar(
                    "Conserve este ticket"
                )
                + "\n\n"
            ).encode()
        )

        contenido.extend(
            cls.AVANZAR_LINEAS
        )

        if abrir_cajon:
            contenido.extend(
                cls.ABRIR_CAJON
            )

        contenido.extend(
            cls.CORTE_PARCIAL
        )

        return bytes(contenido)

    @classmethod
    def imprimir_ticket(
        cls,
        venta,
        detalles,
        pagos,
        abrir_cajon=False
    ):
        contenido = cls.construir_ticket(
            venta=venta,
            detalles=detalles,
            pagos=pagos,
            abrir_cajon=abrir_cajon
        )

        ruta_temporal = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=".bin",
                delete=False
            ) as archivo:

                archivo.write(contenido)
                ruta_temporal = archivo.name

            resultado = subprocess.run(
                [
                    "lp",
                    "-d",
                    cls.NOMBRE_IMPRESORA,
                    "-o",
                    "raw",
                    ruta_temporal
                ],
                capture_output=True,
                text=True,
                timeout=15,
                check=False
            )

            if resultado.returncode != 0:
                return {
                    "exito": False,
                    "mensaje": (
                        resultado.stderr.strip()
                        or "CUPS rechazó el trabajo de impresión."
                    )
                }

            return {
                "exito": True,
                "mensaje": resultado.stdout.strip()
            }

        except FileNotFoundError:
            return {
                "exito": False,
                "mensaje": (
                    "No se encontró el comando lp "
                    "en el sistema operativo."
                )
            }

        except subprocess.TimeoutExpired:
            return {
                "exito": False,
                "mensaje": (
                    "La impresora tardó demasiado "
                    "en responder."
                )
            }

        except Exception as error:
            return {
                "exito": False,
                "mensaje": str(error)
            }

        finally:
            if (
                ruta_temporal
                and os.path.exists(ruta_temporal)
            ):
                os.remove(ruta_temporal)