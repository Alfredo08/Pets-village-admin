from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session
)

from app_flask.servicios.servicio_impresion import (
    ServicioImpresion
)

from datetime import date

from app_flask import app
from app_flask.modelos.modelo_orden_servicio import OrdenServicio
from app_flask.modelos.modelo_producto import Producto
from app_flask.modelos.modelo_servicio import Servicio
from app_flask.modelos.modelo_venta import Venta

def usuario_autenticado():
    return "id_usuario" in session


####################################################
# NUEVA VENTA DESDE UNA ORDEN
####################################################

@app.route("/ventas/nueva")
def nueva_venta():
    if not usuario_autenticado():
        return redirect("/login")

    id_orden = request.args.get(
        "orden",
        ""
    ).strip()

    if not id_orden.isdigit():
        flash(
            "Debes abrir el Punto de Venta desde una orden válida.",
            "danger"
        )
        return redirect("/agenda")

    orden = OrdenServicio.obtener_para_pos({
        "id_orden": int(id_orden)
    })

    if not orden:
        flash(
            "La orden de servicio no existe.",
            "danger"
        )
        return redirect("/agenda")

    if orden["id_venta"]:
        flash(
            "Esta orden ya tiene una venta registrada.",
            "warning"
        )
        return redirect(
            f"/agenda/orden/{orden['id_orden']}"
        )

    if orden["estado"] not in {
        "confirmada",
        "en_proceso"
    }:
        flash(
            "La orden debe estar confirmada o en proceso "
            "para abrir el Punto de Venta.",
            "warning"
        )
        return redirect(
            f"/agenda/orden/{orden['id_orden']}"
        )

    # Al abrir el POS desde una orden confirmada,
    # cambia automáticamente a en proceso.
    if orden["estado"] == "confirmada":
        resultado = OrdenServicio.cambiar_estado({
            "id_orden": orden["id_orden"],
            "estado": "en_proceso"
        })

        if resultado is False:
            flash(
                "No fue posible iniciar la orden.",
                "danger"
            )
            return redirect(
                f"/agenda/orden/{orden['id_orden']}"
            )

        orden["estado"] = "en_proceso"

    tarifa = Servicio.obtener_tarifa_aplicable({
        "id_servicio": orden["id_servicio"],
        "tamano": orden["tamano"],
        "tipo_pelo": orden["tipo_pelo"]
    })

    if not tarifa:
        flash(
            "No existe una tarifa aplicable para el servicio "
            "y las características de la mascota.",
            "danger"
        )
        return redirect(
            f"/agenda/orden/{orden['id_orden']}"
        )

    productos = Producto.obtener_disponibles_pos()

    return render_template(
        "ventas/nueva.html",
        orden=orden,
        tarifa=tarifa,
        productos=productos
    )

####################################################
# PROCESAR COBRO
####################################################

@app.route("/ventas/cobrar", methods=["POST"])
def cobrar_venta():
    if "id_usuario" not in session:
        return jsonify({
            "exito": False,
            "mensaje": "Tu sesión ha expirado."
        }), 401

    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({
            "exito": False,
            "mensaje": "No se recibieron datos para registrar la venta."
        }), 400

    try:
        id_orden = int(payload.get("id_orden", 0))
        id_tarifa = int(payload.get("id_tarifa", 0))
    except (TypeError, ValueError):
        return jsonify({
            "exito": False,
            "mensaje": "La orden o la tarifa no son válidas."
        }), 400

    if id_orden <= 0 or id_tarifa <= 0:
        return jsonify({
            "exito": False,
            "mensaje": "La orden o la tarifa no son válidas."
        }), 400

    productos = payload.get("productos", [])
    pagos = payload.get("pagos", [])

    if not isinstance(productos, list):
        return jsonify({
            "exito": False,
            "mensaje": "La lista de productos no es válida."
        }), 400

    if not isinstance(pagos, list) or not pagos:
        return jsonify({
            "exito": False,
            "mensaje": "Debes registrar al menos un pago."
        }), 400

    servicio_payload = payload.get(
        "servicio",
        {}
    )

    if not isinstance(servicio_payload, dict):
        return jsonify({
            "exito": False,
            "mensaje": (
                "La información del servicio "
                "no es válida."
            )
        }), 400

    data = {
        "id_orden": id_orden,
        "id_usuario": session["id_usuario"],

        "servicio": {
            "id_tarifa": id_tarifa,
            "descuento_porcentaje": (
                servicio_payload.get(
                    "descuento_porcentaje",
                    0
                )
            )
        },

        "productos": productos,
        "pagos": pagos,

        "impuestos": payload.get("impuestos", "0.00")
    }

    resultado = Venta.registrar(data)

    if not resultado["exito"]:
        return jsonify({
            "exito": False,
            "mensaje": resultado["mensaje"]
        }), 400

    flash(
        f"Venta {resultado['folio']} registrada correctamente.",
        "success"
    )

    return jsonify({
        "exito": True,
        "mensaje": "Venta registrada correctamente.",
        "id_venta": resultado["id_venta"],
        "folio": resultado["folio"],
        "total": str(resultado["total"]),
        "total_pagado": str(resultado["total_pagado"]),
        "cambio": str(resultado["cambio"]),
        "url_redireccion": (
            f"/ventas/{resultado['id_venta']}"
        )
    }), 201


####################################################
# DETALLE DE VENTA / TICKET
####################################################

@app.route("/ventas/<int:id_venta>")
def detalle_venta(id_venta):
    if "id_usuario" not in session:
        return redirect("/login")

    venta = Venta.obtener_por_id({
        "id_venta": id_venta
    })

    if not venta:
        flash(
            "La venta solicitada no existe.",
            "danger"
        )
        return redirect("/agenda")

    detalles = Venta.obtener_detalles({
        "id_venta": id_venta
    })

    pagos = Venta.obtener_pagos({
        "id_venta": id_venta
    })

    total_pagado = sum(
        pago["monto"]
        for pago in pagos
    )

    cambio = total_pagado - venta["total"]

    return render_template(
        "ventas/detalle.html",
        venta=venta,
        detalles=detalles,
        pagos=pagos,
        total_pagado=total_pagado,
        cambio=max(cambio, 0)
    )

####################################################
# BANDEJA GENERAL DEL POS
####################################################

@app.route("/pos")
def punto_venta():
    if "id_usuario" not in session:
        return redirect("/login")

    fecha_seleccionada = request.args.get(
        "fecha",
        date.today().isoformat()
    ).strip()

    termino = request.args.get(
        "buscar",
        ""
    ).strip()

    ordenes = OrdenServicio.obtener_pendientes_pos(
        fecha=fecha_seleccionada,
        termino=termino
    )

    return render_template(
        "ventas/pos.html",
        ordenes=ordenes,
        fecha_seleccionada=fecha_seleccionada,
        termino=termino
    )

####################################################
# IMPRIMIR TICKET TÉRMICO
####################################################

@app.route(
    "/ventas/<int:id_venta>/imprimir",
    methods=["POST"]
)
def imprimir_ticket_venta(id_venta):

    if "id_usuario" not in session:
        return redirect("/login")

    venta = Venta.obtener_por_id({
        "id_venta": id_venta
    })

    if not venta:
        flash(
            "La venta solicitada no existe.",
            "danger"
        )

        return redirect("/caja")

    detalles = Venta.obtener_detalles({
        "id_venta": id_venta
    })

    pagos = Venta.obtener_pagos({
        "id_venta": id_venta
    })

    if not detalles:
        flash(
            "La venta no tiene conceptos para imprimir.",
            "warning"
        )

        return redirect(
            f"/ventas/{id_venta}"
        )

    resultado = ServicioImpresion.imprimir_ticket(
        venta=venta,
        detalles=detalles,
        pagos=pagos,
        abrir_cajon=False
    )

    if not resultado["exito"]:

        print(
            "Error al imprimir ticket:",
            resultado["mensaje"]
        )

        flash(
            "No fue posible imprimir el ticket. "
            + resultado["mensaje"],
            "danger"
        )

        return redirect(
            f"/ventas/{id_venta}"
        )

    flash(
        "Ticket enviado correctamente a la impresora.",
        "success"
    )

    return redirect(
        f"/ventas/{id_venta}"
    )

####################################################
# FORMULARIO DE VENTA RÁPIDA
####################################################

@app.route("/ventas/rapida")
def nueva_venta_rapida():
    if "id_usuario" not in session:
        return redirect("/login")

    productos = Producto.obtener_disponibles_pos()

    return render_template(
        "ventas/rapida.html",
        productos=productos
    )

####################################################
# PROCESAR VENTA RÁPIDA
####################################################

@app.route(
    "/ventas/rapida/cobrar",
    methods=["POST"]
)
def cobrar_venta_rapida():

    if "id_usuario" not in session:
        return jsonify({
            "exito": False,
            "mensaje": "Tu sesión ha expirado."
        }), 401

    payload = request.get_json(
        silent=True
    )

    if not payload:
        return jsonify({
            "exito": False,
            "mensaje": (
                "No se recibieron datos "
                "para registrar la venta."
            )
        }), 400

    productos = payload.get(
        "productos",
        []
    )

    pagos = payload.get(
        "pagos",
        []
    )

    if (
        not isinstance(productos, list)
        or not productos
    ):
        return jsonify({
            "exito": False,
            "mensaje": (
                "Debes agregar al menos "
                "un producto."
            )
        }), 400

    if (
        not isinstance(pagos, list)
        or not pagos
    ):
        return jsonify({
            "exito": False,
            "mensaje": (
                "Debes registrar al menos "
                "un pago."
            )
        }), 400

    id_cliente = payload.get(
        "id_cliente"
    )

    if id_cliente in {
        "",
        None
    }:
        id_cliente = None

    data = {
        "id_usuario": session[
            "id_usuario"
        ],

        "id_cliente": id_cliente,

        "nombre_cliente_rapido": (
            payload.get(
                "nombre_cliente_rapido",
                ""
            ).strip()
        ),

        "productos": productos,

        "pagos": pagos,

        "impuestos": payload.get(
            "impuestos",
            "0.00"
        )
    }

    resultado = (
        Venta.registrar_venta_rapida(
            data
        )
    )

    if not resultado["exito"]:
        return jsonify({
            "exito": False,
            "mensaje": resultado[
                "mensaje"
            ]
        }), 400

    flash(
        f"Venta {resultado['folio']} "
        "registrada correctamente.",
        "success"
    )

    return jsonify({
        "exito": True,
        "mensaje": (
            "Venta registrada correctamente."
        ),
        "id_venta": resultado[
            "id_venta"
        ],
        "folio": resultado[
            "folio"
        ],
        "total": str(
            resultado["total"]
        ),
        "total_pagado": str(
            resultado["total_pagado"]
        ),
        "cambio": str(
            resultado["cambio"]
        ),
        "url_redireccion": (
            f"/ventas/"
            f"{resultado['id_venta']}"
        )
    }), 201