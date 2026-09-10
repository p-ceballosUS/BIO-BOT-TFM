"""Prueba básica del NeoPixel conectado al GPIO18 de la Raspberry Pi 4."""

import time

import board
import neopixel


NUMERO_DE_PIXELES = 16
PIN_NEOPIXEL = board.D18
BRILLO = 0.3
TIEMPO_POR_COLOR = 2

COLORES_PRUEBA = [
    ("Rojo", (255, 0, 0)),
    ("Verde", (0, 255, 0)),
    ("Azul", (0, 0, 255)),
    ("Amarillo", (255, 255, 0)),
    ("Apagado", (0, 0, 0)),
]


def main():
    print("Inicializando NeoPixel en GPIO18...")
    pixels = neopixel.NeoPixel(
        PIN_NEOPIXEL,
        NUMERO_DE_PIXELES,
        brightness=BRILLO,
        auto_write=True,
    )

    try:
        print(
            "El NeoPixel cambiara de color "
            f"cada {TIEMPO_POR_COLOR} segundos.\n"
        )

        for nombre, color in COLORES_PRUEBA:
            print(f"Mostrando: {nombre} {color}")
            pixels.fill(color)
            time.sleep(TIEMPO_POR_COLOR)
    finally:
        pixels.fill((0, 0, 0))

    print("Prueba finalizada.")


if __name__ == "__main__":
    main()
