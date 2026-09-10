"""Permite determina el contenedor de destino y el color RGB que debe mostrar el NeoPixel."""

FINAL_CLASSES = [
    "Carton",
    "Papel",
    "Vidrio",
    "Metal",
    "Plastico",
    "Organico",
    "Ordinario",
]

CLASE_A_CONTENEDOR = {
    "Carton": "Azul",
    "Papel": "Azul",
    "Vidrio": "Verde",
    "Metal": "Amarillo",
    "Plastico": "Amarillo",
    "Organico": "Ordinario",
    "Ordinario": "Ordinario",
}

CONTENEDOR_A_COLOR_RGB = {
    "Azul": (0, 80, 200),
    "Verde": (0, 150, 40),
    "Amarillo": (255, 180, 0),
    "Ordinario": (128, 128, 128),
}


def determinar_contenedor(nombre_clase):
    """Devuelve el contenedor asociado a una clase detectada."""
    if nombre_clase not in CLASE_A_CONTENEDOR:
        clases_validas = list(CLASE_A_CONTENEDOR.keys())
        raise ValueError(
            f"Clase no reconocida: '{nombre_clase}'. "
            f"Clases validas: {clases_validas}"
        )
    return CLASE_A_CONTENEDOR[nombre_clase]


def determinar_color(nombre_clase):
    """Devuelve el color RGB asociado al contenedor de la clase detectada."""
    contenedor = determinar_contenedor(nombre_clase)
    return CONTENEDOR_A_COLOR_RGB[contenedor]


def elegir_deteccion_prioritaria(detecciones):
    """Selecciona la detección con mayor confianza."""
    if not detecciones:
        return None
    return max(detecciones, key=lambda deteccion: deteccion[1])


if __name__ == "__main__":
    print("Mapeo de clase -> contenedor -> color:\n")
    for clase in FINAL_CLASSES:
        contenedor = determinar_contenedor(clase)
        color = determinar_color(clase)
        print(f"  {clase:12s} -> {contenedor:10s} -> RGB{color}")

    ejemplo = [("Carton", 0.62), ("Organico", 0.81), ("Vidrio", 0.45)]
    elegido = elegir_deteccion_prioritaria(ejemplo)

    print("\nPrueba de seleccion por confianza:")
    print(f"  Detecciones: {ejemplo}")
    print(
        f"  Elegida: {elegido} -> "
        f"contenedor: {determinar_contenedor(elegido[0])}"
    )
