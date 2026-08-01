from datetime import date

from flask import (
    redirect,
    render_template,
    session
)

from app_flask import app
from app_flask.modelos.modelo_dashboard import Dashboard


####################################################
# DASHBOARD
####################################################

@app.route("/dashboard")
def dashboard():
    if "id_usuario" not in session:
        return redirect("/login")

    fecha_actual = date.today().isoformat()

    resumen = Dashboard.obtener_resumen_dia(
        fecha_actual
    )

    proximas_citas = (
        Dashboard.obtener_proximas_citas(
            fecha_actual
        )
    )

    productos_stock_bajo = (
        Dashboard.obtener_productos_stock_bajo()
    )

    ventas_recientes = (
        Dashboard.obtener_ventas_recientes()
    )

    return render_template(
        "dashboard.html",
        fecha_actual=fecha_actual,
        resumen=resumen,
        proximas_citas=proximas_citas,
        productos_stock_bajo=productos_stock_bajo,
        ventas_recientes=ventas_recientes
    )