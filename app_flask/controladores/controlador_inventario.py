from flask import flash, redirect, render_template, request, session

from app_flask import app
from app_flask.modelos.modelo_inventario import MovimientoInventario
from app_flask.modelos.modelo_producto import Producto


def usuario_autenticado():
    return "id_usuario" in session


@app.route("/inventario")
def listar_inventario():
    if not usuario_autenticado():
        return redirect("/login")

    termino = request.args.get("buscar", "").strip()

    productos = MovimientoInventario.obtener_resumen_productos()
    movimientos = MovimientoInventario.obtener_movimientos(termino)

    return render_template(
        "inventario/listar.html",
        productos=productos,
        movimientos=movimientos,
        termino=termino
    )


@app.route("/inventario/movimiento")
def formulario_movimiento():
    if not usuario_autenticado():
        return redirect("/login")

    productos = Producto.obtener_todos()
    productos_activos = [
        producto
        for producto in productos
        if producto.activo
    ]

    id_producto = request.args.get("producto", type=int)

    return render_template(
        "inventario/movimiento.html",
        productos=productos_activos,
        id_producto_seleccionado=id_producto
    )


@app.route("/inventario/movimiento/crear", methods=["POST"])
def crear_movimiento():
    if not usuario_autenticado():
        return redirect("/login")

    errores = MovimientoInventario.validar(request.form)

    if errores:
        for error in errores:
            flash(error, "danger")

        session["formulario_movimiento"] = request.form.to_dict()
        return redirect("/inventario/movimiento")

    data = {
        "id_producto": int(request.form["id_producto"]),
        "id_usuario": session["id_usuario"],
        "tipo_movimiento": request.form["tipo_movimiento"],
        "cantidad": int(request.form["cantidad"]),
        "motivo": request.form["motivo"].strip(),
        "observaciones": (
            request.form.get("observaciones", "").strip() or None
        )
    }

    resultado = MovimientoInventario.registrar(data)

    if not resultado["exito"]:
        flash(resultado["mensaje"], "danger")

        session["formulario_movimiento"] = request.form.to_dict()
        return redirect("/inventario/movimiento")

    session.pop("formulario_movimiento", None)

    flash(
        (
            "Movimiento registrado correctamente. "
            f"Nueva existencia: {resultado['nuevo_stock']}."
        ),
        "success"
    )

    return redirect("/inventario")