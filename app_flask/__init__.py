from flask import Flask
import re
import os

from dotenv import load_dotenv
from flask_bcrypt import Bcrypt


# ==================================================
# CARGAR VARIABLES DE ENTORNO
# ==================================================

load_dotenv()


# ==================================================
# APLICACIÓN FLASK
# ==================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "petsvillage"
)


# ==================================================
# BCRYPT
# ==================================================

bcrypt = Bcrypt(app)


# ==================================================
# BASE DE DATOS
# ==================================================

BASE_DATOS = "bd_petsvillage"


# ==================================================
# VALIDACIÓN DE CORREO
# ==================================================

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$'
)