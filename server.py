from app_flask import app
from app_flask.controladores import controlador_usuarios
from app_flask.controladores import controlador_productos
from app_flask.controladores import controlador_inventario
from app_flask.controladores import controlador_servicios
from app_flask.controladores import controlador_clientes
from app_flask.controladores import controlador_mascotas
from app_flask.controladores import controlador_ordenes_servicios
from app_flask.controladores import controlador_ventas
from app_flask.controladores import controlador_caja
from app_flask.controladores import controlador_dashboard

if __name__ == "__main__":
    app.run(debug=True)