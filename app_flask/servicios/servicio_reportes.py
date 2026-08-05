import io
import os
from datetime import datetime
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT,
    TA_RIGHT
)
from reportlab.lib.pagesizes import (
    A4,
    landscape
)
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle
)


class ServicioReportes:

    ####################################################
    # COLORES
    ####################################################

    COLOR_PRIMARIO = colors.HexColor(
        "#7C3AED"
    )

    COLOR_PRIMARIO_SUAVE = colors.HexColor(
        "#F3E8FF"
    )

    COLOR_TEXTO = colors.HexColor(
        "#1F2937"
    )

    COLOR_TEXTO_SUAVE = colors.HexColor(
        "#6B7280"
    )

    COLOR_BORDE = colors.HexColor(
        "#E5E7EB"
    )

    COLOR_FONDO_TABLA = colors.HexColor(
        "#F9FAFB"
    )

    COLOR_EXITO = colors.HexColor(
        "#15803D"
    )

    COLOR_EXITO_SUAVE = colors.HexColor(
        "#DCFCE7"
    )

    COLOR_ADVERTENCIA = colors.HexColor(
        "#B45309"
    )

    COLOR_ADVERTENCIA_SUAVE = colors.HexColor(
        "#FEF3C7"
    )

    COLOR_PELIGRO = colors.HexColor(
        "#B91C1C"
    )

    COLOR_PELIGRO_SUAVE = colors.HexColor(
        "#FEE2E2"
    )

    ####################################################
    # CONFIGURACIÓN
    ####################################################

    PAGINA_HORIZONTAL = landscape(A4)

    MARGEN_IZQUIERDO = 12 * mm
    MARGEN_DERECHO = 12 * mm
    MARGEN_SUPERIOR = 13 * mm
    MARGEN_INFERIOR = 16 * mm

    ####################################################
    # UTILIDADES GENERALES
    ####################################################

    @classmethod
    def obtener_ruta_logo(cls):
        return os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)
            ),
            "static",
            "img",
            "Petvillage.jpg"
        )

    @classmethod
    def crear_buffer(cls):
        return io.BytesIO()

    @classmethod
    def texto_seguro(cls, valor):
        if valor is None:
            return ""

        texto = str(valor)

        return (
            texto
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    @classmethod
    def numero_entero(cls, valor):
        try:
            return int(valor or 0)

        except (
            TypeError,
            ValueError
        ):
            return 0

    @classmethod
    def decimal(cls, valor):
        try:
            return Decimal(
                str(valor or 0)
            )

        except Exception:
            return Decimal("0.00")

    @classmethod
    def dinero(cls, valor):
        cantidad = cls.decimal(
            valor
        )

        return f"${cantidad:,.2f}"

    ####################################################
    # ESTILOS DE TEXTO
    ####################################################

    @classmethod
    def crear_estilos(cls):
        estilos = getSampleStyleSheet()

        estilos.add(
            ParagraphStyle(
                name="ReporteMarca",
                parent=estilos["Normal"],
                fontName="Helvetica-Bold",
                fontSize=16,
                leading=18,
                alignment=TA_CENTER,
                textColor=cls.COLOR_TEXTO,
                spaceAfter=2
            )
        )

        estilos.add(
            ParagraphStyle(
                name="ReporteMarcaSubtitulo",
                parent=estilos["Normal"],
                fontName="Helvetica",
                fontSize=7.5,
                leading=9,
                alignment=TA_CENTER,
                textColor=cls.COLOR_TEXTO_SUAVE,
                spaceAfter=2
            )
        )

        estilos.add(
            ParagraphStyle(
                name="ReporteTitulo",
                parent=estilos["Title"],
                fontName="Helvetica-Bold",
                fontSize=18,
                leading=22,
                alignment=TA_LEFT,
                textColor=cls.COLOR_TEXTO,
                spaceAfter=3
            )
        )

        estilos.add(
            ParagraphStyle(
                name="ReporteSubtitulo",
                parent=estilos["Normal"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=11,
                alignment=TA_LEFT,
                textColor=cls.COLOR_TEXTO_SUAVE
            )
        )

        estilos.add(
            ParagraphStyle(
                name="ReporteSeccion",
                parent=estilos["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                textColor=cls.COLOR_TEXTO,
                spaceBefore=8,
                spaceAfter=7
            )
        )

        estilos.add(
            ParagraphStyle(
                name="ReporteTexto",
                parent=estilos["Normal"],
                fontName="Helvetica",
                fontSize=7.5,
                leading=9.5,
                textColor=cls.COLOR_TEXTO
            )
        )

        estilos.add(
            ParagraphStyle(
                name="ReporteTextoCentro",
                parent=estilos["Normal"],
                fontName="Helvetica",
                fontSize=7.5,
                leading=9.5,
                alignment=TA_CENTER,
                textColor=cls.COLOR_TEXTO
            )
        )

        estilos.add(
            ParagraphStyle(
                name="ReporteTextoDerecha",
                parent=estilos["Normal"],
                fontName="Helvetica",
                fontSize=7.5,
                leading=9.5,
                alignment=TA_RIGHT,
                textColor=cls.COLOR_TEXTO
            )
        )

        estilos.add(
            ParagraphStyle(
                name="ReporteTextoPequeno",
                parent=estilos["Normal"],
                fontName="Helvetica",
                fontSize=6.8,
                leading=8.5,
                textColor=cls.COLOR_TEXTO_SUAVE
            )
        )

        estilos.add(
            ParagraphStyle(
                name="ResumenEtiqueta",
                parent=estilos["Normal"],
                fontName="Helvetica-Bold",
                fontSize=7,
                leading=8,
                textColor=cls.COLOR_TEXTO_SUAVE,
                spaceAfter=3
            )
        )

        estilos.add(
            ParagraphStyle(
                name="ResumenValor",
                parent=estilos["Normal"],
                fontName="Helvetica-Bold",
                fontSize=13,
                leading=15,
                textColor=cls.COLOR_TEXTO
            )
        )

        estilos.add(
            ParagraphStyle(
                name="EstadoNormal",
                parent=estilos["Normal"],
                fontName="Helvetica-Bold",
                fontSize=6.5,
                leading=8,
                alignment=TA_CENTER,
                textColor=cls.COLOR_EXITO
            )
        )

        estilos.add(
            ParagraphStyle(
                name="EstadoBajo",
                parent=estilos["Normal"],
                fontName="Helvetica-Bold",
                fontSize=6.5,
                leading=8,
                alignment=TA_CENTER,
                textColor=cls.COLOR_ADVERTENCIA
            )
        )

        estilos.add(
            ParagraphStyle(
                name="EstadoAgotado",
                parent=estilos["Normal"],
                fontName="Helvetica-Bold",
                fontSize=6.5,
                leading=8,
                alignment=TA_CENTER,
                textColor=cls.COLOR_PELIGRO
            )
        )

        return estilos

    ####################################################
    # ENCABEZADO DEL DOCUMENTO
    ####################################################

    @classmethod
    def crear_encabezado(
        cls,
        titulo,
        subtitulo,
        fecha_generacion,
        usuario,
        estilos
    ):
        elementos_marca = []

        ruta_logo = cls.obtener_ruta_logo()

        if os.path.exists(ruta_logo):
            try:
                logo = Image(
                    ruta_logo,
                    width=25 * mm,
                    height=25 * mm
                )

                logo.hAlign = "CENTER"

                elementos_marca.append(
                    logo
                )

            except Exception as error:
                print(
                    "No fue posible cargar el logo "
                    "del reporte:",
                    error
                )

        elementos_marca.extend([
            Paragraph(
                "PETSVILLAGE",
                estilos["ReporteMarca"]
            ),

            Paragraph(
                "Gestión y estética canina",
                estilos[
                    "ReporteMarcaSubtitulo"
                ]
            )
        ])

        bloque_marca = Table(
            [
                [elemento]
                for elemento in elementos_marca
            ],
            colWidths=[
                44 * mm
            ]
        )

        bloque_marca.setStyle(
            TableStyle([
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                )
            ])
        )

        informacion = [
            Paragraph(
                cls.texto_seguro(titulo),
                estilos["ReporteTitulo"]
            ),

            Paragraph(
                cls.texto_seguro(subtitulo),
                estilos["ReporteSubtitulo"]
            ),

            Spacer(
                1,
                3 * mm
            ),

            Paragraph(
                (
                    "<b>Generado:</b> "
                    f"{fecha_generacion}"
                    "<br/>"
                    "<b>Usuario:</b> "
                    f"{cls.texto_seguro(usuario)}"
                ),
                estilos["ReporteTextoPequeno"]
            )
        ]

        bloque_informacion = Table(
            [
                [elemento]
                for elemento in informacion
            ],
            colWidths=[
                213 * mm
            ]
        )

        bloque_informacion.setStyle(
            TableStyle([
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                )
            ])
        )

        encabezado = Table(
            [
                [
                    bloque_marca,
                    bloque_informacion
                ]
            ],
            colWidths=[
                48 * mm,
                217 * mm
            ]
        )

        encabezado.setStyle(
            TableStyle([
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    cls.COLOR_BORDE
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    cls.COLOR_PRIMARIO_SUAVE
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm
                )
            ])
        )

        return encabezado

    ####################################################
    # TARJETAS DE RESUMEN
    ####################################################

    @classmethod
    def crear_tarjeta_resumen(
        cls,
        etiqueta,
        valor,
        estilos,
        color_fondo=None
    ):
        contenido = [
            Paragraph(
                cls.texto_seguro(
                    etiqueta.upper()
                ),
                estilos["ResumenEtiqueta"]
            ),

            Paragraph(
                cls.texto_seguro(valor),
                estilos["ResumenValor"]
            )
        ]

        tarjeta = Table(
            [
                [elemento]
                for elemento in contenido
            ],
            colWidths=[
                39 * mm
            ]
        )

        tarjeta.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    (
                        color_fondo
                        or cls.COLOR_FONDO_TABLA
                    )
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    cls.COLOR_BORDE
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm
                )
            ])
        )

        return tarjeta

    @classmethod
    def crear_resumen_inventario(
        cls,
        resumen,
        estilos
    ):
        tarjetas = [
            cls.crear_tarjeta_resumen(
                "Productos activos",
                str(
                    cls.numero_entero(
                        resumen.get(
                            "productos_activos"
                        )
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Unidades totales",
                str(
                    cls.numero_entero(
                        resumen.get(
                            "unidades_totales"
                        )
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Sin existencias",
                str(
                    cls.numero_entero(
                        resumen.get(
                            "productos_sin_stock"
                        )
                    )
                ),
                estilos,
                cls.COLOR_PELIGRO_SUAVE
            ),

            cls.crear_tarjeta_resumen(
                "Stock bajo",
                str(
                    cls.numero_entero(
                        resumen.get(
                            "productos_stock_bajo"
                        )
                    )
                ),
                estilos,
                cls.COLOR_ADVERTENCIA_SUAVE
            ),

            cls.crear_tarjeta_resumen(
                "Valor de compra",
                cls.dinero(
                    resumen.get(
                        "valor_compra"
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Valor estimado de venta",
                cls.dinero(
                    resumen.get(
                        "valor_venta"
                    )
                ),
                estilos,
                cls.COLOR_PRIMARIO_SUAVE
            )
        ]

        tabla = Table(
            [
                tarjetas
            ],
            colWidths=[
                43.5 * mm
            ] * 6,
            hAlign="LEFT"
        )

        tabla.setStyle(
            TableStyle([
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.2 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.2 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                )
            ])
        )

        return tabla

    ####################################################
    # ESTADO DEL PRODUCTO
    ####################################################

    @classmethod
    def obtener_estado_producto(
        cls,
        stock_actual,
        stock_minimo
    ):
        stock_actual = cls.numero_entero(
            stock_actual
        )

        stock_minimo = cls.numero_entero(
            stock_minimo
        )

        if stock_actual <= 0:
            return {
                "texto": "Sin existencias",
                "estilo": "EstadoAgotado",
                "fondo": cls.COLOR_PELIGRO_SUAVE
            }

        if stock_actual <= stock_minimo:
            return {
                "texto": "Stock bajo",
                "estilo": "EstadoBajo",
                "fondo": cls.COLOR_ADVERTENCIA_SUAVE
            }

        return {
            "texto": "Disponible",
            "estilo": "EstadoNormal",
            "fondo": cls.COLOR_EXITO_SUAVE
        }

    ####################################################
    # TABLA DE INVENTARIO
    ####################################################

    @classmethod
    def crear_tabla_inventario(
        cls,
        productos,
        estilos
    ):
        encabezados = [
            Paragraph(
                "<b>Producto</b>",
                estilos["ReporteTexto"]
            ),
            Paragraph(
                "<b>Categoría</b>",
                estilos["ReporteTexto"]
            ),
            Paragraph(
                "<b>Código</b>",
                estilos["ReporteTexto"]
            ),
            Paragraph(
                "<b>Existencia</b>",
                estilos["ReporteTextoCentro"]
            ),
            Paragraph(
                "<b>Mínimo</b>",
                estilos["ReporteTextoCentro"]
            ),
            Paragraph(
                "<b>Precio compra</b>",
                estilos["ReporteTextoDerecha"]
            ),
            Paragraph(
                "<b>Precio venta</b>",
                estilos["ReporteTextoDerecha"]
            ),
            Paragraph(
                "<b>Estado</b>",
                estilos["ReporteTextoCentro"]
            )
        ]

        datos = [
            encabezados
        ]

        estilos_condicionales = []

        for indice, producto in enumerate(
            productos,
            start=1
        ):
            estado = cls.obtener_estado_producto(
                producto.get(
                    "stock_actual"
                ),
                producto.get(
                    "stock_minimo"
                )
            )

            datos.append([
                Paragraph(
                    cls.texto_seguro(
                        producto.get(
                            "nombre"
                        )
                        or "Sin nombre"
                    ),
                    estilos["ReporteTexto"]
                ),

                Paragraph(
                    cls.texto_seguro(
                        producto.get(
                            "nombre_categoria"
                        )
                        or "Sin categoría"
                    ),
                    estilos["ReporteTexto"]
                ),

                Paragraph(
                    cls.texto_seguro(
                        producto.get(
                            "codigo_barras"
                        )
                        or "—"
                    ),
                    estilos[
                        "ReporteTextoPequeno"
                    ]
                ),

                Paragraph(
                    str(
                        cls.numero_entero(
                            producto.get(
                                "stock_actual"
                            )
                        )
                    ),
                    estilos[
                        "ReporteTextoCentro"
                    ]
                ),

                Paragraph(
                    str(
                        cls.numero_entero(
                            producto.get(
                                "stock_minimo"
                            )
                        )
                    ),
                    estilos[
                        "ReporteTextoCentro"
                    ]
                ),

                Paragraph(
                    cls.dinero(
                        producto.get(
                            "precio_compra"
                        )
                    ),
                    estilos[
                        "ReporteTextoDerecha"
                    ]
                ),

                Paragraph(
                    cls.dinero(
                        producto.get(
                            "precio_venta"
                        )
                    ),
                    estilos[
                        "ReporteTextoDerecha"
                    ]
                ),

                Paragraph(
                    estado["texto"],
                    estilos[
                        estado["estilo"]
                    ]
                )
            ])

            estilos_condicionales.append(
                (
                    "BACKGROUND",
                    (7, indice),
                    (7, indice),
                    estado["fondo"]
                )
            )

        tabla = Table(
            datos,
            colWidths=[
                53 * mm,
                35 * mm,
                34 * mm,
                19 * mm,
                18 * mm,
                29 * mm,
                29 * mm,
                30 * mm
            ],
            repeatRows=1,
            hAlign="LEFT"
        )

        estilo_tabla = [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                cls.COLOR_PRIMARIO
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                cls.COLOR_BORDE
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    cls.COLOR_FONDO_TABLA
                ]
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                2.2 * mm
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                2.2 * mm
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                2 * mm
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                2 * mm
            ),
            (
                "ALIGN",
                (3, 1),
                (4, -1),
                "CENTER"
            ),
            (
                "ALIGN",
                (5, 1),
                (6, -1),
                "RIGHT"
            ),
            (
                "ALIGN",
                (7, 1),
                (7, -1),
                "CENTER"
            )
        ]

        estilo_tabla.extend(
            estilos_condicionales
        )

        tabla.setStyle(
            TableStyle(
                estilo_tabla
            )
        )

        return tabla

    ####################################################
    # PIE DE PÁGINA
    ####################################################

    @classmethod
    def crear_pie_pagina(
        cls,
        fecha_generacion,
        usuario
    ):
        def dibujar_pie(
            canvas,
            documento
        ):
            canvas.saveState()

            ancho_pagina, _ = (
                cls.PAGINA_HORIZONTAL
            )

            y = 8 * mm

            canvas.setStrokeColor(
                cls.COLOR_BORDE
            )

            canvas.setLineWidth(
                0.5
            )

            canvas.line(
                cls.MARGEN_IZQUIERDO,
                y + 4 * mm,
                ancho_pagina
                - cls.MARGEN_DERECHO,
                y + 4 * mm
            )

            canvas.setFont(
                "Helvetica",
                6.8
            )

            canvas.setFillColor(
                cls.COLOR_TEXTO_SUAVE
            )

            canvas.drawString(
                cls.MARGEN_IZQUIERDO,
                y,
                (
                    "PetsVillage - "
                    f"Generado por {usuario} "
                    f"el {fecha_generacion}"
                )
            )

            canvas.drawRightString(
                ancho_pagina
                - cls.MARGEN_DERECHO,
                y,
                f"Página {documento.page}"
            )

            canvas.restoreState()

        return dibujar_pie

    ####################################################
    # GENERAR REPORTE DE INVENTARIO
    ####################################################

    @classmethod
    def generar_reporte_inventario(
        cls,
        productos,
        resumen,
        usuario
    ):
        buffer = cls.crear_buffer()

        fecha_generacion_datetime = (
            datetime.now()
        )

        fecha_generacion = (
            fecha_generacion_datetime
            .strftime("%d/%m/%Y %H:%M")
        )

        nombre_archivo = (
            "reporte_inventario_"
            + fecha_generacion_datetime.strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".pdf"
        )

        documento = SimpleDocTemplate(
            buffer,
            pagesize=cls.PAGINA_HORIZONTAL,
            rightMargin=cls.MARGEN_DERECHO,
            leftMargin=cls.MARGEN_IZQUIERDO,
            topMargin=cls.MARGEN_SUPERIOR,
            bottomMargin=cls.MARGEN_INFERIOR,
            title="Reporte de inventario",
            author="PetsVillage",
            subject=(
                "Inventario actual de productos"
            )
        )

        estilos = cls.crear_estilos()

        historia = []

        historia.append(
            cls.crear_encabezado(
                titulo="Reporte de inventario",
                subtitulo=(
                    "Existencias actuales, niveles mínimos "
                    "y valor estimado del inventario."
                ),
                fecha_generacion=fecha_generacion,
                usuario=usuario,
                estilos=estilos
            )
        )

        historia.append(
            Spacer(
                1,
                5 * mm
            )
        )

        historia.append(
            KeepTogether([
                Paragraph(
                    "Resumen general",
                    estilos["ReporteSeccion"]
                ),

                cls.crear_resumen_inventario(
                    resumen,
                    estilos
                )
            ])
        )

        historia.append(
            Spacer(
                1,
                5 * mm
            )
        )

        historia.append(
            Paragraph(
                "Detalle de productos",
                estilos["ReporteSeccion"]
            )
        )

        if productos:
            historia.append(
                cls.crear_tabla_inventario(
                    productos,
                    estilos
                )
            )

        else:
            mensaje = Table(
                [[
                    Paragraph(
                        (
                            "No existen productos activos "
                            "para incluir en el reporte."
                        ),
                        estilos["ReporteTexto"]
                    )
                ]],
                colWidths=[
                    260 * mm
                ]
            )

            mensaje.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        cls.COLOR_FONDO_TABLA
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        cls.COLOR_BORDE
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm
                    )
                ])
            )

            historia.append(
                mensaje
            )

        pie_pagina = cls.crear_pie_pagina(
            fecha_generacion=fecha_generacion,
            usuario=usuario
        )

        documento.build(
            historia,
            onFirstPage=pie_pagina,
            onLaterPages=pie_pagina
        )

        buffer.seek(0)

        return {
            "buffer": buffer,
            "nombre_archivo": nombre_archivo
        }

    ####################################################
    # RESUMEN DEL REPORTE DE VENTAS
    ####################################################

    @classmethod
    def crear_resumen_ventas(
        cls,
        resumen,
        estilos
    ):
        tarjetas = [
            cls.crear_tarjeta_resumen(
                "Ventas completadas",
                str(
                    cls.numero_entero(
                        resumen.get(
                            "cantidad_ventas"
                        )
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Total vendido",
                cls.dinero(
                    resumen.get(
                        "total_vendido"
                    )
                ),
                estilos,
                cls.COLOR_PRIMARIO_SUAVE
            ),

            cls.crear_tarjeta_resumen(
                "Promedio por venta",
                cls.dinero(
                    resumen.get(
                        "promedio_venta"
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Ventas de servicio",
                str(
                    cls.numero_entero(
                        resumen.get(
                            "cantidad_servicios"
                        )
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Ventas rápidas",
                str(
                    cls.numero_entero(
                        resumen.get(
                            "cantidad_ventas_rapidas"
                        )
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Descuentos",
                cls.dinero(
                    resumen.get(
                        "descuentos_totales"
                    )
                ),
                estilos,
                cls.COLOR_ADVERTENCIA_SUAVE
            )
        ]

        tabla = Table(
            [
                tarjetas
            ],
            colWidths=[
                43.5 * mm
            ] * 6,
            hAlign="LEFT"
        )

        tabla.setStyle(
            TableStyle([
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.2 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.2 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                )
            ])
        )

        return tabla

    ####################################################
    # MÉTODOS DE PAGO DEL REPORTE DE VENTAS
    ####################################################

    @classmethod
    def crear_resumen_metodos_pago(
        cls,
        metodos,
        estilos
    ):
        datos = [
            [
                Paragraph(
                    "<b>Método</b>",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    "<b>Operaciones</b>",
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    "<b>Total recibido</b>",
                    estilos["ReporteTextoDerecha"]
                )
            ],

            [
                Paragraph(
                    "Efectivo",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    str(
                        cls.numero_entero(
                            metodos.get(
                                "operaciones_efectivo"
                            )
                        )
                    ),
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    cls.dinero(
                        metodos.get(
                            "total_efectivo"
                        )
                    ),
                    estilos["ReporteTextoDerecha"]
                )
            ],

            [
                Paragraph(
                    "Tarjeta",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    str(
                        cls.numero_entero(
                            metodos.get(
                                "operaciones_tarjeta"
                            )
                        )
                    ),
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    cls.dinero(
                        metodos.get(
                            "total_tarjeta"
                        )
                    ),
                    estilos["ReporteTextoDerecha"]
                )
            ],

            [
                Paragraph(
                    "Transferencia",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    str(
                        cls.numero_entero(
                            metodos.get(
                                "operaciones_transferencia"
                            )
                        )
                    ),
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    cls.dinero(
                        metodos.get(
                            "total_transferencia"
                        )
                    ),
                    estilos["ReporteTextoDerecha"]
                )
            ]
        ]

        tabla = Table(
            datos,
            colWidths=[
                55 * mm,
                35 * mm,
                50 * mm
            ],
            repeatRows=1,
            hAlign="LEFT"
        )

        tabla.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    cls.COLOR_PRIMARIO
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    cls.COLOR_BORDE
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        cls.COLOR_FONDO_TABLA
                    ]
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.2 * mm
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.2 * mm
                )
            ])
        )

        return tabla

    ####################################################
    # TABLA DE VENTAS
    ####################################################

    @classmethod
    def crear_tabla_ventas(
        cls,
        ventas,
        estilos
    ):
        encabezados = [
            Paragraph(
                "<b>Fecha</b>",
                estilos["ReporteTexto"]
            ),
            Paragraph(
                "<b>Folio</b>",
                estilos["ReporteTexto"]
            ),
            Paragraph(
                "<b>Tipo</b>",
                estilos["ReporteTextoCentro"]
            ),
            Paragraph(
                "<b>Cliente / mascota</b>",
                estilos["ReporteTexto"]
            ),
            Paragraph(
                "<b>Método</b>",
                estilos["ReporteTexto"]
            ),
            Paragraph(
                "<b>Registró</b>",
                estilos["ReporteTexto"]
            ),
            Paragraph(
                "<b>Total</b>",
                estilos["ReporteTextoDerecha"]
            )
        ]

        datos = [
            encabezados
        ]

        for venta in ventas:

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
                fecha_texto = (
                    str(fecha_creacion or "—")
                )

            if venta.get("tipo_venta") == "rapida":
                tipo_texto = "Venta rápida"
            else:
                tipo_texto = "Servicio"

            nombre_cliente = (
                venta.get("nombre_cliente")
                or "Público general"
            )

            nombre_mascota = venta.get(
                "nombre_mascota"
            )

            if nombre_mascota:
                cliente_mascota = (
                    f"<b>{cls.texto_seguro(nombre_cliente)}</b>"
                    f"<br/>Mascota: "
                    f"{cls.texto_seguro(nombre_mascota)}"
                )
            elif venta.get("tipo_venta") == "rapida":
                cliente_mascota = (
                    f"<b>{cls.texto_seguro(nombre_cliente)}</b>"
                    "<br/>Solo productos"
                )
            else:
                cliente_mascota = (
                    f"<b>{cls.texto_seguro(nombre_cliente)}</b>"
                    "<br/>Sin mascota"
                )

            folio_orden = venta.get(
                "folio_orden"
            )

            if folio_orden:
                folio_texto = (
                    f"<b>{cls.texto_seguro(venta.get('folio'))}</b>"
                    f"<br/>{cls.texto_seguro(folio_orden)}"
                )
            else:
                folio_texto = (
                    f"<b>{cls.texto_seguro(venta.get('folio'))}</b>"
                    "<br/>Sin orden"
                )

            datos.append([
                Paragraph(
                    cls.texto_seguro(
                        fecha_texto
                    ),
                    estilos[
                        "ReporteTextoPequeno"
                    ]
                ),

                Paragraph(
                    folio_texto,
                    estilos["ReporteTextoPequeno"]
                ),

                Paragraph(
                    tipo_texto,
                    estilos["ReporteTextoCentro"]
                ),

                Paragraph(
                    cliente_mascota,
                    estilos["ReporteTextoPequeno"]
                ),

                Paragraph(
                    cls.texto_seguro(
                        venta.get(
                            "metodos_pago"
                        )
                        or "Sin información"
                    ),
                    estilos["ReporteTextoPequeno"]
                ),

                Paragraph(
                    cls.texto_seguro(
                        venta.get(
                            "nombre_usuario"
                        )
                        or "Sin información"
                    ),
                    estilos["ReporteTextoPequeno"]
                ),

                Paragraph(
                    cls.dinero(
                        venta.get("total")
                    ),
                    estilos["ReporteTextoDerecha"]
                )
            ])

        tabla = Table(
            datos,
            colWidths=[
                28 * mm,
                29 * mm,
                26 * mm,
                54 * mm,
                38 * mm,
                41 * mm,
                30 * mm
            ],
            repeatRows=1,
            hAlign="LEFT"
        )

        tabla.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    cls.COLOR_PRIMARIO
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    cls.COLOR_BORDE
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        cls.COLOR_FONDO_TABLA
                    ]
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2.2 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2.2 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm
                ),
                (
                    "ALIGN",
                    (2, 1),
                    (2, -1),
                    "CENTER"
                ),
                (
                    "ALIGN",
                    (6, 1),
                    (6, -1),
                    "RIGHT"
                )
            ])
        )

        return tabla

    ####################################################
    # GENERAR REPORTE DE VENTAS
    ####################################################

    @classmethod
    def generar_reporte_ventas(
        cls,
        ventas,
        resumen,
        metodos_pago,
        fecha_inicio,
        fecha_fin,
        usuario
    ):
        buffer = cls.crear_buffer()

        fecha_generacion_datetime = datetime.now()

        fecha_generacion = (
            fecha_generacion_datetime
            .strftime("%d/%m/%Y %H:%M")
        )

        try:
            fecha_inicio_texto = (
                datetime.strptime(
                    fecha_inicio,
                    "%Y-%m-%d"
                ).strftime("%d/%m/%Y")
            )

            fecha_fin_texto = (
                datetime.strptime(
                    fecha_fin,
                    "%Y-%m-%d"
                ).strftime("%d/%m/%Y")
            )

        except ValueError:
            fecha_inicio_texto = fecha_inicio
            fecha_fin_texto = fecha_fin

        nombre_archivo = (
            "reporte_ventas_"
            + fecha_inicio.replace("-", "")
            + "_"
            + fecha_fin.replace("-", "")
            + ".pdf"
        )

        documento = SimpleDocTemplate(
            buffer,
            pagesize=cls.PAGINA_HORIZONTAL,
            rightMargin=cls.MARGEN_DERECHO,
            leftMargin=cls.MARGEN_IZQUIERDO,
            topMargin=cls.MARGEN_SUPERIOR,
            bottomMargin=cls.MARGEN_INFERIOR,
            title="Reporte de ventas",
            author="PetsVillage",
            subject=(
                "Ventas registradas en el periodo"
            )
        )

        estilos = cls.crear_estilos()

        historia = []

        historia.append(
            cls.crear_encabezado(
                titulo="Reporte de ventas",
                subtitulo=(
                    "Periodo del "
                    f"{fecha_inicio_texto} "
                    "al "
                    f"{fecha_fin_texto}."
                ),
                fecha_generacion=fecha_generacion,
                usuario=usuario,
                estilos=estilos
            )
        )

        historia.append(
            Spacer(
                1,
                5 * mm
            )
        )

        historia.append(
            KeepTogether([
                Paragraph(
                    "Resumen general",
                    estilos["ReporteSeccion"]
                ),

                cls.crear_resumen_ventas(
                    resumen,
                    estilos
                )
            ])
        )

        historia.append(
            Spacer(
                1,
                5 * mm
            )
        )

        historia.append(
            KeepTogether([
                Paragraph(
                    "Ingresos por método de pago",
                    estilos["ReporteSeccion"]
                ),

                cls.crear_resumen_metodos_pago(
                    metodos_pago,
                    estilos
                )
            ])
        )

        historia.append(
            Spacer(
                1,
                5 * mm
            )
        )

        historia.append(
            Paragraph(
                "Detalle de ventas",
                estilos["ReporteSeccion"]
            )
        )

        if ventas:
            historia.append(
                cls.crear_tabla_ventas(
                    ventas,
                    estilos
                )
            )

        else:
            mensaje = Table(
                [[
                    Paragraph(
                        (
                            "No existen ventas completadas "
                            "dentro del periodo seleccionado."
                        ),
                        estilos["ReporteTexto"]
                    )
                ]],
                colWidths=[
                    260 * mm
                ]
            )

            mensaje.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        cls.COLOR_FONDO_TABLA
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        cls.COLOR_BORDE
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm
                    )
                ])
            )

            historia.append(
                mensaje
            )

        pie_pagina = cls.crear_pie_pagina(
            fecha_generacion=fecha_generacion,
            usuario=usuario
        )

        documento.build(
            historia,
            onFirstPage=pie_pagina,
            onLaterPages=pie_pagina
        )

        buffer.seek(0)

        return {
            "buffer": buffer,
            "nombre_archivo": nombre_archivo
        }

    ####################################################
    # TARJETAS DEL REPORTE DE CAJA
    ####################################################

    @classmethod
    def crear_resumen_caja(
        cls,
        resumen,
        estilos
    ):
        tarjetas = [
            cls.crear_tarjeta_resumen(
                "Ventas completadas",
                str(
                    cls.numero_entero(
                        resumen.get(
                            "cantidad_ventas"
                        )
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Total vendido",
                cls.dinero(
                    resumen.get(
                        "total_vendido"
                    )
                ),
                estilos,
                cls.COLOR_PRIMARIO_SUAVE
            ),

            cls.crear_tarjeta_resumen(
                "Promedio por venta",
                cls.dinero(
                    resumen.get(
                        "promedio_venta"
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Ventas de servicio",
                str(
                    cls.numero_entero(
                        resumen.get(
                            "ventas_servicio"
                        )
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Ventas rápidas",
                str(
                    cls.numero_entero(
                        resumen.get(
                            "ventas_rapidas"
                        )
                    )
                ),
                estilos
            ),

            cls.crear_tarjeta_resumen(
                "Descuentos",
                cls.dinero(
                    resumen.get(
                        "descuentos_totales"
                    )
                ),
                estilos,
                cls.COLOR_ADVERTENCIA_SUAVE
            )
        ]

        tabla = Table(
            [tarjetas],
            colWidths=[
                43.5 * mm
            ] * 6,
            hAlign="LEFT"
        )

        tabla.setStyle(
            TableStyle([
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.2 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.2 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                )
            ])
        )

        return tabla

    ####################################################
    # RESUMEN FINANCIERO DE CAJA
    ####################################################

    @classmethod
    def crear_resumen_financiero_caja(
        cls,
        metodos_pago,
        conceptos,
        estilos
    ):
        datos = [
            [
                Paragraph(
                    "<b>Concepto</b>",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    "<b>Operaciones / unidades</b>",
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    "<b>Total</b>",
                    estilos["ReporteTextoDerecha"]
                )
            ],

            [
                Paragraph(
                    "Efectivo",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    str(
                        cls.numero_entero(
                            metodos_pago.get(
                                "operaciones_efectivo"
                            )
                        )
                    ),
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    cls.dinero(
                        metodos_pago.get(
                            "efectivo"
                        )
                    ),
                    estilos["ReporteTextoDerecha"]
                )
            ],

            [
                Paragraph(
                    "Tarjeta",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    str(
                        cls.numero_entero(
                            metodos_pago.get(
                                "operaciones_tarjeta"
                            )
                        )
                    ),
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    cls.dinero(
                        metodos_pago.get(
                            "tarjeta"
                        )
                    ),
                    estilos["ReporteTextoDerecha"]
                )
            ],

            [
                Paragraph(
                    "Transferencia",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    str(
                        cls.numero_entero(
                            metodos_pago.get(
                                "operaciones_transferencia"
                            )
                        )
                    ),
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    cls.dinero(
                        metodos_pago.get(
                            "transferencia"
                        )
                    ),
                    estilos["ReporteTextoDerecha"]
                )
            ],

            [
                Paragraph(
                    "Servicios vendidos",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    str(
                        cls.numero_entero(
                            conceptos.get(
                                "cantidad_servicios"
                            )
                        )
                    ),
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    cls.dinero(
                        conceptos.get(
                            "total_servicios"
                        )
                    ),
                    estilos["ReporteTextoDerecha"]
                )
            ],

            [
                Paragraph(
                    "Productos vendidos",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    str(
                        cls.numero_entero(
                            conceptos.get(
                                "cantidad_productos"
                            )
                        )
                    ),
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    cls.dinero(
                        conceptos.get(
                            "total_productos"
                        )
                    ),
                    estilos["ReporteTextoDerecha"]
                )
            ]
        ]

        tabla = Table(
            datos,
            colWidths=[
                70 * mm,
                45 * mm,
                55 * mm
            ],
            repeatRows=1,
            hAlign="LEFT"
        )

        tabla.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    cls.COLOR_PRIMARIO
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    cls.COLOR_BORDE
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        cls.COLOR_FONDO_TABLA
                    ]
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.2 * mm
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.2 * mm
                )
            ])
        )

        return tabla

    ####################################################
    # TABLA DE CONCEPTOS VENDIDOS
    ####################################################

    @classmethod
    def crear_tabla_conceptos_vendidos(
        cls,
        conceptos,
        estilos
    ):
        datos = [
            [
                Paragraph(
                    "<b>Descripción</b>",
                    estilos["ReporteTexto"]
                ),
                Paragraph(
                    "<b>Cantidad</b>",
                    estilos["ReporteTextoCentro"]
                ),
                Paragraph(
                    "<b>Total</b>",
                    estilos["ReporteTextoDerecha"]
                )
            ]
        ]

        for concepto in conceptos:
            datos.append([
                Paragraph(
                    cls.texto_seguro(
                        concepto.get(
                            "descripcion"
                        )
                        or "Sin descripción"
                    ),
                    estilos["ReporteTexto"]
                ),

                Paragraph(
                    str(
                        cls.numero_entero(
                            concepto.get(
                                "cantidad"
                            )
                        )
                    ),
                    estilos["ReporteTextoCentro"]
                ),

                Paragraph(
                    cls.dinero(
                        concepto.get(
                            "total"
                        )
                    ),
                    estilos["ReporteTextoDerecha"]
                )
            ])

        tabla = Table(
            datos,
            colWidths=[
                95 * mm,
                30 * mm,
                45 * mm
            ],
            repeatRows=1,
            hAlign="LEFT"
        )

        tabla.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    cls.COLOR_PRIMARIO
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    cls.COLOR_BORDE
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        cls.COLOR_FONDO_TABLA
                    ]
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm
                )
            ])
        )

        return tabla

    ####################################################
    # GENERAR REPORTE DE CAJA
    ####################################################

    @classmethod
    def generar_reporte_caja(
        cls,
        ventas,
        resumen,
        metodos_pago,
        conceptos,
        productos_vendidos,
        servicios_vendidos,
        fecha,
        usuario
    ):
        buffer = cls.crear_buffer()

        fecha_generacion_datetime = datetime.now()

        fecha_generacion = (
            fecha_generacion_datetime
            .strftime("%d/%m/%Y %H:%M")
        )

        try:
            fecha_texto = datetime.strptime(
                fecha,
                "%Y-%m-%d"
            ).strftime("%d/%m/%Y")

        except ValueError:
            fecha_texto = fecha

        nombre_archivo = (
            "reporte_caja_"
            + fecha.replace("-", "")
            + ".pdf"
        )

        documento = SimpleDocTemplate(
            buffer,
            pagesize=cls.PAGINA_HORIZONTAL,
            rightMargin=cls.MARGEN_DERECHO,
            leftMargin=cls.MARGEN_IZQUIERDO,
            topMargin=cls.MARGEN_SUPERIOR,
            bottomMargin=cls.MARGEN_INFERIOR,
            title="Reporte de caja",
            author="PetsVillage",
            subject=(
                f"Resumen de caja del {fecha_texto}"
            )
        )

        estilos = cls.crear_estilos()

        historia = []

        historia.append(
            cls.crear_encabezado(
                titulo="Reporte de caja del día",
                subtitulo=(
                    "Resumen de ingresos y movimientos "
                    f"correspondientes al {fecha_texto}."
                ),
                fecha_generacion=fecha_generacion,
                usuario=usuario,
                estilos=estilos
            )
        )

        historia.append(
            Spacer(
                1,
                5 * mm
            )
        )

        historia.append(
            KeepTogether([
                Paragraph(
                    "Resumen general",
                    estilos["ReporteSeccion"]
                ),

                cls.crear_resumen_caja(
                    resumen,
                    estilos
                )
            ])
        )

        historia.append(
            Spacer(
                1,
                5 * mm
            )
        )

        historia.append(
            KeepTogether([
                Paragraph(
                    "Resumen financiero",
                    estilos["ReporteSeccion"]
                ),

                cls.crear_resumen_financiero_caja(
                    metodos_pago,
                    conceptos,
                    estilos
                )
            ])
        )

        historia.append(
            Spacer(
                1,
                5 * mm
            )
        )

        historia.append(
            Paragraph(
                "Movimientos del día",
                estilos["ReporteSeccion"]
            )
        )

        if ventas:
            historia.append(
                cls.crear_tabla_ventas(
                    ventas,
                    estilos
                )
            )
        else:
            historia.append(
                Paragraph(
                    (
                        "No existen ventas completadas "
                        "en la fecha seleccionada."
                    ),
                    estilos["ReporteTexto"]
                )
            )

        if servicios_vendidos:
            historia.append(
                Spacer(
                    1,
                    5 * mm
                )
            )

            historia.append(
                Paragraph(
                    "Servicios vendidos",
                    estilos["ReporteSeccion"]
                )
            )

            historia.append(
                cls.crear_tabla_conceptos_vendidos(
                    servicios_vendidos,
                    estilos
                )
            )

        if productos_vendidos:
            historia.append(
                Spacer(
                    1,
                    5 * mm
                )
            )

            historia.append(
                Paragraph(
                    "Productos vendidos",
                    estilos["ReporteSeccion"]
                )
            )

            historia.append(
                cls.crear_tabla_conceptos_vendidos(
                    productos_vendidos,
                    estilos
                )
            )

        pie_pagina = cls.crear_pie_pagina(
            fecha_generacion=fecha_generacion,
            usuario=usuario
        )

        documento.build(
            historia,
            onFirstPage=pie_pagina,
            onLaterPages=pie_pagina
        )

        buffer.seek(0)

        return {
            "buffer": buffer,
            "nombre_archivo": nombre_archivo
        }