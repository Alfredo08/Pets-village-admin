import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class ServicioCorreo:
    """
    Servicio centralizado para enviar correos
    mediante Gmail SMTP.
    """

    SMTP_HOST = os.getenv(
        "MAIL_SMTP_HOST",
        "smtp.gmail.com"
    )

    SMTP_PORT = int(
        os.getenv(
            "MAIL_SMTP_PORT",
            "587"
        )
    )

    USUARIO = os.getenv(
        "MAIL_USERNAME"
    )

    PASSWORD = os.getenv(
        "MAIL_PASSWORD"
    )

    REMITENTE = os.getenv(
        "MAIL_FROM",
        USUARIO
    )

    # ==================================================
    # CONFIGURACIÓN
    # ==================================================

    @classmethod
    def _configuracion_valida(cls):

        if not cls.USUARIO:
            return False, (
                "No está configurado MAIL_USERNAME."
            )

        if not cls.PASSWORD:
            return False, (
                "No está configurado MAIL_PASSWORD."
            )

        if not cls.REMITENTE:
            return False, (
                "No está configurado MAIL_FROM."
            )

        return True, None

    # ==================================================
    # VALIDAR CORREO
    # ==================================================

    @staticmethod
    def _correo_valido(correo):

        if not correo:
            return False

        correo = str(correo).strip()

        if "@" not in correo:
            return False

        dominio = correo.split("@")[-1]

        if "." not in dominio:
            return False

        return True

    # ==================================================
    # ENVIAR CORREO
    # ==================================================

    @classmethod
    def enviar_correo(
        cls,
        destinatario,
        asunto,
        contenido_html,
        contenido_texto=None
    ):

        # --------------------------------------------------
        # CONFIGURACIÓN
        # --------------------------------------------------

        configuracion_ok, error = (
            cls._configuracion_valida()
        )

        if not configuracion_ok:

            return {
                "exito": False,
                "mensaje": error
            }

        # --------------------------------------------------
        # DESTINATARIO
        # --------------------------------------------------

        if not cls._correo_valido(
            destinatario
        ):

            return {
                "exito": False,
                "mensaje": (
                    "El correo del destinatario "
                    "no es válido."
                )
            }

        destinatario = str(
            destinatario
        ).strip()

        # --------------------------------------------------
        # TEXTO PLANO
        # --------------------------------------------------

        if not contenido_texto:

            contenido_texto = (
                "Este correo contiene información "
                "importante de Pet Village."
            )

        # --------------------------------------------------
        # CREAR MENSAJE
        # --------------------------------------------------

        mensaje = MIMEMultipart(
            "alternative"
        )

        mensaje["From"] = cls.REMITENTE
        mensaje["To"] = destinatario
        mensaje["Subject"] = asunto

        mensaje.attach(
            MIMEText(
                contenido_texto,
                "plain",
                "utf-8"
            )
        )

        mensaje.attach(
            MIMEText(
                contenido_html,
                "html",
                "utf-8"
            )
        )

        # --------------------------------------------------
        # CONEXIÓN SMTP
        # --------------------------------------------------

        try:

            with smtplib.SMTP(
                cls.SMTP_HOST,
                cls.SMTP_PORT,
                timeout=30
            ) as servidor:

                servidor.ehlo()

                servidor.starttls()

                servidor.ehlo()

                servidor.login(
                    cls.USUARIO,
                    cls.PASSWORD
                )

                servidor.sendmail(
                    cls.REMITENTE,
                    [destinatario],
                    mensaje.as_string()
                )

        except smtplib.SMTPAuthenticationError:

            return {
                "exito": False,
                "mensaje": (
                    "Gmail rechazó la autenticación. "
                    "Verifica la cuenta y la contraseña "
                    "de aplicación."
                )
            }

        except smtplib.SMTPException as error:

            return {
                "exito": False,
                "mensaje": (
                    "Gmail rechazó el envío: "
                    f"{error}"
                )
            }

        except OSError as error:

            return {
                "exito": False,
                "mensaje": (
                    "No fue posible conectarse con "
                    f"Gmail: {error}"
                )
            }

        except Exception as error:

            return {
                "exito": False,
                "mensaje": (
                    "Error inesperado al enviar "
                    f"el correo: {error}"
                )
            }

        # --------------------------------------------------
        # ÉXITO
        # --------------------------------------------------

        return {
            "exito": True,
            "mensaje": (
                "Correo enviado correctamente."
            ),
            "destinatario": destinatario
        }

    # ==================================================
    # RECORDATORIO DE CITA
    # ==================================================

    @classmethod
    def enviar_recordatorio(
        cls,
        destinatario,
        nombre_cliente,
        nombre_mascota,
        fecha,
        hora,
        servicio
    ):

        asunto = (
            "🐾 Recordatorio de cita - Pet Village"
        )

        # ==================================================
        # TEXTO PLANO
        # ==================================================

        contenido_texto = f"""
Hola {nombre_cliente}.

Te recordamos que tienes una cita programada
en Pet Village.

Mascota: {nombre_mascota}
Fecha: {fecha}
Hora: {hora}
Servicio: {servicio}

Te esperamos.

Pet Village
Estética Canina y Felina
""".strip()

        # ==================================================
        # HTML
        # ==================================================

        contenido_html = f"""
<!DOCTYPE html>
<html lang="es">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width,
                   initial-scale=1.0">

    <title>
        Recordatorio de cita - Pet Village
    </title>

</head>

<body style="
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
    font-family: Arial, Helvetica, sans-serif;
">

    <div style="
        max-width: 600px;
        margin: 30px auto;
        background-color: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    ">

        <div style="
            padding: 25px;
            text-align: center;
        ">

            <h1 style="
                margin: 0 0 10px 0;
                font-size: 26px;
            ">
                🐾 Pet Village
            </h1>

            <p style="
                margin: 0;
                color: #666666;
                font-size: 15px;
            ">
                Estética Canina y Felina
            </p>

        </div>

        <div style="
            padding: 30px;
        ">

            <h2 style="
                margin-top: 0;
                font-size: 21px;
            ">
                Hola {nombre_cliente},
            </h2>

            <p style="
                font-size: 16px;
                line-height: 1.6;
                color: #333333;
            ">
                Te recordamos que tienes una cita
                programada para mañana en
                <strong>Pet Village</strong>.
            </p>

            <div style="
                margin: 25px 0;
                padding: 20px;
                background-color: #f7f7f7;
                border-radius: 10px;
            ">

                <p style="
                    margin: 8px 0;
                    font-size: 15px;
                ">
                    🐶 <strong>Mascota:</strong>
                    {nombre_mascota}
                </p>

                <p style="
                    margin: 8px 0;
                    font-size: 15px;
                ">
                    📅 <strong>Fecha:</strong>
                    {fecha}
                </p>

                <p style="
                    margin: 8px 0;
                    font-size: 15px;
                ">
                    🕐 <strong>Hora:</strong>
                    {hora}
                </p>

                <p style="
                    margin: 8px 0;
                    font-size: 15px;
                ">
                    ✂️ <strong>Servicio:</strong>
                    {servicio}
                </p>

            </div>

            <p style="
                font-size: 16px;
                line-height: 1.6;
                color: #333333;
            ">
                Te esperamos. 🐾
            </p>

            <p style="
                margin-top: 30px;
                font-size: 15px;
                color: #666666;
            ">
                Saludos,<br>
                <strong>Pet Village</strong><br>
                Estética Canina y Felina
            </p>

        </div>

    </div>

</body>

</html>
""".strip()

        # ==================================================
        # ENVIAR
        # ==================================================

        return cls.enviar_correo(
            destinatario=destinatario,
            asunto=asunto,
            contenido_html=contenido_html,
            contenido_texto=contenido_texto
        )