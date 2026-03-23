# Urban Routes – Automatización QA con Selenium

Proyecto de automatización de pruebas UI para la aplicación web **Urban Routes**, desarrollado como parte del Sprint 8 del Bootcamp de QA de TripleTen.

Valida que en un flujo completo el usuario pueda solicitar un taxi, registrar su teléfono, agregar método de pago y solicitar extras — todo sin errores.

---

## 🧪 Cobertura de pruebas

- Selección de origen y destino
- Selección de tarifa (Comfort)
- Ingreso y validación del número de teléfono
- Registro de una tarjeta de crédito
- Envío de mensaje al conductor
- Solicitud de manta y pañuelos
- Solicitud de 2 helados
- Confirmación de solicitud de taxi

---

## ⚙️ Tecnologías utilizadas

- **Lenguaje:** Python 3.10+
- **Framework de pruebas:** pytest
- **Automatización:** Selenium 4.x + ChromeDriver
- **Patrón de diseño:** Page Object Model (POM)

---

## 🏗️ Estructura del proyecto

```
project/
│
├── main.py          ← Page Object Model + caso de prueba
├── data.py          ← Datos fijos: direcciones, teléfono, tarjeta, mensaje
├── requirements.txt ← Dependencias
└── README.md
```

---

## ▶️ Instalación y ejecución local

```bash
# 1. Clonar el repositorio
git clone https://github.com/DavidHunter94/qa-project-Urban-Routes-es.git
cd qa-project-Urban-Routes-es

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 3. Ejecutar la prueba
pytest -q main.py
```

Al finalizar verás:

```
1 passed
```

> ⚠️ Los tests requieren que el servidor de Urban Routes esté activo.
> Esta URL es temporal del entorno de TripleTen y puede estar inactiva
> una vez finalizado el sprint.

---

## 🔍 Detalles de implementación

- Migración de `desired_capabilities` (obsoleto) a `Options()` de Selenium 4
- Captura del código de verificación telefónica mediante respuesta del backend
- Separación de datos de prueba en `data.py`
- Un único flujo E2E que encadena todos los pasos sin errores

---

## ⚖️ Selenium vs Playwright

Este mismo proyecto fue reimplementado con Playwright para comparar enfoques.

| | Selenium | Playwright |
|---|---|---|
| Esperas | Manuales (explicit waits) | Automáticas (auto-waiting) |
| Cantidad de código | Mayor | Más limpio y conciso |
| Estabilidad | Más flaky | Mayor estabilidad |
| Soporte CI/CD | Requiere más config | Nativo con headless |

Puedes ver la versión con Playwright aquí: [qa-automation-playwright](https://github.com/DavidHunter94/qa-automation-playwright)

---

## 🚀 Autor

**Victor David Martínez Matías**
QA Engineer con experiencia en pruebas manuales, automatización UI y pruebas de API.
