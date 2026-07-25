from flask import flash, redirect, render_template, request, session

from app_flask import app
from app_flask.modelos.modelo_categoria_producto import CategoriaProducto
from app_flask.modelos.modelo_producto import Producto

def sesion_iniciada():
    return "id_usuario" in session

@app.route("/productos")
def listar_productos():
    if not sesion_iniciada():
        return redirect("/login")

    termino = request.args.get("buscar", "").strip()
    productos = Producto.obtener_todos(termino)

    return render_template(
        "productos/listar.html",
        productos=productos,
        termino=termino
    )

@app.route("/productos/nuevo")
def formulario_nuevo_producto():
    if not sesion_iniciada():
        return redirect("/login")

    categorias = CategoriaProducto.obtener_activas()

    return render_template(
        "productos/nuevo.html",
        categorias=categorias
    )

@app.route("/productos/crear", methods=["POST"])
def crear_producto():
    if not sesion_iniciada():
        return redirect("/login")

    errores = Producto.validar(request.form)

    if errores:
        for error in errores:
            flash(error, "danger")

        session["formulario_producto"] = request.form.to_dict()
        return redirect("/productos/nuevo")

    data = preparar_datos_producto(request.form)
    id_producto = Producto.crear(data)

    if not id_producto:
        flash(
            "No fue posible registrar el producto.",
            "danger"
        )
        return redirect("/productos/nuevo")

    session.pop("formulario_producto", None)

    flash("Producto registrado correctamente.", "success")
    return redirect("/productos")

@app.route("/productos/<int:id_producto>/editar")
def formulario_editar_producto(id_producto):
    if not sesion_iniciada():
        return redirect("/login")

    producto = Producto.obtener_por_id({
        "id_producto": id_producto
    })

    if not producto:
        flash("El producto solicitado no existe.", "danger")
        return redirect("/productos")

    categorias = CategoriaProducto.obtener_activas()

    return render_template(
        "productos/editar.html",
        producto=producto,
        categorias=categorias
    )

@app.route("/productos/<int:id_producto>/actualizar", methods=["POST"])
def actualizar_producto(id_producto):
    if not sesion_iniciada():
        return redirect("/login")

    producto = Producto.obtener_por_id({
        "id_producto": id_producto
    })

    if not producto:
        flash("El producto solicitado no existe.", "danger")
        return redirect("/productos")

    errores = Producto.validar(
        request.form,
        producto_actual=producto
    )

    if errores:
        for error in errores:
            flash(error, "danger")

        return redirect(f"/productos/{id_producto}/editar")

    data = preparar_datos_producto(request.form)
    data["id_producto"] = id_producto

    resultado = Producto.actualizar(data)

    if resultado is False:
        flash(
            "No fue posible actualizar el producto.",
            "danger"
        )
        return redirect(f"/productos/{id_producto}/editar")

    flash("Producto actualizado correctamente.", "success")
    return redirect("/productos")

@app.route("/productos/<int:id_producto>/estado", methods=["POST"])
def cambiar_estado_producto(id_producto):
    if not sesion_iniciada():
        return redirect("/login")

    producto = Producto.obtener_por_id({
        "id_producto": id_producto
    })

    if not producto:
        flash("El producto solicitado no existe.", "danger")
        return redirect("/productos")

    nuevo_estado = 0 if producto.activo else 1

    resultado = Producto.cambiar_estado({
        "id_producto": id_producto,
        "activo": nuevo_estado
    })

    if resultado is False:
        flash(
            "No fue posible cambiar el estado del producto.",
            "danger"
        )
    else:
        mensaje = (
            "Producto activado correctamente."
            if nuevo_estado
            else "Producto desactivado correctamente."
        )
        flash(mensaje, "success")

    return redirect("/productos")

def preparar_datos_producto(formulario):
    id_categoria = formulario.get("id_categoria", "").strip()
    codigo_barras = formulario.get("codigo_barras", "").strip()

    return {
        "id_categoria": int(id_categoria) if id_categoria else None,
        "nombre": formulario.get("nombre", "").strip(),
        "descripcion": formulario.get("descripcion", "").strip() or None,
        "codigo_barras": codigo_barras or None,
        "precio_compra": formulario.get("precio_compra", "0").strip(),
        "precio_venta": formulario.get("precio_venta", "0").strip(),
        "stock_minimo": formulario.get("stock_minimo", "0").strip()
    }