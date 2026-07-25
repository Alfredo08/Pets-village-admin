from flask import flash, redirect, render_template, request, session

from app_flask import app
from app_flask.modelos.modelo_cliente import Cliente
from app_flask.modelos.modelo_mascota import Mascota


def usuario_autenticado():
    return "id_usuario" in session


@app.route("/clientes")
def listar_clientes():
    if not usuario_autenticado():
        return redirect("/login")

    termino = request.args.get("buscar", "").strip()
    clientes = Cliente.obtener_todos(termino)

    return render_template(
        "clientes/listar.html",
        clientes=clientes,
        termino=termino
    )


@app.route("/clientes/nuevo")
def formulario_nuevo_cliente():
    if not usuario_autenticado():
        return redirect("/login")

    formulario = session.pop("formulario_cliente", None)

    return render_template(
        "clientes/nuevo.html",
        formulario=formulario
    )


@app.route("/clientes/crear", methods=["POST"])
def crear_cliente():
    if not usuario_autenticado():
        return redirect("/login")

    errores = Cliente.validar(request.form)

    if errores:
        for error in errores:
            flash(error, "danger")

        session["formulario_cliente"] = request.form.to_dict()
        return redirect("/clientes/nuevo")

    data = preparar_datos_cliente(request.form)

    id_cliente = Cliente.crear(data)

    if not id_cliente:
        flash(
            "No fue posible registrar el cliente.",
            "danger"
        )

        session["formulario_cliente"] = request.form.to_dict()
        return redirect("/clientes/nuevo")

    flash(
        "Cliente registrado correctamente.",
        "success"
    )

    return redirect(f"/clientes/{id_cliente}")


@app.route("/clientes/<int:id_cliente>")
def detalle_cliente(id_cliente):
    if not usuario_autenticado():
        return redirect("/login")

    cliente = Cliente.obtener_por_id({
        "id_cliente": id_cliente
    })

    if not cliente:
        flash(
            "El cliente solicitado no existe.",
            "danger"
        )
        return redirect("/clientes")

    # Las mascotas se agregarán en el siguiente módulo.
    mascotas = Mascota.obtener_por_cliente({
        "id_cliente": id_cliente
    })

    return render_template(
        "clientes/detalle.html",
        cliente=cliente,
        mascotas=mascotas
    )


@app.route("/clientes/<int:id_cliente>/editar")
def formulario_editar_cliente(id_cliente):
    if not usuario_autenticado():
        return redirect("/login")

    cliente = Cliente.obtener_por_id({
        "id_cliente": id_cliente
    })

    if not cliente:
        flash(
            "El cliente solicitado no existe.",
            "danger"
        )
        return redirect("/clientes")

    formulario = session.pop(
        f"formulario_cliente_{id_cliente}",
        None
    )

    return render_template(
        "clientes/editar.html",
        cliente=cliente,
        formulario=formulario
    )


@app.route(
    "/clientes/<int:id_cliente>/actualizar",
    methods=["POST"]
)
def actualizar_cliente(id_cliente):
    if not usuario_autenticado():
        return redirect("/login")

    cliente = Cliente.obtener_por_id({
        "id_cliente": id_cliente
    })

    if not cliente:
        flash(
            "El cliente solicitado no existe.",
            "danger"
        )
        return redirect("/clientes")

    errores = Cliente.validar(request.form)

    if errores:
        for error in errores:
            flash(error, "danger")

        session[f"formulario_cliente_{id_cliente}"] = (
            request.form.to_dict()
        )

        return redirect(
            f"/clientes/{id_cliente}/editar"
        )

    data = preparar_datos_cliente(request.form)
    data["id_cliente"] = id_cliente

    resultado = Cliente.actualizar(data)

    if resultado is False:
        flash(
            "No fue posible actualizar el cliente.",
            "danger"
        )

        return redirect(
            f"/clientes/{id_cliente}/editar"
        )

    flash(
        "Cliente actualizado correctamente.",
        "success"
    )

    return redirect(f"/clientes/{id_cliente}")


@app.route(
    "/clientes/<int:id_cliente>/estado",
    methods=["POST"]
)
def cambiar_estado_cliente(id_cliente):
    if not usuario_autenticado():
        return redirect("/login")

    cliente = Cliente.obtener_por_id({
        "id_cliente": id_cliente
    })

    if not cliente:
        flash(
            "El cliente solicitado no existe.",
            "danger"
        )
        return redirect("/clientes")

    nuevo_estado = 0 if cliente.activo else 1

    resultado = Cliente.cambiar_estado({
        "id_cliente": id_cliente,
        "activo": nuevo_estado
    })

    if resultado is False:
        flash(
            "No fue posible cambiar el estado del cliente.",
            "danger"
        )
    else:
        mensaje = (
            "Cliente activado correctamente."
            if nuevo_estado
            else "Cliente desactivado correctamente."
        )

        flash(mensaje, "success")

    return redirect("/clientes")


def preparar_datos_cliente(formulario):
    return {
        "nombre": formulario.get("nombre", "").strip(),
        "telefono": (
            formulario.get("telefono", "").strip() or None
        ),
        "correo": (
            formulario.get("correo", "").strip().lower() or None
        ),
        "observaciones": (
            formulario.get("observaciones", "").strip() or None
        )
    }