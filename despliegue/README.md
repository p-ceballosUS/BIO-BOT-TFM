# BIO-BOT --- Despliegue

Este directorio contiene todo lo necesario para ejecutar el modelo ya
entrenado del proyecto, sin necesidad de reproducir el proceso completo
de recolección de datos ni de entrenamiento.

Para consultar el proceso completo, ver `entrenamientos/` y
`dataset_propio_remapeado/` en la raíz del repositorio.

Repositorio completo: <https://github.com/p-ceballosUS/BIO-BOT-TFM>

## Contenido de esta carpeta

  -----------------------------------------------------------------------
  Archivo                             Qué hace
  ----------------------------------- -----------------------------------
  `determinar_contenedor.py`          Traduce la clase detectada al
                                      contenedor de disposición
                                      correspondiente.

  `webcam_con_contenedor.py`          Ejecuta el sistema en PC: cámara,
                                      detección y decisión de contenedor
                                      en pantalla, sin NeoPixel físico.

  `webcam_con_neopixel.py`            Ejecuta el sistema completo en
                                      Raspberry Pi 4, incluyendo el
                                      control del NeoPixel.

  `webcam_con_neopixel_pi5.py`        Ejecuta el sistema completo en
                                      Raspberry Pi 5, incluyendo el
                                      control del NeoPixel.

  `probar_neopixel.py`                Prueba aislada del NeoPixel, sin
                                      cámara ni modelo.

  `probar_cualitativo.py`             Ejecuta el modelo sobre fotografías
                                      fijas para una verificación
                                      cualitativa.

  `best.pt`                           Pesos del modelo seleccionado,
                                      correspondiente a la configuración
                                      v11 + final.
  -----------------------------------------------------------------------

El modelo también se encuentra en:

``` text
entrenamientos/yoloe_v11/final/runs/detect/runs/final_v11/weights/best.pt
```

## Requisitos previos

-   Python 3.11 o superior.
-   Cámara web integrada o USB, o cámara compatible con Raspberry Pi.
-   Para Raspberry Pi: NeoPixel WS2812.
-   Monitor HDMI si se desea visualizar localmente la ventana de
    detección.

## Despliegue en PC

### Crear y activar el entorno virtual

``` bash
python -m venv venv
```

Windows:

``` powershell
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

``` bash
source venv/bin/activate
```

### Instalar dependencias

``` bash
pip install ultralytics opencv-python
```

### Colocar el modelo

`best.pt` debe encontrarse en la misma carpeta que los scripts de
despliegue.

### Ejecutar

``` bash
python webcam_con_contenedor.py
```

Se abrirá una ventana con el vídeo en vivo. Cada residuo detectado se
marcará con una caja y se mostrará el contenedor correspondiente junto
con su color asociado. El programa se cierra presionando `q`.

## Despliegue en Raspberry Pi 4 o Raspberry Pi 5

### Preparar la tarjeta SD

Se recomienda preparar la tarjeta con Raspberry Pi Imager y configurar
previamente usuario, contraseña, Wi-Fi y SSH desde las opciones
avanzadas. Si no es posible, la configuración inicial puede realizarse
localmente mediante HDMI, teclado y ratón, o utilizando Ethernet para
obtener conectividad y acceder posteriormente mediante SSH.

### Conectarse por SSH

``` bash
ssh usuario@direccion_ip_de_la_raspberry_pi
```

### Crear el entorno virtual e instalar PyTorch para CPU

``` bash
python3 -m venv ~/despliegue/.venv
source ~/despliegue/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install wheel setuptools
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

El parámetro `--index-url` evita instalar dependencias CUDA innecesarias
para la Raspberry Pi.

### Instalar el resto de dependencias

``` bash
python -m pip install ultralytics opencv-python adafruit-circuitpython-neopixel rpi_ws281x
```

Si aparecen errores relacionados con `swig` o `lgpio`:

``` bash
sudo apt update
sudo apt install swig liblgpio-dev -y
python -m pip install adafruit-circuitpython-neopixel rpi_ws281x
```

### Transferir los archivos

Raspberry Pi 4:

``` bash
scp despliegue/determinar_contenedor.py despliegue/webcam_con_neopixel.py despliegue/probar_neopixel.py despliegue/best.pt usuario@direccion_ip:~/despliegue/
```

Raspberry Pi 5:

``` bash
scp despliegue/determinar_contenedor.py despliegue/webcam_con_neopixel_pi5.py despliegue/probar_neopixel.py despliegue/best.pt usuario@direccion_ip:~/despliegue/
```

### Conectar el NeoPixel

  Equipo           Pin GPIO   ¿Requiere `sudo`?
  ---------------- ---------- --------------------------------
  Raspberry Pi 4   GPIO18     Sí
  Raspberry Pi 5   GPIO24     No, en la mayoría de los casos

### Probar el NeoPixel

Raspberry Pi 5:

``` bash
python probar_neopixel.py
```

Raspberry Pi 4:

``` bash
sudo .venv/bin/python probar_neopixel.py
```

Los LEDs deberían cambiar entre rojo, verde, azul, amarillo y apagado.

### Ejecutar el sistema completo

Raspberry Pi 5:

``` bash
DISPLAY=:0 .venv/bin/python webcam_con_neopixel_pi5.py
```

Raspberry Pi 4:

``` bash
sudo DISPLAY=:0 .venv/bin/python webcam_con_neopixel.py
```

`DISPLAY=:0` permite mostrar la ventana en el monitor conectado
físicamente a la Raspberry Pi cuando el programa se inicia desde SSH. El
programa puede detenerse con `Ctrl+C` o presionando `q` desde un teclado
conectado al equipo.

## Código de colores empleado

  Categoría detectada   Contenedor         Color
  --------------------- ------------------ ----------------------
  Cartón, Papel         Azul               `RGB(0, 80, 200)`
  Vidrio                Verde              `RGB(0, 150, 40)`
  Metal, Plástico       Amarillo           `RGB(255, 180, 0)`
  Orgánico, Ordinario   Ordinario (gris)   `RGB(128, 128, 128)`

Cartón/Papel y Metal/Plástico comparten contenedor. Orgánico se agrupa
con Ordinario a partir de los resultados de evaluación del modelo, donde
fue la categoría con el desempeño menos confiable.

El umbral de confianza indicado para el modelo seleccionado es `0.346`.

## Problemas comunes

**`Could not connect to display` o error Qt/xcb:** anteponer
`DISPLAY=:0` cuando la ventana deba mostrarse en el monitor conectado a
la Raspberry Pi.

**`NeoPixel support requires running with sudo`:** en Raspberry Pi 4,
ejecutar el script con `sudo`.

**`Gpio X is illegal for LED channel 0`:** comprobar que el pin
configurado en el script coincide con la conexión física del NeoPixel.

**Error con `swig` o `lgpio`:**

``` bash
sudo apt install swig liblgpio-dev -y
```

**Conflicto de OpenCV en Windows:**

``` bash
pip uninstall opencv-python-headless -y
pip install --force-reinstall opencv-python
```

## Créditos

Proyecto desarrollado como Trabajo de Fin de Máster (TFM):

**BIO-BOT: Desarrollo y evaluación de modelo de detección y
clasificación de residuos sólidos por medio de sistema de visión
artificial.**
