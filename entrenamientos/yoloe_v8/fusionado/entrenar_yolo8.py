from ultralytics import YOLOE
from ultralytics.models.yolo.yoloe import YOLOEPETrainer

model = YOLOE("yoloe-v8s.yaml")
model.load("yoloe-v8s-seg.pt")

results = model.train(
    data=r"C:\Users\pacem\Desktop\BIO_BOT\datasets\dataset_fusionado\data.yaml",
    epochs=30,
    patience=10,
    imgsz=320,
    batch=8,
    device="cpu",
    workers=4,
    save_period=5,
    project="runs_completo",
    name="full_run",
    trainer=YOLOEPETrainer,
)

print("\n✅ Entrenamiento completo terminado.")
print("Resultados guardados en la carpeta: runs_completo/full_run")