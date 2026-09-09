"""
entrenar_yolo11_final_v2.py

Entrena YOLOE (base YOLO11s) sobre el conjunto de datos final_v2, es decir,
el conjunto balanceado y aumentado con la correccion de conversion de
poligonos a cajas delimitadoras aplicada. Misma configuracion de
hiperparametros que las cuatro configuraciones originales, para que la
comparacion siga siendo valida.
"""
from ultralytics import YOLOE
from ultralytics.models.yolo.yoloe import YOLOEPETrainer

model = YOLOE("yoloe-11s.yaml")
model.load("yoloe-11s-seg.pt")

model.train(
    data=r"C:\Users\pacem\Desktop\BIO_BOT\datasets\dataset_final_aumentado_v2\data.yaml",
    epochs=30,
    patience=10,
    imgsz=320,
    batch=8,
    device="cpu",
    workers=4,
    save_period=5,
    project="runs",
    name="final_v2_v11",
    trainer=YOLOEPETrainer,
)