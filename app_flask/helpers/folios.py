def generar_folio(prefijo, numero):
    """
    generar_folio("OS",15)

    ↓

    OS-000015
    """

    return f"{prefijo}-{numero:06d}"