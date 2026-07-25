from decimal import Decimal, InvalidOperation

from app_flask import BASE_DATOS
from app_flask.config.mysqlconnection import connectToMySQL


class Servicio:
    TIPOS_VALIDOS = {
        "paquete",
        "complemento",
        "adicional"
    }

    TAMANOS_VALIDOS = {
        "toy_chico",
        "mediano",
        "grande",
        "extra_grande",
        "cualquier_tamano"
    }

    TIPOS_PELO_VALIDOS = {
        "corto",
        "largo",
        "cualquier_tipo"
    }

    def __init__(self, data):
        self.id_servicio = data["id_servicio"]
        self.nombre = data["nombre"]
        self.descripcion = data.get("descripcion")
        self.tipo = data["tipo"]
        self.activo = data["activo"]

        self.precio_minimo = data.get("precio_minimo")
        self.precio_maximo = data.get("precio_maximo")
        self.total_tarifas = data.get("total_tarifas", 0)

        self.tarifas = []

    @classmethod
    def obtener_todos(cls, termino=""):
        query = """
            SELECT
                s.id_servicio,
                s.nombre,
                s.descripcion,
                s.tipo,
                s.activo,
                MIN(st.precio) AS precio_minimo,
                MAX(st.precio) AS precio_maximo,
                COUNT(st.id_tarifa) AS total_tarifas
            FROM servicios s
            LEFT JOIN servicio_tarifas st
                ON st.id_servicio = s.id_servicio
                AND st.activo = 1
            WHERE (
                s.nombre LIKE %(termino)s
                OR s.descripcion LIKE %(termino)s
                OR s.tipo LIKE %(termino)s
            )
            GROUP BY
                s.id_servicio,
                s.nombre,
                s.descripcion,
                s.tipo,
                s.activo
            ORDER BY s.activo DESC, s.nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(
            query,
            {"termino": f"%{termino.strip()}%"}
        )

        if not resultados:
            return []

        return [cls(servicio) for servicio in resultados]

    @classmethod
    def obtener_activos_con_tarifas(cls):
        query = """
            SELECT
                s.id_servicio,
                s.nombre,
                s.descripcion,
                s.tipo,
                s.activo,
                MIN(st.precio) AS precio_minimo,
                MAX(st.precio) AS precio_maximo,
                COUNT(st.id_tarifa) AS total_tarifas
            FROM servicios s
            INNER JOIN servicio_tarifas st
                ON st.id_servicio = s.id_servicio
                AND st.activo = 1
            WHERE s.activo = 1
            GROUP BY
                s.id_servicio,
                s.nombre,
                s.descripcion,
                s.tipo,
                s.activo
            ORDER BY s.nombre ASC;
        """

        resultados = connectToMySQL(BASE_DATOS).query_db(query)

        if not resultados:
            return []

        servicios = []

        for data in resultados:
            servicio = cls(data)
            servicio.tarifas = cls.obtener_tarifas({
                "id_servicio": servicio.id_servicio
            })
            servicios.append(servicio)

        return servicios

    @classmethod
    def obtener_por_id(cls, data):
        query = """
            SELECT
                id_servicio,
                nombre,
                descripcion,
                tipo,
                activo
            FROM servicios
            WHERE id_servicio = %(id_servicio)s
            LIMIT 1;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, data)

        if not resultado:
            return None

        servicio = cls(resultado[0])

        servicio.tarifas = cls.obtener_tarifas({
            "id_servicio": servicio.id_servicio
        })

        return servicio

    @classmethod
    def obtener_tarifas(cls, data):
        query = """
            SELECT
                id_tarifa,
                id_servicio,
                tamano,
                tipo_pelo,
                precio,
                activo
            FROM servicio_tarifas
            WHERE id_servicio = %(id_servicio)s
              AND activo = 1
            ORDER BY
                FIELD(
                    tamano,
                    'toy_chico',
                    'mediano',
                    'grande',
                    'extra_grande',
                    'cualquier_tamano'
                ),
                FIELD(
                    tipo_pelo,
                    'corto',
                    'largo',
                    'cualquier_tipo'
                );
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, data)

        return resultado if resultado else []

    @classmethod
    def crear_con_tarifas(cls, data, tarifas):
        conexion = connectToMySQL(BASE_DATOS).connection

        try:
            conexion.begin()

            with conexion.cursor() as cursor:
                query_servicio = """
                    INSERT INTO servicios (
                        nombre,
                        descripcion,
                        tipo,
                        activo
                    )
                    VALUES (
                        %(nombre)s,
                        %(descripcion)s,
                        %(tipo)s,
                        1
                    );
                """

                cursor.execute(query_servicio, data)
                id_servicio = cursor.lastrowid

                query_tarifa = """
                    INSERT INTO servicio_tarifas (
                        id_servicio,
                        tamano,
                        tipo_pelo,
                        precio,
                        activo
                    )
                    VALUES (
                        %(id_servicio)s,
                        %(tamano)s,
                        %(tipo_pelo)s,
                        %(precio)s,
                        1
                    );
                """

                for tarifa in tarifas:
                    tarifa["id_servicio"] = id_servicio
                    cursor.execute(query_tarifa, tarifa)

            conexion.commit()
            return id_servicio

        except Exception as error:
            conexion.rollback()
            print("Error al crear servicio:", error)
            return False

        finally:
            conexion.close()

    @classmethod
    def actualizar_con_tarifas(cls, data, tarifas):
        conexion = connectToMySQL(BASE_DATOS).connection

        try:
            conexion.begin()

            with conexion.cursor() as cursor:
                query_servicio = """
                    UPDATE servicios
                    SET
                        nombre = %(nombre)s,
                        descripcion = %(descripcion)s,
                        tipo = %(tipo)s
                    WHERE id_servicio = %(id_servicio)s;
                """

                cursor.execute(query_servicio, data)

                # Las tarifas anteriores se desactivan.
                # Las enviadas por el formulario se reactivan o insertan.
                query_desactivar = """
                    UPDATE servicio_tarifas
                    SET activo = 0
                    WHERE id_servicio = %(id_servicio)s;
                """

                cursor.execute(query_desactivar, {
                    "id_servicio": data["id_servicio"]
                })

                query_actualizar_tarifa = """
                    UPDATE servicio_tarifas
                    SET
                        tamano = %(tamano)s,
                        tipo_pelo = %(tipo_pelo)s,
                        precio = %(precio)s,
                        activo = 1
                    WHERE id_tarifa = %(id_tarifa)s
                      AND id_servicio = %(id_servicio)s;
                """

                query_insertar_tarifa = """
                    INSERT INTO servicio_tarifas (
                        id_servicio,
                        tamano,
                        tipo_pelo,
                        precio,
                        activo
                    )
                    VALUES (
                        %(id_servicio)s,
                        %(tamano)s,
                        %(tipo_pelo)s,
                        %(precio)s,
                        1
                    );
                """

                for tarifa in tarifas:
                    tarifa["id_servicio"] = data["id_servicio"]

                    if tarifa.get("id_tarifa"):
                        cursor.execute(
                            query_actualizar_tarifa,
                            tarifa
                        )
                    else:
                        cursor.execute(
                            query_insertar_tarifa,
                            tarifa
                        )

            conexion.commit()
            return True

        except Exception as error:
            conexion.rollback()
            print("Error al actualizar servicio:", error)
            return False

        finally:
            conexion.close()

    @classmethod
    def cambiar_estado(cls, data):
        query = """
            UPDATE servicios
            SET activo = %(activo)s
            WHERE id_servicio = %(id_servicio)s;
        """

        return connectToMySQL(BASE_DATOS).query_db(query, data)

    @classmethod
    def obtener_tarifa_aplicable(cls, data):
        """
        Más adelante el POS utilizará este método para encontrar
        automáticamente el precio según la mascota.
        """

        query = """
            SELECT
                id_tarifa,
                id_servicio,
                tamano,
                tipo_pelo,
                precio
            FROM servicio_tarifas
            WHERE id_servicio = %(id_servicio)s
              AND activo = 1
              AND tamano IN (
                  %(tamano)s,
                  'cualquier_tamano'
              )
              AND tipo_pelo IN (
                  %(tipo_pelo)s,
                  'cualquier_tipo'
              )
            ORDER BY
                CASE
                    WHEN tamano = %(tamano)s THEN 0
                    ELSE 1
                END,
                CASE
                    WHEN tipo_pelo = %(tipo_pelo)s THEN 0
                    ELSE 1
                END
            LIMIT 1;
        """

        resultado = connectToMySQL(BASE_DATOS).query_db(query, data)

        if not resultado:
            return None

        return resultado[0]

    @classmethod
    def validar(cls, formulario, tarifas):
        errores = []

        nombre = formulario.get("nombre", "").strip()
        tipo = formulario.get("tipo", "").strip()

        if len(nombre) < 2:
            errores.append(
                "El nombre del servicio debe tener al menos 2 caracteres."
            )

        if len(nombre) > 100:
            errores.append(
                "El nombre del servicio no puede superar 100 caracteres."
            )

        if tipo not in cls.TIPOS_VALIDOS:
            errores.append(
                "Selecciona un tipo de servicio válido."
            )

        if not tarifas:
            errores.append(
                "Debes registrar al menos una tarifa."
            )

        combinaciones = set()

        for posicion, tarifa in enumerate(tarifas, start=1):
            tamano = tarifa.get("tamano")
            tipo_pelo = tarifa.get("tipo_pelo")
            precio_texto = tarifa.get("precio")

            if tamano not in cls.TAMANOS_VALIDOS:
                errores.append(
                    f"El tamaño de la tarifa {posicion} no es válido."
                )

            if tipo_pelo not in cls.TIPOS_PELO_VALIDOS:
                errores.append(
                    f"El tipo de pelo de la tarifa {posicion} no es válido."
                )

            try:
                precio = Decimal(str(precio_texto))

                if precio < 0:
                    errores.append(
                        f"El precio de la tarifa {posicion} "
                        "no puede ser negativo."
                    )

            except (InvalidOperation, TypeError, ValueError):
                errores.append(
                    f"El precio de la tarifa {posicion} no es válido."
                )

            combinacion = (tamano, tipo_pelo)

            if combinacion in combinaciones:
                errores.append(
                    "No puedes repetir la misma combinación "
                    "de tamaño y tipo de pelo."
                )

            combinaciones.add(combinacion)

        return errores