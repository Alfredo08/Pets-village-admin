from datetime import date

from flask import (
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session
)

from datetime import (
    date,
    datetime
)

from app_flask import app
from app_flask.utilidades.decoradores import admin_requerido
from app_flask.modelos.modelo_reporte import Reporte
from app_flask.servicios.servicio_reportes import (
    ServicioReportes
)


####################################################
# PANTALLA PRINCIPAL DE REPORTES
####################################################

@app.route("/reportes")
@admin_requerido
def listar_reportes():

    fecha_actual = date.today().isoformat()

    fecha_inicio = request.args.get(
        "fecha_inicio",
        fecha_actual
    )

    fecha_fin = request.args.get(
        "fecha_fin",
        fecha_actual
    )

    fecha_caja = request.args.get(
        "fecha_caja",
        fecha_actual
    )

    return render_template(
        "reportes/listar.html",
        fecha_actual=fecha_actual,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        fecha_caja=fecha_caja
    )


####################################################
# REPORTE DE INVENTARIO
####################################################

@app.route("/reportes/inventario")
@admin_requerido
def reporte_inventario():

    productos = Reporte.obtener_inventario()

    resumen = (
        Reporte.obtener_resumen_inventario()
    )

    usuario = session.get(
        "nombre",
        "Usuario del sistema"
    )

    try:
        resultado = (
            ServicioReportes
            .generar_reporte_inventario(
                productos=productos,
                resumen=resumen,
                usuario=usuario
            )
        )

        return send_file(
            resultado["buffer"],
            mimetype="application/pdf",
            as_attachment=True,
            download_name=resultado[
                "nombre_archivo"
            ]
        )

    except Exception as error:

        print(
            "Error al generar reporte "
            "de inventario:",
            error
        )

        flash(
            "No fue posible generar el "
            "reporte de inventario.",
            "danger"
        )

        return redirect("/reportes")


####################################################
# REPORTE DE VENTAS
####################################################

@app.route("/reportes/ventas")
@admin_requerido
def reporte_ventas():

    fecha_inicio = request.args.get(
        "fecha_inicio",
        ""
    ).strip()

    fecha_fin = request.args.get(
        "fecha_fin",
        ""
    ).strip()

    # ==========================================
    # VALIDAR FECHAS
    # ==========================================

    try:
        fecha_inicio_objeto = datetime.strptime(
            fecha_inicio,
            "%Y-%m-%d"
        ).date()

        fecha_fin_objeto = datetime.strptime(
            fecha_fin,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "Selecciona un rango de fechas válido.",
            "danger"
        )

        return redirect("/reportes")

    if fecha_inicio_objeto > fecha_fin_objeto:

        flash(
            "La fecha inicial no puede ser "
            "posterior a la fecha final.",
            "warning"
        )

        return redirect(
            "/reportes"
            f"?fecha_inicio={fecha_inicio}"
            f"&fecha_fin={fecha_fin}"
        )

    if fecha_fin_objeto > date.today():

        flash(
            "La fecha final no puede ser "
            "posterior al día actual.",
            "warning"
        )

        return redirect(
            "/reportes"
            f"?fecha_inicio={fecha_inicio}"
            f"&fecha_fin={date.today().isoformat()}"
        )

    # ==========================================
    # CONSULTAR INFORMACIÓN
    # ==========================================

    ventas = Reporte.obtener_ventas(
        fecha_inicio,
        fecha_fin
    )

    resumen = Reporte.obtener_resumen_ventas(
        fecha_inicio,
        fecha_fin
    )

    metodos_pago = (
        Reporte.obtener_resumen_metodos_pago(
            fecha_inicio,
            fecha_fin
        )
    )

    usuario = session.get(
        "nombre",
        "Usuario del sistema"
    )

    # ==========================================
    # GENERAR PDF
    # ==========================================

    try:
        resultado = (
            ServicioReportes
            .generar_reporte_ventas(
                ventas=ventas,
                resumen=resumen,
                metodos_pago=metodos_pago,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                usuario=usuario
            )
        )

        return send_file(
            resultado["buffer"],
            mimetype="application/pdf",
            as_attachment=True,
            download_name=resultado[
                "nombre_archivo"
            ]
        )

    except Exception as error:

        print(
            "Error al generar reporte "
            "de ventas:",
            error
        )

        flash(
            "No fue posible generar el "
            "reporte de ventas.",
            "danger"
        )

        return redirect(
            "/reportes"
            f"?fecha_inicio={fecha_inicio}"
            f"&fecha_fin={fecha_fin}"
        )


####################################################
# REPORTE DE CAJA DEL DÍA
####################################################

@app.route("/reportes/caja")
@admin_requerido
def reporte_caja():

    fecha = request.args.get(
        "fecha",
        ""
    ).strip()

    # ==========================================
    # VALIDAR FECHA
    # ==========================================

    try:
        fecha_objeto = datetime.strptime(
            fecha,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "Selecciona una fecha válida "
            "para generar el reporte de caja.",
            "danger"
        )

        return redirect("/reportes")

    if fecha_objeto > date.today():

        flash(
            "La fecha del reporte no puede "
            "ser posterior al día actual.",
            "warning"
        )

        return redirect(
            "/reportes"
            f"?fecha_caja={date.today().isoformat()}"
        )

    # ==========================================
    # CONSULTAR DATOS
    # ==========================================

    ventas = Reporte.obtener_ventas_caja(
        fecha
    )

    resumen = Reporte.obtener_resumen_caja(
        fecha
    )

    metodos_pago = (
        Reporte.obtener_metodos_pago_caja(
            fecha
        )
    )

    conceptos = Reporte.obtener_conceptos_caja(
        fecha
    )

    productos_vendidos = (
        Reporte.obtener_productos_vendidos_caja(
            fecha
        )
    )

    servicios_vendidos = (
        Reporte.obtener_servicios_vendidos_caja(
            fecha
        )
    )

    usuario = session.get(
        "nombre",
        "Usuario del sistema"
    )

    # ==========================================
    # GENERAR PDF
    # ==========================================

    try:
        resultado = (
            ServicioReportes
            .generar_reporte_caja(
                ventas=ventas,
                resumen=resumen,
                metodos_pago=metodos_pago,
                conceptos=conceptos,
                productos_vendidos=productos_vendidos,
                servicios_vendidos=servicios_vendidos,
                fecha=fecha,
                usuario=usuario
            )
        )

        return send_file(
            resultado["buffer"],
            mimetype="application/pdf",
            as_attachment=True,
            download_name=resultado[
                "nombre_archivo"
            ]
        )

    except Exception as error:

        print(
            "Error al generar reporte "
            "de caja:",
            error
        )

        flash(
            "No fue posible generar el "
            "reporte de caja.",
            "danger"
        )

        return redirect(
            "/reportes"
            f"?fecha_caja={fecha}"
        )