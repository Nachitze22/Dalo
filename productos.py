MAPEO_CATEGORIAS = {
    "carteras": ["bag", "purse", "handbag"],
    "mochilas": ["backpack", "bulletproof vest"],
    "remeras": ["jersey", "t-shirt", "shirt"],
    "pantalones": ["jean", "trouser"],
    "camisas": ["shirt", "suit"]}
def detectar_categoria_texto(nombre_archivo):
    nombre = nombre_archivo.lower()
    if "cartera" in nombre:
        return "carteras"
    elif "mochila" in nombre:
        return "mochilas"
    elif "remera" in nombre:
        return "remeras"
    elif "pantalon" in nombre or "jean" in nombre:
        return "pantalones"
    elif "camisa" in nombre:
        return "camisas"
    return None