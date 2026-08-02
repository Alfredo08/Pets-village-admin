from flask import (
    flash,
    redirect,
    render_template,
    request,
    session
)
from app_flask.utilidades.decoradores import admin_requerido

from flask_bcrypt import Bcrypt

from app_flask import app
from app_flask.modelos.modelo_usuario import Usuario


bcrypt = Bcrypt(app)


####################################################
# VALIDAR ADMINISTRADOR
####################################################

def administrador_autenticado():
    return (
        "id_usuario" in session
        and session.get("rol") in {
            "admin",
            "recepcion"
        }
    )


####################################################
# LISTAR USUARIOS
####################################################

@app.route("/usuarios")
@admin_requerido
def listar_usuarios():
    if "id_usuario" not in session:
        return redirect("/login")

    if not administrador_autenticado():
        flash(
            "No tienes permisos para administrar usuarios.",
            "danger"
        )
        return redirect("/dashboard")

    termino = request.args.get(
        "buscar",
        ""
    ).strip()

    usuarios = Usuario.obtener_todos(
        termino
    )

    return render_template(
        "usuarios/listar.html",
        usuarios=usuarios,
        termino=termino
    )


####################################################
# FORMULARIO NUEVO USUARIO
####################################################

@app.route("/usuarios/nuevo")
@admin_requerido
def formulario_nuevo_usuario():
    if "id_usuario" not in session:
        return redirect("/login")

    if not administrador_autenticado():
        flash(
            "No tienes permisos para crear usuarios.",
            "danger"
        )
        return redirect("/dashboard")

    formulario = session.pop(
        "formulario_usuario",
        None
    )

    return render_template(
        "usuarios/nuevo.html",
        formulario=formulario
    )


####################################################
# CREAR USUARIO
####################################################

@app.route(
    "/usuarios/crear",
    methods=["POST"]
)
@admin_requerido
def crear_usuario():
    if "id_usuario" not in session:
        return redirect("/login")

    if not administrador_autenticado():
        flash(
            "No tienes permisos para crear usuarios.",
            "danger"
        )
        return redirect("/dashboard")

    errores = Usuario.validar_creacion(
        request.form
    )

    if errores:
        for error in errores:
            flash(error, "danger")

        formulario = request.form.to_dict()
        formulario.pop("password", None)
        formulario.pop(
            "confirmar_password",
            None
        )

        session["formulario_usuario"] = formulario

        return redirect("/usuarios/nuevo")

    rol = request.form["rol"].strip()

    es_estilista = (
        request.form.get("es_estilista") == "1"
        or rol == "estilista"
    )

    if es_estilista:
        color_agenda = (
            request.form.get(
                "color_agenda",
                "#3B82F6"
            ).strip()
            or "#3B82F6"
        )

        orden_agenda = int(
            request.form.get(
                "orden_agenda",
                1
            )
        )
    else:
        color_agenda = None
        orden_agenda = 0

    password_hash = (
        bcrypt.generate_password_hash(
            request.form["password"]
        ).decode("utf-8")
    )

    data = {
        "nombre": request.form[
            "nombre"
        ].strip(),

        "correo": request.form[
            "correo"
        ].strip().lower(),

        "password_hash": password_hash,

        "rol": rol,

        "es_estilista": (
            1 if es_estilista else 0
        ),

        "color_agenda": color_agenda,

        "orden_agenda": orden_agenda
    }

    id_usuario = Usuario.crear(data)

    if not id_usuario:
        flash(
            "No fue posible registrar el usuario.",
            "danger"
        )

        return redirect("/usuarios/nuevo")

    session.pop(
        "formulario_usuario",
        None
    )

    flash(
        "Usuario registrado correctamente.",
        "success"
    )

    return redirect("/usuarios")


@app.route("/")
def index():
    if "id_usuario" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/login")
def formulario_login():
    if "id_usuario" in session:
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/registro")
@admin_requerido
def formulario_registro():
    if "id_usuario" in session:
        return redirect("/dashboard")
    return render_template("registro.html")


@app.route("/registrar", methods=["POST"])
@admin_requerido
def registrar_usuario():
    errores = Usuario.validar_registro(request.form)

    if errores:
        for error in errores:
            flash(error, "registro")
        return redirect("/registro")

    password_hash = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

    data = {
        "nombre": request.form["nombre"],
        "correo": request.form["correo"],
        "password_hash": password_hash,
        "rol": request.form["rol"]
    }

    id_usuario = Usuario.crear(data)

    session["id_usuario"] = id_usuario
    session["nombre"] = request.form["nombre"]
    session["rol"] = request.form["rol"]

    return redirect("/dashboard")


@app.route("/procesar_login", methods=["POST"])
def procesar_login():
    usuario = Usuario.obtener_por_correo({
        "correo": request.form["correo"]
    })

    if not usuario:
        flash("Correo o contraseña incorrectos.", "login")
        return redirect("/login")

    if not usuario.activo:
        flash("Este usuario está desactivado.", "login")
        return redirect("/login")

    if not bcrypt.check_password_hash(usuario.password_hash, request.form["password"]):
        flash("Correo o contraseña incorrectos.", "login")
        return redirect("/login")

    session["id_usuario"] = usuario.id_usuario
    session["nombre"] = usuario.nombre
    session["rol"] = usuario.rol

    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

####################################################
# FORMULARIO EDITAR USUARIO
####################################################

@app.route("/usuarios/<int:id_usuario>/editar")
@admin_requerido
def formulario_editar_usuario(id_usuario):
    if "id_usuario" not in session:
        return redirect("/login")

    if not administrador_autenticado():
        flash(
            "No tienes permisos para editar usuarios.",
            "danger"
        )
        return redirect("/dashboard")

    usuario = Usuario.obtener_por_id({
        "id_usuario": id_usuario
    })

    if not usuario:
        flash(
            "El usuario solicitado no existe.",
            "danger"
        )
        return redirect("/usuarios")

    formulario_guardado = session.pop(
        f"formulario_usuario_{id_usuario}",
        None
    )

    return render_template(
        "usuarios/editar.html",
        usuario=usuario,
        formulario=formulario_guardado
    )

####################################################
# ACTUALIZAR USUARIO
####################################################

@app.route(
    "/usuarios/<int:id_usuario>/actualizar",
    methods=["POST"]
)
@admin_requerido
def actualizar_usuario(id_usuario):
    if "id_usuario" not in session:
        return redirect("/login")

    if not administrador_autenticado():
        flash(
            "No tienes permisos para actualizar usuarios.",
            "danger"
        )
        return redirect("/dashboard")

    usuario = Usuario.obtener_por_id({
        "id_usuario": id_usuario
    })

    if not usuario:
        flash(
            "El usuario solicitado no existe.",
            "danger"
        )
        return redirect("/usuarios")

    errores = Usuario.validar_edicion(
        request.form,
        id_usuario
    )

    if errores:
        for error in errores:
            flash(error, "danger")

        session[
            f"formulario_usuario_{id_usuario}"
        ] = request.form.to_dict()

        return redirect(
            f"/usuarios/{id_usuario}/editar"
        )

    nuevo_rol = request.form[
        "rol"
    ].strip()

    # Evitar eliminar el último administrador activo.
    if (
        usuario.rol == "admin"
        and nuevo_rol != "admin"
        and usuario.activo
        and Usuario.contar_administradores_activos() <= 1
    ):
        flash(
            "No puedes cambiar el rol del único "
            "administrador activo.",
            "warning"
        )

        return redirect(
            f"/usuarios/{id_usuario}/editar"
        )

    es_estilista = (
        request.form.get("es_estilista") == "1"
        or nuevo_rol == "estilista"
    )

    if es_estilista:
        color_agenda = (
            request.form.get(
                "color_agenda",
                "#3B82F6"
            ).strip()
            or "#3B82F6"
        )

        orden_agenda = int(
            request.form.get(
                "orden_agenda",
                1
            )
        )

    else:
        color_agenda = None
        orden_agenda = 0

    data = {
        "id_usuario": id_usuario,

        "nombre": request.form[
            "nombre"
        ].strip(),

        "correo": request.form[
            "correo"
        ].strip().lower(),

        "rol": nuevo_rol,

        "es_estilista": (
            1 if es_estilista else 0
        ),

        "color_agenda": color_agenda,

        "orden_agenda": orden_agenda
    }

    resultado = Usuario.actualizar(data)

    if resultado is False:
        flash(
            "No fue posible actualizar el usuario.",
            "danger"
        )

        return redirect(
            f"/usuarios/{id_usuario}/editar"
        )

    # Si el usuario editó su propia cuenta,
    # actualizamos los datos conservados en sesión.
    if id_usuario == session["id_usuario"]:
        session["nombre"] = data["nombre"]
        session["rol"] = data["rol"]

    session.pop(
        f"formulario_usuario_{id_usuario}",
        None
    )

    flash(
        "Usuario actualizado correctamente.",
        "success"
    )

    return redirect("/usuarios")

####################################################
# ACTIVAR / DESACTIVAR USUARIO
####################################################

@app.route(
    "/usuarios/<int:id_usuario>/estado",
    methods=["POST"]
)
@admin_requerido
def cambiar_estado_usuario(id_usuario):
    if "id_usuario" not in session:
        return redirect("/login")

    if not administrador_autenticado():
        flash(
            "No tienes permisos para cambiar "
            "el estado de los usuarios.",
            "danger"
        )
        return redirect("/dashboard")

    usuario = Usuario.obtener_por_id({
        "id_usuario": id_usuario
    })

    if not usuario:
        flash(
            "El usuario solicitado no existe.",
            "danger"
        )
        return redirect("/usuarios")

    nuevo_estado = (
        request.form.get("activo") == "1"
    )

    if (
        id_usuario == session["id_usuario"]
        and not nuevo_estado
    ):
        flash(
            "No puedes desactivar tu propia cuenta.",
            "warning"
        )
        return redirect("/usuarios")

    if (
        usuario.rol == "admin"
        and usuario.activo
        and not nuevo_estado
        and Usuario.contar_administradores_activos() <= 1
    ):
        flash(
            "No puedes desactivar al único "
            "administrador activo.",
            "warning"
        )
        return redirect("/usuarios")

    resultado = Usuario.cambiar_estado({
        "id_usuario": id_usuario,
        "activo": 1 if nuevo_estado else 0
    })

    if resultado is False:
        flash(
            "No fue posible cambiar el estado del usuario.",
            "danger"
        )
    else:
        mensaje = (
            "Usuario activado correctamente."
            if nuevo_estado
            else "Usuario desactivado correctamente."
        )

        flash(mensaje, "success")

    return redirect("/usuarios")

####################################################
# CAMBIAR CONTRASEÑA
####################################################

@app.route(
    "/usuarios/<int:id_usuario>/password",
    methods=["POST"]
)
@admin_requerido
def cambiar_password_usuario(id_usuario):
    if "id_usuario" not in session:
        return redirect("/login")

    if not administrador_autenticado():
        flash(
            "No tienes permisos para cambiar contraseñas.",
            "danger"
        )
        return redirect("/dashboard")

    usuario = Usuario.obtener_por_id({
        "id_usuario": id_usuario
    })

    if not usuario:
        flash(
            "El usuario solicitado no existe.",
            "danger"
        )
        return redirect("/usuarios")

    password = request.form.get(
        "password",
        ""
    )

    confirmar_password = request.form.get(
        "confirmar_password",
        ""
    )

    errores = []

    if len(password) < 6:
        errores.append(
            "La contraseña debe tener al menos 6 caracteres."
        )

    if password != confirmar_password:
        errores.append(
            "Las contraseñas no coinciden."
        )

    if errores:
        for error in errores:
            flash(error, "danger")

        return redirect(
            f"/usuarios/{id_usuario}/editar"
        )

    password_hash = (
        bcrypt.generate_password_hash(
            password
        ).decode("utf-8")
    )

    resultado = Usuario.actualizar_password({
        "id_usuario": id_usuario,
        "password_hash": password_hash
    })

    if resultado is False:
        flash(
            "No fue posible actualizar la contraseña.",
            "danger"
        )
    else:
        flash(
            "Contraseña actualizada correctamente.",
            "success"
        )

    return redirect(
        f"/usuarios/{id_usuario}/editar"
    )