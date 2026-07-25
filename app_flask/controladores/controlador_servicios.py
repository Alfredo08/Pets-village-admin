from flask import flash, redirect, render_template, request, session

from app_flask import app
from app_flask.modelos.modelo_servicio import Servicio


def usuario_autenticado():
    return "id_usuario" in session


@app.route("/servicios")
def listar_servicios():
    if not usuario_autenticado():
        return redirect("/login")

    termino = request.args.get("buscar", "").strip()
    servicios = Servicio.obtener_todos(termino)

    return render_template(
        "servicios/listar.html",
        servicios=servicios,
        termino=termino
    )


@app.route("/servicios/nuevo")
def formulario_nuevo_servicio():
    if not usuario_autenticado():
        return redirect("/login")

    formulario = session.pop("formulario_servicio", None)

    return render_template(
        "servicios/nuevo.html",
        formulario=formulario
    )


@app.route("/servicios/crear", methods=["POST"])
def crear_servicio():
    if not usuario_autenticado():
        return redirect("/login")

    tarifas = obtener_tarifas_formulario(request.form)
    errores = Servicio.validar(request.form, tarifas)

    if errores:
        for error in errores:
            flash(error, "danger")

        session["formulario_servicio"] = {
            "nombre": request.form.get("nombre", ""),
            "descripcion": request.form.get("descripcion", ""),
            "tipo": request.form.get("tipo", ""),
            "tarifas": tarifas
        }

        return redirect("/servicios/nuevo")

    data = {
        "nombre": request.form.get("nombre", "").strip(),
        "descripcion": (
            request.form.get("descripcion", "").strip() or None
        ),
        "tipo": request.form.get("tipo", "").strip()
    }

    id_servicio = Servicio.crear_con_tarifas(
        data,
        tarifas
    )

    if not id_servicio:
        flash(
            "No fue posible registrar el servicio.",
            "danger"
        )
        return redirect("/servicios/nuevo")

    flash(
        "Servicio y tarifas registrados correctamente.",
        "success"
    )

    return redirect("/servicios")


@app.route("/servicios/<int:id_servicio>/editar")
def formulario_editar_servicio(id_servicio):
    if not usuario_autenticado():
        return redirect("/login")

    servicio = Servicio.obtener_por_id({
        "id_servicio": id_servicio
    })

    if not servicio:
        flash(
            "El servicio solicitado no existe.",
            "danger"
        )
        return redirect("/servicios")

    formulario_guardado = session.pop(
        f"formulario_servicio_{id_servicio}",
        None
    )

    return render_template(
        "servicios/editar.html",
        servicio=servicio,
        formulario=formulario_guardado
    )


@app.route(
    "/servicios/<int:id_servicio>/actualizar",
    methods=["POST"]
)
def actualizar_servicio(id_servicio):
    if not usuario_autenticado():
        return redirect("/login")

    servicio = Servicio.obtener_por_id({
        "id_servicio": id_servicio
    })

    if not servicio:
        flash(
            "El servicio solicitado no existe.",
            "danger"
        )
        return redirect("/servicios")

    tarifas = obtener_tarifas_formulario(request.form)
    errores = Servicio.validar(request.form, tarifas)

    if errores:
        for error in errores:
            flash(error, "danger")

        session[f"formulario_servicio_{id_servicio}"] = {
            "nombre": request.form.get("nombre", ""),
            "descripcion": request.form.get("descripcion", ""),
            "tipo": request.form.get("tipo", ""),
            "tarifas": tarifas
        }

        return redirect(
            f"/servicios/{id_servicio}/editar"
        )

    data = {
        "id_servicio": id_servicio,
        "nombre": request.form.get("nombre", "").strip(),
        "descripcion": (
            request.form.get("descripcion", "").strip() or None
        ),
        "tipo": request.form.get("tipo", "").strip()
    }

    resultado = Servicio.actualizar_con_tarifas(
        data,
        tarifas
    )

    if not resultado:
        flash(
            "No fue posible actualizar el servicio.",
            "danger"
        )

        return redirect(
            f"/servicios/{id_servicio}/editar"
        )

    flash(
        "Servicio y tarifas actualizados correctamente.",
        "success"
    )

    return redirect("/servicios")


@app.route(
    "/servicios/<int:id_servicio>/estado",
    methods=["POST"]
)
def cambiar_estado_servicio(id_servicio):
    if not usuario_autenticado():
        return redirect("/login")

    servicio = Servicio.obtener_por_id({
        "id_servicio": id_servicio
    })

    if not servicio:
        flash(
            "El servicio solicitado no existe.",
            "danger"
        )
        return redirect("/servicios")

    nuevo_estado = 0 if servicio.activo else 1

    resultado = Servicio.cambiar_estado({
        "id_servicio": id_servicio,
        "activo": nuevo_estado
    })

    if resultado is False:
        flash(
            "No fue posible cambiar el estado del servicio.",
            "danger"
        )

    else:
        mensaje = (
            "Servicio activado correctamente."
            if nuevo_estado
            else "Servicio desactivado correctamente."
        )

        flash(mensaje, "success")

    return redirect("/servicios")


def obtener_tarifas_formulario(formulario):
    ids_tarifas = formulario.getlist("id_tarifa[]")
    tamanos = formulario.getlist("tamano[]")
    tipos_pelo = formulario.getlist("tipo_pelo[]")
    precios = formulario.getlist("precio[]")

    tarifas = []

    total_filas = max(
        len(tamanos),
        len(tipos_pelo),
        len(precios)
    )

    for indice in range(total_filas):
        tamano = (
            tamanos[indice].strip()
            if indice < len(tamanos)
            else ""
        )

        tipo_pelo = (
            tipos_pelo[indice].strip()
            if indice < len(tipos_pelo)
            else ""
        )

        precio = (
            precios[indice].strip()
            if indice < len(precios)
            else ""
        )

        id_tarifa = (
            ids_tarifas[indice].strip()
            if indice < len(ids_tarifas)
            else ""
        )

        # Ignora filas completamente vacías.
        if not tamano and not tipo_pelo and not precio:
            continue

        tarifas.append({
            "id_tarifa": (
                int(id_tarifa)
                if id_tarifa.isdigit()
                else None
            ),
            "tamano": tamano,
            "tipo_pelo": tipo_pelo,
            "precio": precio
        })

    return tarifas