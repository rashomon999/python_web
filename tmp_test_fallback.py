from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import crear_driver
import time

print('Iniciando prueba del fallback alternativo...')
driver = crear_driver()
try:
    driver.get('https://www.instagram.com')
    time.sleep(10)
    xpath = "(//div[@data-visualcompletion='ignore' and contains(@style, 'inset')])[1]"
    print('Esperando que aparezca el fallback...')
    time.sleep(5)
    print('Buscando XPath:', xpath)
    elem = WebDriverWait(driver, 12).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    print('ENCONTRADO:', elem.is_displayed())
    elem.click()
    print('CLICK_OK')
    time.sleep(3)
except Exception as e:
    print('ERROR:', e)
finally:
    driver.quit()
