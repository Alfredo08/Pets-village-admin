from functools import wraps

from flask import (
    flash,
    redirect,
    session
)


def login_requerido(funcion):
    @wraps(funcion)
    def funcion_protegida(*args, **kwargs):

        if "id_usuario" not in session:
            return redirect("/login")

        return funcion(*args, **kwargs)

    return funcion_protegida


def admin_requerido(funcion):
    @wraps(funcion)
    def funcion_protegida(*args, **kwargs):

        if "id_usuario" not in session:
            return redirect("/login")

        if session.get("rol") != "admin":
            flash(
                "No tienes permisos para acceder a esta sección.",
                "danger"
            )

            return redirect("/dashboard")

        return funcion(*args, **kwargs)

    return funcion_protegida