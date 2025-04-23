import json
import time
import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

# ——— Helper para capturar el código de confirmación vía CDP logs ———
def retrieve_phone_code(driver: webdriver.Chrome, attempts: int = 10) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código solo se puede obtener después de haberlo solicitado en la aplicación."""
    for _ in range(attempts):
        try:
            logs = driver.get_log("performance")
            msgs = [e["message"] for e in logs if isinstance(e.get("message"), str) and "api/v1/number?number" in e["message"]]
            for raw in reversed(msgs):
                parsed = json.loads(raw)["message"]
                req_id = parsed["params"]["requestId"]
                body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": req_id})
                digits = "".join(filter(str.isdigit, body.get("body", "")))
                if digits:
                    return digits
        except (ValueError, WebDriverException):
            time.sleep(1)
    raise TimeoutException(f"No se encontró el código tras {attempts} intentos.")


class UrbanRoutesPage:
    # ——— Localizadores ———
    from_field         = (By.ID, "from")
    to_field           = (By.ID, "to")
    boton_taxi         = (By.XPATH, "//button[text()='Pedir un taxi']")
    tarjeta_comfort    = (By.XPATH, "//div[contains(@class,'tcard') and .//div[text()='Comfort']]")

    btn_phone          = (By.CSS_SELECTOR, ".np-button")
    phone_input        = (By.ID, "phone")
    phone_next_button  = (By.CSS_SELECTOR, "button[type='submit']")
    phone_code_input   = (By.ID, "code")
    close_button       = (By.CSS_SELECTOR, ".input-close-button")

    boton_pago         = (By.CSS_SELECTOR, ".pp-button.filled")
    fila_add_tarjeta   = (By.XPATH, "//div[contains(@class,'pp-row') and .//div[text()='Agregar tarjeta']]")
    credit_card_number = (By.ID, "number")
    credit_card_code   = (By.XPATH, "//div[@class='card-code-input']//input")
    add_card_button    = (By.XPATH, "//div[@class='pp-buttons']/button[normalize-space()='Agregar']")
    payment_section_close = (By.CSS_SELECTOR, ".close-button.section-close")

    blanket_switch = (By.XPATH, "//div[text()='Manta y pañuelos']/following-sibling::div//input[@type='checkbox']")
    plus_helado    = (By.XPATH, "//div[text()='Helado']/following-sibling::div//div[contains(@class,'counter-plus')]")

    message_field = (By.ID, "comment")

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # ——— Métodos para ruta ———
    def set_from(self, addr: str) -> None:
        origen = self.wait.until(EC.element_to_be_clickable(self.from_field))
        origen.clear(); origen.send_keys(addr)

    def set_to(self, addr: str) -> None:
        destino = self.wait.until(EC.element_to_be_clickable(self.to_field))
        destino.clear(); destino.send_keys(addr)

    def set_route(self, addr_from: str, addr_to: str) -> None:
        """Pequeño helper para rellenar origen y destino."""
        self.set_from(addr_from)
        self.set_to(addr_to)

    def get_from(self) -> str:
        return self.driver.find_element(*self.from_field).get_property("value")

    def get_to(self) -> str:
        return self.driver.find_element(*self.to_field).get_property("value")

    # ——— Pedir taxi y tarifa ———
    def click_taxi_button(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.boton_taxi)).click()

    def select_comfort_tariff(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.tarjeta_comfort)).click()

    # ——— Formulario de teléfono ———
    def fill_phone_and_verify(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.btn_phone)).click()
        self.wait.until(EC.element_to_be_clickable(self.phone_input)).send_keys(data.phone_number)
        self.wait.until(EC.element_to_be_clickable(self.phone_next_button)).click()

        code = retrieve_phone_code(self.driver)
        self.wait.until(EC.element_to_be_clickable(self.phone_code_input)).send_keys(code + Keys.ENTER)
        try:
            self.wait.until(EC.element_to_be_clickable(self.close_button)).click()
        except TimeoutException:
            pass

    # ——— Métodos de pago ———
    def fill_credit_card(self) -> None:
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".section.active")))
        self.wait.until(EC.element_to_be_clickable(self.boton_pago)).click()

        self.wait.until(EC.element_to_be_clickable(self.fila_add_tarjeta)).click()
        self.wait.until(EC.element_to_be_clickable(self.credit_card_number)).send_keys(data.card_number)
        cvv = self.wait.until(EC.element_to_be_clickable(self.credit_card_code))
        cvv.send_keys(data.card_code + Keys.TAB)
        self.wait.until(EC.element_to_be_clickable(self.add_card_button)).click()

        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".section.active")))

    # ——— Extras ———
    def request_blanket_and_tissues(self, enable: bool = True) -> None:
        try:
            switch = self.wait.until(EC.presence_of_element_located(self.blanket_switch))
            if switch.is_selected() is not enable:
                try:
                    switch.click()
                except Exception:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", switch)
                    self.driver.execute_script("arguments[0].click();", switch)
        except TimeoutException:
            pass

    def request_ice_creams(self, count: int = 2) -> None:
        try:
            plus = self.wait.until(EC.element_to_be_clickable(self.plus_helado))
            for _ in range(count):
                try:
                    plus.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", plus)
                time.sleep(0.2)
        except TimeoutException:
            pass

    # ——— Mensaje al conductor ———
    def write_driver_message(self) -> None:
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".overlay")))
        campo = self.wait.until(EC.element_to_be_clickable(self.message_field))
        campo.clear(); campo.send_keys(data.message_for_driver)


class TestUrbanRoutes:
    driver: webdriver.Chrome

    @classmethod
    def setup_class(cls) -> None:
        opts = Options()
        opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        cls.driver = webdriver.Chrome(options=opts)

    def test_full_flow(self) -> None:
        page = UrbanRoutesPage(self.driver)
        self.driver.get(data.urban_routes_url)

        # 1. Ruta
        page.set_route(data.address_from, data.address_to)
        assert page.get_from() == data.address_from
        assert page.get_to() == data.address_to

        # 2. Pedir taxi y tarifa
        page.click_taxi_button()
        page.select_comfort_tariff()

        # 3. Teléfono + verificación
        page.fill_phone_and_verify()

        # 4. Pago con tarjeta
        page.fill_credit_card()

        # 5. Mensaje y extras
        page.write_driver_message()
        page.request_blanket_and_tissues()
        page.request_ice_creams(2)

    @classmethod
    def teardown_class(cls) -> None:
        cls.driver.quit()
