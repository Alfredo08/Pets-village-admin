from datetime import date

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session
)

from app_flask.modelos.modelo_cliente import Cliente
from app_flask.modelos.modelo_mascota import Mascota
from app_flask.modelos.modelo_servicio import Servicio

from app_flask import app
from app_flask.helpers.horarios import obtener_bloques_horarios
from app_flask.modelos.modelo_orden_servicio import OrdenServicio
from app_flask.modelos.modelo_usuario import Usuario
from app_flask.servicios.servicio_correo import ServicioCorreo


from datetime import date, timedelta

####################################################
# AGENDA
####################################################

@app.route("/agenda")
def agenda():

    if "id_usuario" not in session:
        return redirect("/login")

    fecha_seleccionada = request.args.get(
        "fecha",
        date.today().isoformat()
    )

    horarios = obtener_bloques_horarios()

    ordenes = OrdenServicio.obtener_por_fecha(
        fecha_seleccionada
    ) or []

    estilistas = Usuario.obtener_estilistas() or []

    # ==========================================
    # Construir índice de la agenda
    # ==========================================

    agenda = {}

    for orden in ordenes:

        hora = orden["hora_inicio"]

        # MySQL TIME puede llegar como timedelta
        if isinstance(hora, timedelta):

            segundos = int(
                hora.total_seconds()
            )

            horas = segundos // 3600

            minutos = (
                segundos % 3600
            ) // 60

            hora_normalizada = (
                f"{horas:02d}:{minutos:02d}"
            )

        elif hasattr(hora, "strftime"):

            hora_normalizada = (
                hora.strftime("%H:%M")
            )

        else:

            hora_normalizada = str(hora)[:5]

        duracion = int(
            orden.get(
                "duracion_minutos",
                60
            )
        )

        # Cada bloque representa 30 minutos.
        bloques_agenda = max(
            1,
            duracion // 30
        )

        orden["hora_normalizada"] = (
            hora_normalizada
        )

        orden["bloques_agenda"] = (
            bloques_agenda
        )

        llave = (
            f"{hora_normalizada}_"
            f"{orden['id_usuario']}"
        )

        if llave not in agenda:
            agenda[llave] = []

        agenda[llave].append(orden)

    return render_template(
        "agenda/listar.html",
        horarios=horarios,
        estilistas=estilistas,
        agenda=agenda,
        fecha_seleccionada=fecha_seleccionada
    )

@app.route("/agenda/enviar-recordatorios", methods=["POST"])
def enviar_recordatorios():
    from datetime import date, timedelta

    try:
        # ==========================================
        # FECHA DE MAÑANA
        # ==========================================

        manana = date.today() + timedelta(days=1)

        fecha_manana = manana.strftime("%Y-%m-%d")

        # ==========================================
        # OBTENER ÓRDENES
        # ==========================================

        ordenes = OrdenServicio.obtener_por_fecha(
            fecha_manana
        )

        enviados = 0
        omitidos = 0
        errores = 0

        detalle_errores = []

        # ==========================================
        # PROCESAR CADA ORDEN
        # ==========================================

        for orden in ordenes:

            correo = orden.get(
                "correo_cliente"
            )

            # --------------------------------------
            # SIN CORREO
            # --------------------------------------

            if not correo:

                omitidos += 1
                continue

            # --------------------------------------
            # DATOS DEL RECORDATORIO
            # --------------------------------------

            nombre_cliente = orden.get(
                "nombre_cliente",
                "Cliente"
            )

            nombre_mascota = orden.get(
                "nombre_mascota",
                "tu mascota"
            )

            nombre_servicio = orden.get(
                "nombre_servicio",
                "Servicio"
            )

            # --------------------------------------
            # FECHA
            # --------------------------------------

            fecha = orden.get(
                "fecha",
                fecha_manana
            )

            if hasattr(fecha, "strftime"):
                fecha = fecha.strftime(
                    "%d/%m/%Y"
                )

            # --------------------------------------
            # HORA
            # --------------------------------------

            hora = orden.get("hora_inicio")

            if hasattr(hora, "strftime"):
                hora = hora.strftime("%H:%M")

            elif hora:
                hora = str(hora)

            else:
                hora = "Por confirmar"

            # --------------------------------------
            # ENVIAR
            # --------------------------------------

            resultado = (
                ServicioCorreo.enviar_recordatorio(
                    destinatario=correo,
                    nombre_cliente=nombre_cliente,
                    nombre_mascota=nombre_mascota,
                    fecha=fecha,
                    hora=hora,
                    servicio=nombre_servicio
                )
            )

            # --------------------------------------
            # RESULTADO
            # --------------------------------------

            if resultado.get("exito"):

                enviados += 1

            else:

                errores += 1

                detalle_errores.append({
                    "id_orden": orden.get(
                        "id_orden"
                    ),
                    "correo": correo,
                    "mensaje": resultado.get(
                        "mensaje"
                    )
                })

        # ==========================================
        # RESPUESTA
        # ==========================================

        return {
            "exito": True,
            "fecha": fecha_manana,
            "total_ordenes": len(ordenes),
            "enviados": enviados,
            "omitidos": omitidos,
            "errores": errores,
            "detalle_errores": detalle_errores
        }

    except Exception as error:

        print(
            "Error enviando recordatorios:",
            error
        )

        return {
            "exito": False,
            "mensaje": str(error)
        }, 500

####################################################
# FORMULARIO NUEVA ORDEN
####################################################

@app.route("/agenda/nueva")
def formulario_nueva_orden():
    if "id_usuario" not in session:
        return redirect("/login")

    fecha_seleccionada = request.args.get(
        "fecha",
        date.today().isoformat()
    )

    clientes = [
        cliente
        for cliente in Cliente.obtener_todos()
        if cliente.activo
    ]

    mascotas = Mascota.obtener_todas_activas()

    servicios = Servicio.obtener_activos_con_tarifas()

    estilistas = Usuario.obtener_estilistas()

    horarios = obtener_bloques_horarios()

    formulario = session.pop(
        "formulario_orden_servicio",
        None
    )

    return render_template(
        "agenda/nuevo.html",
        clientes=clientes,
        mascotas=mascotas,
        servicios=servicios,
        estilistas=estilistas,
        horarios=horarios,
        fecha_seleccionada=fecha_seleccionada,
        formulario=formulario
    )


####################################################
# CREAR ORDEN
####################################################

@app.route("/agenda/crear", methods=["POST"])
def crear_orden_servicio():
    if "id_usuario" not in session:
        return redirect("/login")

    errores = OrdenServicio.validar(request.form)

    if errores:
        for error in errores:
            flash(error, "danger")

        session["formulario_orden_servicio"] = (
            request.form.to_dict()
        )

        fecha = request.form.get(
            "fecha",
            date.today().isoformat()
        )

        return redirect(
            f"/agenda/nueva?fecha={fecha}"
        )

    id_cliente = int(request.form["id_cliente"])
    id_mascota = int(request.form["id_mascota"])
    id_usuario = int(request.form["id_usuario"])
    duracion = int(request.form["duracion_minutos"])

    fecha = request.form["fecha"]
    hora_inicio = request.form["hora_inicio"]

    if not Mascota.pertenece_a_cliente(
        id_mascota,
        id_cliente
    ):
        flash(
            "La mascota seleccionada no pertenece al cliente.",
            "danger"
        )

        session["formulario_orden_servicio"] = (
            request.form.to_dict()
        )

        return redirect(
            f"/agenda/nueva?fecha={fecha}"
        )

    disponible = OrdenServicio.estilista_disponible(
        id_usuario,
        fecha,
        hora_inicio,
        duracion
    )

    if not disponible:
        flash(
            "El estilista ya tiene una orden que se cruza "
            "con ese horario.",
            "danger"
        )

        session["formulario_orden_servicio"] = (
            request.form.to_dict()
        )

        return redirect(
            f"/agenda/nueva?fecha={fecha}"
        )

    data = {
        "id_cliente": id_cliente,
        "id_mascota": id_mascota,
        "id_servicio": int(
            request.form["id_servicio"]
        ),
        "id_usuario": id_usuario,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "duracion_minutos": duracion,
        "estado": request.form.get(
            "estado",
            "pendiente"
        ),
        "notas": (
            request.form.get("notas", "").strip() or None
        )
    }

    if OrdenServicio.existe_orden_duplicada(data):
        flash(
            "Ya existe una orden idéntica para esa mascota, "
            "estilista, fecha y horario.",
            "warning"
        )

        session["formulario_orden_servicio"] = (
            request.form.to_dict()
        )

        return redirect(
            f"/agenda/nueva?fecha={fecha}"
        )

    resultado = OrdenServicio.crear(data)

    if resultado is False:

        flash(
            "No fue posible registrar la orden.",
            "danger"
        )

        return redirect(
            f"/agenda/nueva?fecha={fecha}"
        )

    session.pop(
        "formulario_orden_servicio",
        None
    )

    flash(
        (
            f"Orden {resultado['folio']} "
            "registrada correctamente."
        ),
        "success"
    )

    return redirect(
        f"/agenda?fecha={fecha}"
    )

####################################################
# DETALLE DE ORDEN
####################################################

@app.route("/agenda/orden/<int:id_orden>")
def detalle_orden(id_orden):

    if "id_usuario" not in session:
        return redirect("/login")

    orden = OrdenServicio.obtener_por_id(
        {
            "id_orden": id_orden
        }
    )

    if not orden:

        flash(
            "La orden no existe.",
            "danger"
        )

        return redirect("/agenda")

    return render_template(

        "agenda/detalle.html",

        orden=orden

    )

####################################################
# CAMBIAR ESTADO DE ORDEN
####################################################

@app.route(
    "/agenda/orden/<int:id_orden>/estado",
    methods=["POST"]
)
def cambiar_estado_orden(id_orden):
    if "id_usuario" not in session:
        return redirect("/login")

    orden = OrdenServicio.obtener_por_id({
        "id_orden": id_orden
    })

    if not orden:
        flash(
            "La orden solicitada no existe.",
            "danger"
        )
        return redirect("/agenda")

    nuevo_estado = request.form.get(
        "estado",
        ""
    ).strip()

    if nuevo_estado not in OrdenServicio.ESTADOS_VALIDOS:
        flash(
            "El estado seleccionado no es válido.",
            "danger"
        )
        return redirect(
            f"/agenda/orden/{id_orden}"
        )

    # No permitimos modificar una orden ya finalizada
    # hasta implementar cancelaciones administrativas.
    if orden["estado"] == "finalizada":
        flash(
            "Una orden finalizada ya no puede cambiar de estado.",
            "warning"
        )
        return redirect(
            f"/agenda/orden/{id_orden}"
        )

    resultado = OrdenServicio.cambiar_estado({
        "id_orden": id_orden,
        "estado": nuevo_estado
    })

    if resultado is False:
        flash(
            "No fue posible actualizar el estado de la orden.",
            "danger"
        )
    else:
        mensajes = {
            "pendiente": "Orden marcada como pendiente.",
            "confirmada": "Orden confirmada correctamente.",
            "en_proceso": "Servicio iniciado correctamente.",
            "finalizada": "Orden finalizada correctamente.",
            "cancelada": "Orden cancelada correctamente.",
            "no_asistio": "Orden marcada como no asistió."
        }

        flash(
            mensajes[nuevo_estado],
            "success"
        )

    return redirect(
        f"/agenda/orden/{id_orden}"
    )

####################################################
# FORMULARIO EDITAR ORDEN
####################################################

@app.route("/agenda/orden/<int:id_orden>/editar")
def editar_orden(id_orden):

    if "id_usuario" not in session:
        return redirect("/login")

    orden = OrdenServicio.obtener_por_id(
        {
            "id_orden": id_orden
        }
    )

    if not orden:

        flash(
            "La orden no existe.",
            "danger"
        )

        return redirect("/agenda")

    clientes = [
        cliente
        for cliente in Cliente.obtener_todos()
        if cliente.activo
    ]

    mascotas = Mascota.obtener_todas_activas()

    servicios = Servicio.obtener_activos_con_tarifas()

    estilistas = Usuario.obtener_estilistas()

    horarios = obtener_bloques_horarios()

    # ==========================================
    # Recuperar datos enviados si hubo errores
    # ==========================================

    formulario_guardado = session.pop(
        f"formulario_orden_servicio_{id_orden}",
        None
    )

    return render_template(

        "agenda/editar.html",

        orden=orden,

        clientes=clientes,

        mascotas=mascotas,

        servicios=servicios,

        estilistas=estilistas,

        horarios=horarios,

        formulario=formulario_guardado or orden,

        fecha_seleccionada=orden["fecha"]

    )

####################################################
# ACTUALIZAR ORDEN
####################################################

@app.route(
    "/agenda/orden/<int:id_orden>/actualizar",
    methods=["POST"]
)
def actualizar_orden(id_orden):
    if "id_usuario" not in session:
        return redirect("/login")

    orden = OrdenServicio.obtener_por_id({
        "id_orden": id_orden
    })

    if not orden:
        flash(
            "La orden solicitada no existe.",
            "danger"
        )
        return redirect("/agenda")

    if orden["estado"] in {
        "finalizada",
        "cancelada",
        "no_asistio"
    }:
        flash(
            "Esta orden ya no puede editarse.",
            "warning"
        )
        return redirect(
            f"/agenda/orden/{id_orden}"
        )

    errores = OrdenServicio.validar(request.form)

    if errores:
        for error in errores:
            flash(error, "danger")

        session[
            f"formulario_orden_servicio_{id_orden}"
        ] = request.form.to_dict()

        return redirect(
            f"/agenda/orden/{id_orden}/editar"
        )

    id_cliente = int(request.form["id_cliente"])
    id_mascota = int(request.form["id_mascota"])
    id_usuario = int(request.form["id_usuario"])
    duracion = int(request.form["duracion_minutos"])

    fecha = request.form["fecha"]
    hora_inicio = request.form["hora_inicio"]

    if not Mascota.pertenece_a_cliente(
        id_mascota,
        id_cliente
    ):
        flash(
            "La mascota seleccionada no pertenece al cliente.",
            "danger"
        )

        return redirect(
            f"/agenda/orden/{id_orden}/editar"
        )

    disponible = OrdenServicio.estilista_disponible(
        id_usuario,
        fecha,
        hora_inicio,
        duracion,
        id_orden_ignorar=id_orden
    )

    if not disponible:
        flash(
            "El estilista ya tiene una orden que se cruza "
            "con ese horario.",
            "danger"
        )

        session[
            f"formulario_orden_servicio_{id_orden}"
        ] = request.form.to_dict()

        return redirect(
            f"/agenda/orden/{id_orden}/editar"
        )

    data = {
        "id_orden": id_orden,
        "id_cliente": id_cliente,
        "id_mascota": id_mascota,
        "id_servicio": int(
            request.form["id_servicio"]
        ),
        "id_usuario": id_usuario,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "duracion_minutos": duracion,
        "estado": request.form.get(
            "estado",
            orden["estado"]
        ),
        "notas": (
            request.form.get("notas", "").strip() or None
        )
    }

    resultado = OrdenServicio.actualizar(data)

    if resultado is False:
        flash(
            "No fue posible actualizar la orden.",
            "danger"
        )

        return redirect(
            f"/agenda/orden/{id_orden}/editar"
        )

    session.pop(
        f"formulario_orden_servicio_{id_orden}",
        None
    )

    flash(
        "Orden actualizada correctamente.",
        "success"
    )

    return redirect(
        f"/agenda/orden/{id_orden}"
    )