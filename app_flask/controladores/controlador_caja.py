from datetime import date, datetime

from flask import (
    redirect,
    render_template,
    request,
    session
)

from app_flask import app
from app_flask.modelos.modelo_venta import Venta


####################################################
# RESUMEN DIARIO DE CAJA
####################################################

@app.route("/caja")
def caja():
    if "id_usuario" not in session:
        return redirect("/login")

    fecha_seleccionada = request.args.get(
        "fecha",
        date.today().isoformat()
    ).strip()

    try:
        datetime.strptime(
            fecha_seleccionada,
            "%Y-%m-%d"
        )
    except ValueError:
        fecha_seleccionada = (
            date.today().isoformat()
        )

    resumen = Venta.obtener_resumen_fecha(
        fecha_seleccionada
    )

    metodos_pago = (
        Venta.obtener_totales_pago_fecha(
            fecha_seleccionada
        )
    )

    tipos_venta = (
        Venta.obtener_totales_tipo_fecha(
            fecha_seleccionada
        )
    )

    ventas = Venta.obtener_ventas_fecha(
        fecha_seleccionada
    )

    return render_template(
        "caja/listar.html",
        fecha_seleccionada=fecha_seleccionada,
        resumen=resumen,
        metodos_pago=metodos_pago,
        tipos_venta=tipos_venta,
        ventas=ventas
    )