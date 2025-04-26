# Urban Routes – Proyecto de Automatización Sprint8 (QA)

Este repositorio contiene una prueba automática  para la aplicación web **Urban Routes**, desarrollada como parte del Sprint 8 del Bootcamp de QA de TripleTen. El objetivo es demostrar que, en un único flujo, un usuario puede solicitar un taxi, realizar el pago y añadir extras sin errores.


Pruebas realizadas

- Selección de origen y destino
- Selección de tarifa Comfort
- Ingreso y validación del número de teléfono
- Registro de una tarjeta de crédito
- Envío de un mensaje al conductor
- Solicitud de manta, pañuelos y 2 helados
- Confirmación de solicitud de taxi

## Requisitos

- **Python 3.10 o superior** – Lenguaje principal  
- **Selenium 4.x** – WebDriver para Google Chrome  
- **pytest 8.x** – Ejecución de pruebas

> **Nota sobre la inicialización del driver**  
> La plantilla original fue escrita para una versión anterior de Selenium.  
> A partir de Selenium 4 el parámetro `desired_capabilities` está obsoleto; por ello el driver se crea así:
> ```python
> opts = Options()
> opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
> driver = webdriver.Chrome(options=opts)
> No se modificó ninguna otra parte lógica del flujo.

## Instalación y ejecución

```bash
# 1) Clonar el repositorio
git clone git@github.com:DavidHunter94/qa-project-Urban-Routes-es.git
$ cd qa-project-Urban-Routes-es

# 2) Crear un entorno virtual e instalar dependencias
$ python -m venv venv
$ venv\Scripts\activate 
$ pip install -r requirements.txt

# 3) Ejecutar la prueba
$ pytest -q main.py
```

Al finalizar la prueba aparece algo asi

1 passed

## Estructura del proyecto

- **data.py** – Datos fijos de la prueba: direcciones, teléfono, tarjeta y mensaje.
- **main.py** – Page Object Model + caso de prueba con `pytest`.
- **requirements.txt** – Dependencias mínimas (`selenium`, `pytest`).
- **.gitignore** – Archivos y carpetas que no deben subirse al repo (por ejemplo `venv/`).
- **README.md** – Este documento.


*Cualquier sugerencia es bienvenida; sigo mejorando mis habilidades de automatización.*

