# BIO-BOT

Sistema de detección y clasificación de residuos sólidos mediante YOLOE, desarrollado como Trabajo de Fin de Máster (TFM)

El proyecto abarcó todo el proceso, desde la recopilación y preparación de un conjunto de datos propio y de fuentes públicas, pasando por el entrenamiento y evaluación comparativa de seis configuraciones, hasta el despliegue del sistema resultante sobre distintos equipos de ejecución (un de desarrollo convencional y dos generaciones de Raspberry Pi).

El resultado final permite identificar residuos en tiempo real mediante una cámara y señalizar el contenedor correspondiente a través de un indicador luminoso NeoPixel, de acuerdo con el código de colores de reciclaje empleado en España.

## Estructura del repositorio

| Carpeta | Contenido |
| --- | --- |
| dataset_propio_remapeado/ | Conjunto de datos propio, capturado en campo en distintas ciudades de Colombia, ya etiquetado manualmente y remapeado al esquema común de siete categorías empleado en el proyecto (Cartón, Papel, Vidrio, Metal, Plástico, Orgánico, Ordinario). |
| entrenamientos/ | Resultados de las seis configuraciones de modelo entrenadas (combinación de las variantes YOLOv8 y YOLO11 con tres versiones del conjunto de datos), incluyendo métricas, gráficas de evaluación, y los pesos finales de cada modelo. |
| despliegue/ | Scripts necesarios para ejecutar el modelo seleccionado sobre un equipo de desarrollo o una Raspberry Pi 4 y 5, junto con una guía paso a paso para replicar el despliegue. |

## Configuraciones de entrenamiento

Durante el proceso se entrenaron seis configuraciones distintas, resultado de combinar dos variantes arquitectónicas de YOLOE (basadas en YOLOv8 y YOLO11) con tres versiones del conjunto de datos, con el propósito de aislar el efecto de la arquitectura, del balanceo de clases, y del tratamiento de un subconjunto de anotaciones heredadas en formato de polígono de los datasets públicos.

| Configuración | Variante arquitectónica | Conjunto de datos |
| --- | --- | --- |
| v8_fusionado | YOLOE (YOLOv8) | Fusionado, sin balancear (11.963 imágenes) |
| v11_fusionado | YOLOE (YOLO11) | Fusionado, sin balancear (11.963 imágenes) |
| v8_final | YOLOE (YOLOv8) | Final, balanceado (23.303 imágenes) |
| v11_final | YOLOE (YOLO11) | Final, balanceado (23.303 imágenes) |
| v8_final_v2 | YOLOE (YOLOv8) | Final, balanceado, con tratamiento de polígonos (21.255 imágenes) |
| v11_final_v2 | YOLOE (YOLO11) | Final, balanceado, con tratamiento de polígonos (21.255 imágenes) |

## Modelo seleccionado

Entre las seis configuraciones evaluadas, v11 + final (YOLO11, entrenado sobre el conjunto de datos balanceado) resultó seleccionada como configuración definitiva, por obtener el mAP50 global más alto, el mayor F1-Score, y una velocidad de inferencia favorable frente a las demás configuraciones.

Sus pesos se encuentran disponibles en `entrenamientos/yoloe_v11/final/runs/detect/runs/final_v11/weights/best.pt`, y una copia adicional en `despliegue/best.pt` para facilitar su uso directo.

## Despliegue

Para desplegar el sistema ya entrenado, sin necesidad de reproducir el proceso completo de recolección de datos ni entrenamiento, dirigirse a la carpeta `despliegue/` y seguir las instrucciones de su README, disponibles tanto para un equipo de desarrollo convencional como para una Raspberry Pi.
