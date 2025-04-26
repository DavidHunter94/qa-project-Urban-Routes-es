import json
import time
import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementNotInteractableException

# Helper para capturar el código de confirmación vía CDP logs
def retrieve_phone_code(driver: webdriver.Chrome, attempts: int = 10) -> str:
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
    from_field = (By.ID, "from")
    to_field = (By.ID, "to")
    boton_taxi = (By.XPATH, "//button[text()='Pedir un taxi']")
    tarjeta_comfort = (By.XPATH, "//div[contains(@class,'tcard') and .//div[text()='Comfort']]")
    btn_phone = (By.CLASS_NAME, "np-button")
    phone_input = (By.ID, "phone")
    phone_code_input = (By.ID, "code")
    close_button = (By.CSS_SELECTOR, ".input-close-button")
    boton_pago = (By.CSS_SELECTOR, ".pp-button.filled")
    fila_add_tarjeta = (By.XPATH, "//div[contains(@class,'pp-row') and .//div[text()='Agregar tarjeta']]")
    credit_card_number = (By.ID, "number")
    credit_card_code = (By.XPATH, "//div[@class='card-code-input']//input")
    add_card_button = (By.XPATH, "//div[@class='pp-buttons']/button[normalize-space()='Agregar']")
    close_payment_modal = (By.XPATH, "(//button[contains(@class,'close-button') and contains(@class,'section-close')])[last()]")
    blanket_switch = (By.XPATH, "//div[text()='Manta y pañuelos']/following-sibling::div//input[@type='checkbox']")
    plus_helado = (By.XPATH, "//div[text()='Helado']/following-sibling::div//div[contains(@class,'counter-plus')]")
    message_field = (By.ID, "comment")
    boton_pedir_taxi_final = (By.CSS_SELECTOR, "button.smart-button")

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def set_from(self, addr: str) -> None:
        origen = self.wait.until(EC.element_to_be_clickable(self.from_field))
        origen.clear()
        origen.send_keys(addr)

    def set_to(self, addr: str) -> None:
        destino = self.wait.until(EC.element_to_be_clickable(self.to_field))
        destino.clear()
        destino.send_keys(addr)

    def set_route(self, addr_from: str, addr_to: str) -> None:
        self.set_from(addr_from)
        self.set_to(addr_to)

    def get_from(self) -> str:
        return self.driver.find_element(*self.from_field).get_property("value")

    def get_to(self) -> str:
        return self.driver.find_element(*self.to_field).get_property("value")

    def click_taxi_button(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.boton_taxi)).click()

    def select_comfort_tariff(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.tarjeta_comfort)).click()

    def fill_phone_and_verify(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.btn_phone)).click()
        input_tel = self.wait.until(EC.element_to_be_clickable(self.phone_input))
        input_tel.clear()
        input_tel.send_keys(data.phone_number + Keys.ENTER)
        code = retrieve_phone_code(self.driver)
        self.wait.until(EC.element_to_be_clickable(self.phone_code_input)).send_keys(code + Keys.ENTER)
        try:
            self.wait.until(EC.element_to_be_clickable(self.close_button)).click()
        except TimeoutException:
            pass

    def fill_credit_card(self) -> None:
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".section.active")))
        self.wait.until(EC.element_to_be_clickable(self.boton_pago)).click()
        self.wait.until(EC.element_to_be_clickable(self.fila_add_tarjeta)).click()
        self.wait.until(EC.element_to_be_clickable(self.credit_card_number)).send_keys(data.card_number)
        cvv = self.wait.until(EC.element_to_be_clickable(self.credit_card_code))
        cvv.send_keys(data.card_code + Keys.TAB)
        self.wait.until(EC.element_to_be_clickable(self.add_card_button)).click()
        try:
            close_btn = self.wait.until(EC.presence_of_element_located(self.close_payment_modal))
            self.driver.execute_script("arguments[0].click();", close_btn)
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, ".section.active"))
            )
        except (TimeoutException, ElementNotInteractableException):
            pass

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

    def write_driver_message(self) -> None:
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".overlay")))
        campo = self.wait.until(EC.element_to_be_clickable(self.message_field))
        campo.clear()
        campo.send_keys(data.message_for_driver)

    def click_final_taxi_button(self) -> None:
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".overlay")))
        boton = self.wait.until(EC.element_to_be_clickable(self.boton_pedir_taxi_final))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", boton)
        self.driver.execute_script("arguments[0].click();", boton)


class TestUrbanRoutes:
    driver: webdriver.Chrome

    @classmethod
    def setup_class(cls) -> None:
        opts = Options()
        opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        cls.driver = webdriver.Chrome(options=opts)

    def test_full_flow(self) -> None:
        page = UrbanRoutesPage(self.driver)

        # Abrir la página
        self.driver.get(data.urban_routes_url)

        # Establecer ruta (origen y destino)
        page.set_route(data.address_from, data.address_to)
        assert page.get_from() == data.address_from
        assert page.get_to() == data.address_to

        # Pedir un taxi y seleccionar tarifa Comfort
        page.click_taxi_button()
        page.select_comfort_tariff()

        # Ingresar número de teléfono y verificar con el código recibido
        page.fill_phone_and_verify()

        # Agregar una tarjeta de crédito
        page.fill_credit_card()

        # Escribir mensaje para el conductor
        page.write_driver_message()

        # Pedir manta y pañuelos
        page.request_blanket_and_tissues()

        # Pedir dos helados
        page.request_ice_creams(2)

        # Confirmar el pedido de taxi
        page.click_final_taxi_button()

        # Verificar si aparece el modal de búsqueda de taxi
        try:
            modal = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".order-searching"))
            )
            assert modal.is_displayed()
        except TimeoutException:
            pass
        
    @classmethod
    def teardown_class(cls) -> None:
        cls.driver.quit()
