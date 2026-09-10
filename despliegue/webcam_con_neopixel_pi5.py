"""Integración de BIO-BOT para Raspberry Pi 5"""

import time
from pathlib import Path

import board
import cv2
import neopixel
from ultralytics import YOLOE

from determinar_contenedor import (
    determinar_color,
    determinar_contenedor,
    elegir_deteccion_prioritaria,
)


BASE_DIR = Path(__file__).resolve().parent

MODELO_PATH = BASE_DIR / "best.pt"
LOG_PATH = BASE_DIR / "log_velocidad_raspberry.txt"

CONF_MINIMA = 0.346
CAMARA_INDICE = 0

NUMERO_DE_PIXELES = 16
PIN_NEOPIXEL = board.D24
BRILLO_NEOPIXEL = 0.3
TIEMPO_APAGADO_SIN_DETECCION = 3.0
ANCHO_RECUADRO_COLOR = 60

FINAL_CLASSES = [
    "Carton",
    "Papel",
    "Vidrio",
    "Metal",
    "Plastico",
    "Organico",
    "Ordinario",
]


def obtener_detecciones(resultado):
    """Convierte las cajas del modelo en pares (clase, confianza)."""
    detecciones = []

    if resultado.boxes is None:
        return detecciones

    for box in resultado.boxes:
        cls_id = int(box.cls[0])
        confianza = float(box.conf[0])

        if cls_id < len(FINAL_CLASSES):
            nombre_clase = FINAL_CLASSES[cls_id]
        else:
            nombre_clase = f"clase_{cls_id}"

        detecciones.append((nombre_clase, confianza))

    return detecciones


def ajustar_escala_texto(texto, ancho_disponible):
    """Reduce la escala del texto hasta que encaje en la imagen."""
    escala = 0.8
    (ancho_texto, _), _ = cv2.getTextSize(
        texto,
        cv2.FONT_HERSHEY_SIMPLEX,
        escala,
        2,
    )

    while ancho_texto > ancho_disponible and escala > 0.35:
        escala -= 0.05
        (ancho_texto, _), _ = cv2.getTextSize(
            texto,
            cv2.FONT_HERSHEY_SIMPLEX,
            escala,
            2,
        )

    return escala


def guardar_resumen_fps(fps_registrados):
    """Añade al log un resumen de rendimiento de la ejecución."""
    if not fps_registrados:
        print("No se registro ningun fotograma; no se genero resumen.")
        return

    promedio = sum(fps_registrados) / len(fps_registrados)
    minimo = min(fps_registrados)
    maximo = max(fps_registrados)
    ms_promedio = 1000 / promedio

    resumen = (
        f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        "Entorno: Raspberry Pi 5 "
        "(camara + deteccion + decision + NeoPixel)\n"
        f"Fotogramas procesados: {len(fps_registrados)}\n"
        f"FPS promedio: {promedio:.2f}\n"
        f"FPS minimo: {minimo:.2f}\n"
        f"FPS maximo: {maximo:.2f}\n"
        f"Tiempo promedio por fotograma: {ms_promedio:.1f} ms\n"
        f"{'-' * 50}\n"
    )

    with LOG_PATH.open("a", encoding="utf-8") as archivo:
        archivo.write(resumen)

    print(f"\n{resumen}")
    print(f"Resumen guardado en: {LOG_PATH}")


def main():
    if not MODELO_PATH.exists():
        raise SystemExit(f"No se encontro el modelo: {MODELO_PATH}")

    print(f"Cargando modelo: {MODELO_PATH}")
    model = YOLOE(str(MODELO_PATH))

    print(
        f"Inicializando NeoPixel en GPIO18 "
        f"({NUMERO_DE_PIXELES} LEDs)..."
    )
    pixels = neopixel.NeoPixel(
        PIN_NEOPIXEL,
        NUMERO_DE_PIXELES,
        brightness=BRILLO_NEOPIXEL,
        auto_write=True,
    )
    pixels.fill((0, 0, 0))

    print("Abriendo camara...")
    cap = cv2.VideoCapture(CAMARA_INDICE)
    if not cap.isOpened():
        pixels.fill((0, 0, 0))
        raise SystemExit(
            f"No se pudo abrir la camara con indice {CAMARA_INDICE}."
        )

    print("Camara abierta. Presiona 'q' o Ctrl+C para detener.\n")

    tiempo_anterior = time.perf_counter()
    tiempo_ultima_deteccion = None
    color_actual_neopixel = (0, 0, 0)
    fps_registrados = []

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("No se pudo leer un fotograma. Deteniendo.")
                break

            resultados = model.predict(
                frame,
                conf=CONF_MINIMA,
                verbose=False,
            )
            resultado = resultados[0]
            frame_anotado = resultado.plot()

            detecciones = obtener_detecciones(resultado)
            elegida = elegir_deteccion_prioritaria(detecciones)

            tiempo_actual = time.perf_counter()
            delta = tiempo_actual - tiempo_anterior
            tiempo_anterior = tiempo_actual

            if delta > 0:
                fps = 1 / delta
                fps_registrados.append(fps)
                cv2.putText(
                    frame_anotado,
                    f"FPS: {fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

            alto, ancho = frame_anotado.shape[:2]
            cv2.rectangle(
                frame_anotado,
                (0, alto - 50),
                (ancho, alto),
                (0, 0, 0),
                -1,
            )

            if elegida is not None:
                nombre_clase, confianza = elegida
                contenedor = determinar_contenedor(nombre_clase)
                color_rgb = determinar_color(nombre_clase)

                if color_rgb != color_actual_neopixel:
                    pixels.fill(color_rgb)
                    color_actual_neopixel = color_rgb

                tiempo_ultima_deteccion = tiempo_actual

                color_bgr = (
                    color_rgb[2],
                    color_rgb[1],
                    color_rgb[0],
                )
                texto = (
                    f"Contenedor: {contenedor} "
                    f"({nombre_clase} {confianza:.2f})"
                )
                ancho_disponible = ancho - ANCHO_RECUADRO_COLOR - 20
                escala = ajustar_escala_texto(
                    texto,
                    ancho_disponible,
                )

                cv2.putText(
                    frame_anotado,
                    texto,
                    (10, alto - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    escala,
                    (255, 255, 255),
                    2,
                )
                cv2.rectangle(
                    frame_anotado,
                    (ancho - ANCHO_RECUADRO_COLOR - 10, alto - 50),
                    (ancho - 10, alto - 10),
                    color_bgr,
                    -1,
                )
            else:
                cv2.putText(
                    frame_anotado,
                    "Sin deteccion",
                    (10, alto - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (200, 200, 200),
                    2,
                )

                if (
                    tiempo_ultima_deteccion is not None
                    and tiempo_actual - tiempo_ultima_deteccion
                    > TIEMPO_APAGADO_SIN_DETECCION
                    and color_actual_neopixel != (0, 0, 0)
                ):
                    pixels.fill((0, 0, 0))
                    color_actual_neopixel = (0, 0, 0)

            cv2.imshow(
                "BIO-BOT - Deteccion + NeoPixel",
                frame_anotado,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Detenido manualmente.")
                break

    except KeyboardInterrupt:
        print("\nDetenido con Ctrl+C.")
    finally:
        pixels.fill((0, 0, 0))
        cap.release()
        cv2.destroyAllWindows()
        guardar_resumen_fps(fps_registrados)

    print("Programa finalizado. NeoPixel apagado.")


if __name__ == "__main__":
    main()
