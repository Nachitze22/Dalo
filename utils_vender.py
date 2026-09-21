import idiomas


def _ficha_tecnica_categorias():
    return {
        idiomas.t("cat_carteras"): [idiomas.t("paso_info_color"), idiomas.t("paso_info_material"), "Tipo de cierre", "Dimensiones"],
        idiomas.t("cat_mochilas"): ["Capacidad (L)", idiomas.t("paso_info_material"), "Compartimentos", "Impermeable"],
        idiomas.t("cat_remeras"): ["Talle", "Género", "Tipo de tela", "Cuello"],
        idiomas.t("cat_pantalones"): ["Talle", "Género", "Tipo de tela", "Calce"],
        idiomas.t("cat_camisas"): ["Talle", "Género", "Tipo de tela", "Tipo de manga"],
        idiomas.t("cat_electronica"): ["RAM", "Almacenamiento", "Procesador", "Pantalla", "Batería"],
        idiomas.t("cat_hogar"): ["Capacidad", "Consumo (W)", "Medidas", idiomas.t("paso_info_material")],
        idiomas.t("cat_general"): [idiomas.t("paso_info_material"), idiomas.t("paso_info_color"), "Medidas"],
    }


# Se generan dinámicamente para reflejar el idioma actual en cada uso
FICHA_TECNICA_CATEGORIAS = _ficha_tecnica_categorias()

CATEGORIAS_DISPONIBLES = [
    idiomas.t("cat_carteras"), idiomas.t("cat_mochilas"), idiomas.t("cat_remeras"),
    idiomas.t("cat_pantalones"), idiomas.t("cat_camisas"), idiomas.t("cat_electronica"),
    idiomas.t("cat_hogar"), idiomas.t("cat_general"),
]

ESTADOS_PRODUCTO = [idiomas.t("estado_nuevo"), idiomas.t("estado_usado"), idiomas.t("estado_reacondicionado")]

TIPOS_ENVIO = [
    ("retiro", idiomas.t("envio_solo_retiro")),
    ("envio", idiomas.t("envio_a_domicilio")),
    ("ambos", idiomas.t("envio_ambos")),
]

MEDIOS_PAGO_DISPONIBLES = [
    ("tarjeta_credito", "💳", idiomas.t("medio_tarjeta_credito")),
    ("tarjeta_debito", "💳", idiomas.t("medio_tarjeta_debito")),
    ("transferencia", "🏦", idiomas.t("medio_transferencia")),
    ("billetera_virtual", "📱", idiomas.t("medio_billetera_virtual")),
    ("contra_entrega", "💵", idiomas.t("medio_contra_entrega")),
]

PASOS_WIZARD = [
    idiomas.t("vend_paso_fotos"), idiomas.t("vend_paso_info"), idiomas.t("vend_paso_ficha"),
    idiomas.t("vend_paso_precio"), idiomas.t("vend_paso_pago"), idiomas.t("vend_paso_ia"),
    idiomas.t("vend_paso_preview"),
]


def validar_info_producto(datos):
    errores = []
    if len((datos.get("titulo") or "").strip()) < 10:
        errores.append(idiomas.t("paso_ia_titulo_min"))
    if not (datos.get("subtitulo") or "").strip():
        errores.append("...")
    if len((datos.get("descripcion") or "").strip()) < 100:
        errores.append(idiomas.t("paso_ia_desc_min"))
    campos_obligatorios = ["categoria", "subcategoria", "estado_producto", "marca", "modelo",
                            "color", "material", "peso", "dimensiones", "garantia", "tipo_envio", "etiquetas"]
    for campo in campos_obligatorios:
        if not str(datos.get(campo) or "").strip():
            errores.append(f"...'{campo.replace('_', ' ')}'.")
    if datos.get("stock") is None or datos.get("stock") < 1:
        errores.append(idiomas.t("paso_ia_stock_invalido"))
    return errores


def validar_precio(datos):
    errores = []
    if not datos.get("precio") or datos["precio"] <= 0:
        errores.append(idiomas.t("paso_precio_ingresa_valido"))
    if datos.get("tiene_oferta") and (not datos.get("precio_oferta") or datos["precio_oferta"] <= 0 or datos["precio_oferta"] >= datos.get("precio", 0)):
        errores.append(idiomas.t("paso_precio_oferta_menor"))
    return errores