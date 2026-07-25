from flask import flash, redirect, render_template, request, session

from app_flask import app
from app_flask.modelos.modelo_cliente import Cliente
from app_flask.modelos.modelo_mascota import Mascota
from app_flask.modelos.modelo_venta import Venta
from app_flask.modelos.modelo_orden_servicio import OrdenServicio

def usuario_autenticado():
    return "id_usuario" in session


@app.route("/clientes/<int:id_cliente>/mascotas/nueva")
def formulario_nueva_mascota(id_cliente):
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
        f"formulario_mascota_{id_cliente}",
        None
    )

    return render_template(
        "mascotas/nueva.html",
        cliente=cliente,
        formulario=formulario
    )


@app.route(
    "/clientes/<int:id_cliente>/mascotas/crear",
    methods=["POST"]
)
def crear_mascota(id_cliente):
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

    errores = Mascota.validar(request.form)

    if errores:
        for error in errores:
            flash(error, "danger")

        session[f"formulario_mascota_{id_cliente}"] = (
            request.form.to_dict()
        )

        return redirect(
            f"/clientes/{id_cliente}/mascotas/nueva"
        )

    data = preparar_datos_mascota(
        request.form,
        id_cliente
    )

    id_mascota = Mascota.crear(data)

    if not id_mascota:
        flash(
            "No fue posible registrar la mascota.",
            "danger"
        )

        session[f"formulario_mascota_{id_cliente}"] = (
            request.form.to_dict()
        )

        return redirect(
            f"/clientes/{id_cliente}/mascotas/nueva"
        )

    flash(
        "Mascota registrada correctamente.",
        "success"
    )

    return redirect(f"/clientes/{id_cliente}")


@app.route("/mascotas/<int:id_mascota>/editar")
def formulario_editar_mascota(id_mascota):
    if not usuario_autenticado():
        return redirect("/login")

    mascota = Mascota.obtener_por_id({
        "id_mascota": id_mascota
    })

    if not mascota:
        flash(
            "La mascota solicitada no existe.",
            "danger"
        )
        return redirect("/clientes")

    cliente = Cliente.obtener_por_id({
        "id_cliente": mascota.id_cliente
    })

    formulario = session.pop(
        f"formulario_mascota_editar_{id_mascota}",
        None
    )

    return render_template(
        "mascotas/editar.html",
        cliente=cliente,
        mascota=mascota,
        formulario=formulario
    )


@app.route(
    "/mascotas/<int:id_mascota>/actualizar",
    methods=["POST"]
)
def actualizar_mascota(id_mascota):
    if not usuario_autenticado():
        return redirect("/login")

    mascota = Mascota.obtener_por_id({
        "id_mascota": id_mascota
    })

    if not mascota:
        flash(
            "La mascota solicitada no existe.",
            "danger"
        )
        return redirect("/clientes")

    errores = Mascota.validar(request.form)

    if errores:
        for error in errores:
            flash(error, "danger")

        session[
            f"formulario_mascota_editar_{id_mascota}"
        ] = request.form.to_dict()

        return redirect(
            f"/mascotas/{id_mascota}/editar"
        )

    data = preparar_datos_mascota(
        request.form,
        mascota.id_cliente
    )

    data["id_mascota"] = id_mascota

    resultado = Mascota.actualizar(data)

    if resultado is False:
        flash(
            "No fue posible actualizar la mascota.",
            "danger"
        )

        return redirect(
            f"/mascotas/{id_mascota}/editar"
        )

    flash(
        "Mascota actualizada correctamente.",
        "success"
    )

    return redirect(
        f"/clientes/{mascota.id_cliente}"
    )


@app.route(
    "/mascotas/<int:id_mascota>/estado",
    methods=["POST"]
)
def cambiar_estado_mascota(id_mascota):
    if not usuario_autenticado():
        return redirect("/login")

    mascota = Mascota.obtener_por_id({
        "id_mascota": id_mascota
    })

    if not mascota:
        flash(
            "La mascota solicitada no existe.",
            "danger"
        )
        return redirect("/clientes")

    nuevo_estado = 0 if mascota.activo else 1

    resultado = Mascota.cambiar_estado({
        "id_mascota": id_mascota,
        "activo": nuevo_estado
    })

    if resultado is False:
        flash(
            "No fue posible cambiar el estado de la mascota.",
            "danger"
        )
    else:
        mensaje = (
            "Mascota activada correctamente."
            if nuevo_estado
            else "Mascota desactivada correctamente."
        )

        flash(mensaje, "success")

    return redirect(
        f"/clientes/{mascota.id_cliente}"
    )


def preparar_datos_mascota(formulario, id_cliente):
    esterilizado = formulario.get(
        "esterilizado",
        ""
    ).strip()

    return {
        "id_cliente": id_cliente,
        "nombre": formulario.get("nombre", "").strip(),
        "especie": formulario.get("especie", "").strip(),
        "raza": (
            formulario.get("raza", "").strip() or None
        ),
        "tamano": formulario.get("tamano", "").strip(),
        "tipo_pelo": formulario.get(
            "tipo_pelo",
            ""
        ).strip(),
        "sexo": formulario.get(
            "sexo",
            "No especificado"
        ).strip(),
        "fecha_nacimiento": (
            formulario.get(
                "fecha_nacimiento",
                ""
            ).strip() or None
        ),
        "peso": (
            formulario.get("peso", "").strip() or None
        ),
        "color": (
            formulario.get("color", "").strip() or None
        ),
        "esterilizado": (
            int(esterilizado)
            if esterilizado in {"0", "1"}
            else None
        ),
        "alergias": (
            formulario.get("alergias", "").strip() or None
        ),
        "observaciones": (
            formulario.get(
                "observaciones",
                ""
            ).strip() or None
        ),
        "notas_especiales": (
            formulario.get(
                "notas_especiales",
                ""
            ).strip() or None
        )
    }

@app.route("/mascotas")
def listar_mascotas():

    if not usuario_autenticado():
        return redirect("/login")

    termino = request.args.get(
        "buscar",
        ""
    ).strip()

    mascotas = Mascota.obtener_todas(
        termino
    )

    return render_template(

        "mascotas/listar.html",

        mascotas=mascotas,

        termino=termino

    )

@app.route("/mascotas/<int:id_mascota>")
def expediente_mascota(id_mascota):
    if not usuario_autenticado():
        return redirect("/login")

    mascota = Mascota.obtener_por_id({
        "id_mascota": id_mascota
    })
    
    if not mascota:
        flash(
            "La mascota solicitada no existe.",
            "danger"
        )
        return redirect("/mascotas")

    historial = Venta.obtener_historial_mascota(
        {
            "id_mascota": id_mascota
        }
    )

    citas = OrdenServicio.obtener_citas_mascota({
        "id_mascota": id_mascota
    })

    compras = Venta.obtener_compras_mascota(
        {
            "id_mascota": id_mascota
        }
    )

    cliente = Cliente.obtener_por_id({
        "id_cliente": mascota.id_cliente
    })

    resumen = {
        "servicios": 0,
        "compras": 0,
        "citas": 0,
        "total_gastado": 0
    }

    return render_template(
        "mascotas/expediente.html",
        mascota=mascota,
        cliente=cliente,
        resumen=resumen,
        historial=historial,
        compras=compras,
        citas=citas,
        archivos=[]
    )