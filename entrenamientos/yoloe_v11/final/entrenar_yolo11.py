from ultralytics import YOLOE
from ultralytics.models.yolo.yoloe import YOLOEPETrainer

model = YOLOE("yoloe-11s.yaml")
model.load("yoloe-11s-seg.pt")

results = model.train(
    data=r"C:\Users\pacem\Desktop\BIO_BOT\datasets\dataset_final_aumentado\data.yaml",
    epochs=30,
    patience=10,
    imgsz=320,
    batch=8,
    device="cpu",
    workers=4,
    save_period=5,
    project="runs",
    name="final_v11",
    trainer=YOLOEPETrainer,
)

print("\n✅ Entrenamiento YOLOE-11s (dataset final aumentado) terminado.")