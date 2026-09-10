"""Evaluación cualitativa del modelo seleccionado."""

import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLOE


BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent

MODELO_PATH = BASE_DIR / "best.pt"
INPUT_DIR = REPO_DIR / "datasets" / "externos" / "prueba_cualitativa_futura"
OUTPUT_DIR = REPO_DIR / "datasets" / "prueba_cualitativa_resultados"

N_MUESTRAS_POR_CARPETA = 8
CONF_MINIMA = 0.346
SEMILLA_ALEATORIA = 3

FINAL_CLASSES = [
    "Carton",
    "Papel",
    "Vidrio",
    "Metal",
    "Plastico",
    "Organico",
    "Ordinario",
]

COLORES = {
    "Carton": (139, 90, 43),
    "Papel": (52, 120, 246),
    "Vidrio": (46, 204, 113),
    "Metal": (149, 165, 166),
    "Plastico": (241, 196, 15),
    "Organico": (39, 87, 24),
    "Ordinario": (30, 30, 30),
}

EXTENSIONES_VALIDAS = (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG")


def agrupar_imagenes_por_carpeta(base_dir):
    """Agrupa las imágenes encontradas por su carpeta de origen."""
    grupos = {}

    for root, _, nombres_archivo in os.walk(base_dir):
        imagenes = [
            nombre
            for nombre in nombres_archivo
            if nombre.endswith(EXTENSIONES_VALIDAS)
        ]
        if imagenes:
            grupos[Path(root)] = imagenes

    return grupos


def cargar_fuente():
    """Carga una fuente disponible para dibujar las etiquetas."""
    try:
        return ImageFont.truetype("arial.ttf", 16)
    except OSError:
        return ImageFont.load_default()


def main():
    random.seed(SEMILLA_ALEATORIA)

    if not MODELO_PATH.exists():
        raise SystemExit(f"No se encontro el modelo: {MODELO_PATH}")

    if not INPUT_DIR.exists():
        raise SystemExit(f"No se encontro el directorio de entrada: {INPUT_DIR}")

    print("Buscando imagenes en los conjuntos cualitativos...")
    grupos = agrupar_imagenes_por_carpeta(INPUT_DIR)

    total_imagenes = sum(len(imagenes) for imagenes in grupos.values())
    print(
        f"Se encontraron {len(grupos)} carpetas con imagenes, "
        f"con un total de {total_imagenes} imagenes."
    )

    if not grupos:
        raise SystemExit(
            f"No se encontraron imagenes dentro de {INPUT_DIR}."
        )

    muestra_total = []
    for carpeta, imagenes in grupos.items():
        seleccionadas = random.sample(
            imagenes,
            min(N_MUESTRAS_POR_CARPETA, len(imagenes)),
        )
        muestra_total.extend((carpeta, nombre) for nombre in seleccionadas)

    print(
        f"Se seleccionaron {len(muestra_total)} imagenes "
        f"(hasta {N_MUESTRAS_POR_CARPETA} por carpeta)."
    )

    print(f"Cargando modelo desde: {MODELO_PATH}")
    model = YOLOE(str(MODELO_PATH))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fuente = cargar_fuente()
    sin_detecciones = 0

    print("Ejecutando detecciones...")
    for indice, (carpeta, nombre_img) in enumerate(muestra_total, start=1):
        ruta_img = carpeta / nombre_img
        resultados = model.predict(
            str(ruta_img),
            conf=CONF_MINIMA,
            verbose=False,
        )
        resultado = resultados[0]

        imagen = Image.open(ruta_img).convert("RGB")
        draw = ImageDraw.Draw(imagen)

        cajas = resultado.boxes
        if cajas is None or len(cajas) == 0:
            sin_detecciones += 1
        else:
            for box in cajas:
                cls_id = int(box.cls[0])
                confianza = float(box.conf[0])

                if cls_id < len(FINAL_CLASSES):
                    nombre_clase = FINAL_CLASSES[cls_id]
                else:
                    nombre_clase = f"clase_{cls_id}"

                color = COLORES.get(nombre_clase, (255, 0, 255))
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                etiqueta = f"{nombre_clase} {confianza:.2f}"
                draw.text(
                    (x1 + 2, max(y1 - 18, 0)),
                    etiqueta,
                    fill=color,
                    font=fuente,
                )

        """Mantiene la subcarpeta de origen para facilitar la revisión"""
        destino_dir = OUTPUT_DIR / carpeta.name
        destino_dir.mkdir(parents=True, exist_ok=True)
        imagen.save(destino_dir / nombre_img)

        if indice % 10 == 0 or indice == len(muestra_total):
            print(f"Procesadas {indice}/{len(muestra_total)} imagenes.")

    print(f"Resultados guardados en: {OUTPUT_DIR}")
    print(
        "Imagenes sin detecciones por encima de "
        f"{CONF_MINIMA}: {sin_detecciones} de {len(muestra_total)}"
    )


if __name__ == "__main__":
    main()
