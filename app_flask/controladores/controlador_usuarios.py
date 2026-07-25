from flask import render_template, request, redirect, session, flash
from app_flask import app, bcrypt
from app_flask.modelos.modelo_usuario import Usuario


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
def formulario_registro():
    if "id_usuario" in session:
        return redirect("/dashboard")
    return render_template("registro.html")


@app.route("/registrar", methods=["POST"])
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


@app.route("/dashboard")
def dashboard():
    if "id_usuario" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")