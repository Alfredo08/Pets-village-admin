import os
import subprocess
import tempfile
import unicodedata
from decimal import Decimal

from PIL import Image, ImageOps


class ServicioImpresion:

    NOMBRE_IMPRESORA = (
        "STMicroelectronics_POS58_Printer_USB"
    )

    # Papel térmico de 58 mm con fuente A normal.
    ANCHO_CARACTERES = 32

    # La mayoría de impresoras POS de 58 mm trabajan a 384 puntos.
    ANCHO_IMPRESION_PIXELES = 384
    ANCHO_LOGO_PIXELES = 280

    # Este archivo está pensado para ubicarse en:
    # app_flask/servicios/servicio_impresion.py
    RUTA_LOGO = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        "static",
        "img",
        "Petvillage.jpg"
    )

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
    DOBLE_ALTO = GS + b"!\x01"
    DOBLE_ANCHO = GS + b"!\x10"

    FUENTE_A = ESC + b"M\x00"
    FUENTE_B = ESC + b"M\x01"

    # Texto blanco sobre fondo negro.
    INVERSION_ACTIVA = GS + b"B\x01"
    INVERSION_INACTIVA = GS + b"B\x00"

    AVANZAR_LINEAS = ESC + b"d\x05"

    # Algunas impresoras de 58 mm no incluyen cortador.
    # En ese caso normalmente ignoran este comando.
    CORTE_PARCIAL = GS + b"V\x01"

    # Pulso para cajón de dinero.
    ABRIR_CAJON = ESC + b"p\x00\x19\xfa"

    # ==========================================
    # UTILIDADES DE TEXTO
    # ==========================================

    @classmethod
    def limpiar_texto(cls, texto):
        """
        Convierte caracteres acentuados a ASCII para maximizar
        la compatibilidad con impresoras térmicas ESC/POS OEM.
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
    def texto_bytes(cls, texto):
        return cls.limpiar_texto(
            texto
        ).encode("ascii")

    @classmethod
    def dinero(cls, cantidad):
        cantidad = Decimal(
            str(cantidad or 0)
        )

        return f"${cantidad:,.2f}"

    @classmethod
    def linea(cls, caracter="-"):
        return caracter * cls.ANCHO_CARACTERES

    @classmethod
    def centrar(cls, texto):
        texto = cls.limpiar_texto(
            texto
        )

        return texto.center(
            cls.ANCHO_CARACTERES
        )

    @classmethod
    def columnas(cls, izquierda, derecha):
        """
        Produce una línea con texto a la izquierda y contenido
        alineado a la derecha dentro de 32 caracteres.
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
            max_izquierda = max(
                0,
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

            # Controla palabras individuales más largas que el papel.
            while len(palabra) > ancho:
                if linea_actual:
                    lineas.append(
                        linea_actual
                    )
                    linea_actual = ""

                lineas.append(
                    palabra[:ancho]
                )
                palabra = palabra[ancho:]

            posible_linea = (
                f"{linea_actual} {palabra}".strip()
            )

            if len(posible_linea) <= ancho:
                linea_actual = posible_linea
            else:
                if linea_actual:
                    lineas.append(
                        linea_actual
                    )

                linea_actual = palabra

        if linea_actual:
            lineas.append(
                linea_actual
            )

        return lineas

    @classmethod
    def agregar_linea(cls, contenido, texto=""):
        contenido.extend(
            cls.texto_bytes(
                str(texto) + "\n"
            )
        )

    # ==========================================
    # LOGO ESC/POS
    # ==========================================

    @classmethod
    def obtener_logo_escpos(cls):
        """
        Convierte Petvillage.jpg a una imagen monocromática ESC/POS.

        El logo original tiene fondo oscuro y diseño blanco. Se invierte
        para obtener fondo blanco y elementos negros, que es lo adecuado
        para una impresora térmica.
        """

        if not os.path.exists(
            cls.RUTA_LOGO
        ):
            print(
                "No se encontró el logo del ticket:",
                cls.RUTA_LOGO
            )
            return b""

        try:
            imagen = Image.open(
                cls.RUTA_LOGO
            ).convert("L")

            # Fondo oscuro -> blanco; logo blanco -> negro.
            imagen = ImageOps.invert(
                imagen
            )

            imagen = ImageOps.autocontrast(
                imagen
            )

            # Umbral para blanco y negro puro.
            imagen = imagen.point(
                lambda pixel: (
                    0 if pixel < 170 else 255
                ),
                mode="L"
            )

            # Recortar márgenes blancos externos.
            mascara = ImageOps.invert(
                imagen
            )

            limites = mascara.getbbox()

            if limites:
                imagen = imagen.crop(
                    limites
                )

            # Redimensionar manteniendo proporción.
            ancho_objetivo = min(
                cls.ANCHO_LOGO_PIXELES,
                cls.ANCHO_IMPRESION_PIXELES
            )

            proporcion = (
                ancho_objetivo
                / imagen.width
            )

            alto_nuevo = max(
                1,
                int(
                    imagen.height
                    * proporcion
                )
            )

            imagen = imagen.resize(
                (
                    ancho_objetivo,
                    alto_nuevo
                ),
                Image.Resampling.LANCZOS
            )

            # Reaplicar el umbral después del redimensionamiento.
            imagen = imagen.point(
                lambda pixel: (
                    0 if pixel < 180 else 255
                ),
                mode="L"
            )

            # ESC/POS necesita un ancho múltiplo de 8.
            ancho_ajustado = (
                (
                    imagen.width + 7
                )
                // 8
            ) * 8

            lienzo = Image.new(
                "L",
                (
                    ancho_ajustado,
                    imagen.height
                ),
                255
            )

            posicion_x = (
                ancho_ajustado
                - imagen.width
            ) // 2

            lienzo.paste(
                imagen,
                (
                    posicion_x,
                    0
                )
            )

            lienzo = lienzo.point(
                lambda pixel: (
                    0 if pixel < 180 else 255
                ),
                mode="1"
            )

            ancho_bytes = (
                lienzo.width // 8
            )

            datos_raster = bytearray()

            for y in range(
                lienzo.height
            ):
                for bloque_x in range(
                    ancho_bytes
                ):
                    byte_actual = 0

                    for bit in range(8):
                        x = (
                            bloque_x * 8
                            + bit
                        )

                        pixel = lienzo.getpixel(
                            (
                                x,
                                y
                            )
                        )

                        # Pillow modo 1:
                        # 0 = negro; 255 = blanco.
                        if pixel == 0:
                            byte_actual |= (
                                0x80 >> bit
                            )

                    datos_raster.append(
                        byte_actual
                    )

            x_l = ancho_bytes & 0xFF
            x_h = (
                ancho_bytes >> 8
            ) & 0xFF

            y_l = lienzo.height & 0xFF
            y_h = (
                lienzo.height >> 8
            ) & 0xFF

            # GS v 0 m xL xH yL yH d1...dk
            return (
                cls.GS
                + b"v0"
                + b"\x00"
                + bytes(
                    [
                        x_l,
                        x_h,
                        y_l,
                        y_h
                    ]
                )
                + bytes(datos_raster)
            )

        except Exception as error:
            print(
                "Error al procesar logo ESC/POS:",
                error
            )
            return b""

    # ==========================================
    # ENCABEZADOS VISUALES
    # ==========================================

    @classmethod
    def encabezado_seccion(cls, texto):
        """
        Genera una barra negra con texto blanco para encabezados como
        CONCEPTOS y PAGOS.
        """

        texto = cls.limpiar_texto(
            texto
        ).upper()

        texto = texto.center(
            cls.ANCHO_CARACTERES
        )

        return (
            cls.ALINEAR_CENTRO
            + cls.TAMANO_NORMAL
            + cls.INVERSION_ACTIVA
            + cls.NEGRITA_ACTIVA
            + texto.encode("ascii")
            + b"\n"
            + cls.NEGRITA_INACTIVA
            + cls.INVERSION_INACTIVA
            + cls.ALINEAR_IZQUIERDA
        )

    # ==========================================
    # CONSTRUIR TICKET ESC/POS
    # ==========================================

    @classmethod
    def construir_ticket(
        cls,
        venta,
        detalles,
        pagos,
        abrir_cajon=False
    ):
        contenido = bytearray()

        contenido.extend(
            cls.INICIALIZAR
        )

        contenido.extend(
            cls.FUENTE_A
        )

        # ==========================================
        # ENCABEZADO Y LOGO
        # ==========================================

        contenido.extend(
            cls.ALINEAR_CENTRO
        )

        logo = cls.obtener_logo_escpos()

        if logo:
            contenido.extend(
                logo
            )
            contenido.extend(
                b"\n"
            )
        else:
            # Respaldo si el archivo del logo no existe o la impresora
            # no acepta la imagen raster.
            contenido.extend(
                cls.NEGRITA_ACTIVA
            )
            contenido.extend(
                cls.TAMANO_DOBLE
            )
            contenido.extend(
                b"PET VILLAGE\n"
            )
            contenido.extend(
                cls.TAMANO_NORMAL
            )
            contenido.extend(
                cls.NEGRITA_INACTIVA
            )

            cls.agregar_linea(
                contenido,
                cls.centrar(
                    "GROOMING - BOUTIQUE - SPA"
                )
            )

        cls.agregar_linea(
            contenido,
            cls.linea()
        )

        contenido.extend(
            cls.NEGRITA_ACTIVA
        )

        cls.agregar_linea(
            contenido,
            cls.centrar(
                "Gestion y estetica canina"
            )
        )

        contenido.extend(
            cls.NEGRITA_INACTIVA
        )

        cls.agregar_linea(
            contenido,
            cls.centrar(
                "Gracias por su preferencia"
            )
        )

        cls.agregar_linea(
            contenido,
            cls.linea()
        )

        # ==========================================
        # INFORMACIÓN DE LA VENTA
        # ==========================================

        contenido.extend(
            cls.ALINEAR_IZQUIERDA
        )

        contenido.extend(
            cls.NEGRITA_ACTIVA
        )

        cls.agregar_linea(
            contenido,
            cls.columnas(
                "Venta:",
                venta.get(
                    "folio",
                    ""
                )
            )
        )

        if venta.get(
            "folio_orden"
        ):
            cls.agregar_linea(
                contenido,
                cls.columnas(
                    "Orden:",
                    venta["folio_orden"]
                )
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

        cls.agregar_linea(
            contenido,
            cls.columnas(
                "Fecha:",
                fecha_texto
            )
        )

        contenido.extend(
            cls.NEGRITA_INACTIVA
        )

        tipo_venta = venta.get(
            "tipo_venta",
            "servicio"
        )

        tipo_venta_texto = (
            "Venta de productos"
            if tipo_venta == "rapida"
            else "Servicio"
        )

        cls.agregar_linea(
            contenido,
            cls.columnas(
                "Tipo:",
                tipo_venta_texto
            )
        )

        cls.agregar_linea(
            contenido,
            cls.linea()
        )

        # ==========================================
        # CLIENTE, MASCOTA Y USUARIO
        # ==========================================

        nombre_cliente = (
            venta.get("nombre_cliente")
            or venta.get(
                "nombre_cliente_rapido"
            )
            or "Publico general"
        )

        contenido.extend(
            cls.NEGRITA_ACTIVA
        )

        for linea_cliente in cls.dividir_texto(
            f"Cliente: {nombre_cliente}"
        ):
            cls.agregar_linea(
                contenido,
                linea_cliente
            )

        if venta.get("id_mascota"):
            nombre_mascota = (
                venta.get("nombre_mascota")
                or "Sin nombre"
            )

            for linea_mascota in cls.dividir_texto(
                f"Mascota: {nombre_mascota}"
            ):
                cls.agregar_linea(
                    contenido,
                    linea_mascota
                )

        nombre_usuario = venta.get(
            "nombre_usuario"
        )

        if nombre_usuario:
            for linea_usuario in cls.dividir_texto(
                f"Atendio: {nombre_usuario}"
            ):
                cls.agregar_linea(
                    contenido,
                    linea_usuario
                )

        contenido.extend(
            cls.NEGRITA_INACTIVA
        )

        cls.agregar_linea(
            contenido,
            cls.linea()
        )

        # ==========================================
        # CONCEPTOS
        # ==========================================

        contenido.extend(
            cls.encabezado_seccion(
                "CONCEPTOS"
            )
        )

        contenido.extend(
            cls.FUENTE_B
        )

        cls.agregar_linea(
            contenido,
            cls.columnas(
                "Descripcion",
                "Importe"
            )
        )

        cls.agregar_linea(
            contenido,
            cls.linea()
        )

        contenido.extend(
            cls.FUENTE_A
        )

        for indice, detalle in enumerate(
            detalles
        ):
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

            contenido.extend(
                cls.NEGRITA_ACTIVA
            )

            for linea_descripcion in cls.dividir_texto(
                descripcion
            ):
                cls.agregar_linea(
                    contenido,
                    linea_descripcion
                )

            contenido.extend(
                cls.NEGRITA_INACTIVA
            )

            cantidad_texto = (
                f"{cantidad:g} x "
                f"{cls.dinero(precio_unitario)}"
            )

            cls.agregar_linea(
                contenido,
                cls.columnas(
                    cantidad_texto,
                    cls.dinero(
                        subtotal_detalle
                    )
                )
            )

            if indice < len(detalles) - 1:
                cls.agregar_linea(
                    contenido,
                    cls.linea(".")
                )

        cls.agregar_linea(
            contenido,
            cls.linea()
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

        cls.agregar_linea(
            contenido,
            cls.columnas(
                "Subtotal:",
                cls.dinero(
                    subtotal_venta
                )
            )
        )

        cls.agregar_linea(
            contenido,
            cls.columnas(
                "Descuento:",
                cls.dinero(
                    descuento
                )
            )
        )

        cls.agregar_linea(
            contenido,
            cls.columnas(
                "Impuestos:",
                cls.dinero(
                    impuestos
                )
            )
        )

        contenido.extend(
            cls.NEGRITA_ACTIVA
        )

        contenido.extend(
            cls.TAMANO_DOBLE
        )

        contenido.extend(
            cls.ALINEAR_IZQUIERDA
        )

        cls.agregar_linea(
            contenido,
            "TOTAL:"
        )

        contenido.extend(
            cls.ALINEAR_DERECHA
        )

        cls.agregar_linea(
            contenido,
            cls.dinero(
                total_venta
            )
        )

        contenido.extend(
            cls.TAMANO_NORMAL
        )

        contenido.extend(
            cls.NEGRITA_INACTIVA
        )

        contenido.extend(
            cls.ALINEAR_IZQUIERDA
        )

        cls.agregar_linea(
            contenido,
            cls.linea("=")
        )

        # ==========================================
        # PAGOS
        # ==========================================

        contenido.extend(
            cls.encabezado_seccion(
                "PAGOS"
            )
        )

        total_pagado = Decimal(
            "0.00"
        )

        for pago in pagos:
            metodo = {
                "efectivo": "Efectivo",
                "tarjeta": "Tarjeta",
                "transferencia": "Transferencia"
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

            cls.agregar_linea(
                contenido,
                cls.columnas(
                    f"{metodo}:",
                    cls.dinero(
                        monto
                    )
                )
            )

            referencia = str(
                pago.get(
                    "referencia",
                    ""
                )
                or ""
            ).strip()

            if referencia:
                for linea_referencia in cls.dividir_texto(
                    f"Ref: {referencia}"
                ):
                    cls.agregar_linea(
                        contenido,
                        linea_referencia
                    )

        cambio = max(
            total_pagado - total_venta,
            Decimal("0.00")
        )

        if cambio > 0:
            contenido.extend(
                cls.NEGRITA_ACTIVA
            )

            cls.agregar_linea(
                contenido,
                cls.columnas(
                    "Cambio:",
                    cls.dinero(
                        cambio
                    )
                )
            )

            contenido.extend(
                cls.NEGRITA_INACTIVA
            )

        cls.agregar_linea(
            contenido,
            cls.linea()
        )

        # ==========================================
        # PIE DEL TICKET
        # ==========================================

        contenido.extend(
            cls.ALINEAR_CENTRO
        )

        contenido.extend(
            cls.NEGRITA_ACTIVA
        )

        cls.agregar_linea(
            contenido,
            cls.centrar(
                "Gracias por visitar Pet Village"
            )
        )

        contenido.extend(
            cls.NEGRITA_INACTIVA
        )

        cls.agregar_linea(
            contenido,
            cls.centrar(
                "Conserve este ticket"
            )
        )

        cls.agregar_linea(
            contenido,
            cls.centrar(
                "*  *  *"
            )
        )

        contenido.extend(
            b"\n"
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

    # ==========================================
    # ENVIAR TICKET A CUPS
    # ==========================================

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
                archivo.write(
                    contenido
                )
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
                "mensaje": (
                    resultado.stdout.strip()
                    or "Ticket enviado a la impresora."
                )
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
                and os.path.exists(
                    ruta_temporal
                )
            ):
                try:
                    os.remove(
                        ruta_temporal
                    )
                except OSError:
                    pass
