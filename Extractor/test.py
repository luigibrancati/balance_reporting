from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support import expected_conditions as EC
import time
from sys import exit
import logging
from selenium.common.exceptions import TimeoutException

logger = logging.Logger('logger')
logger.log(10, "Start")

with Firefox() as driver:
    driver.get("https://banking.hellobank.it/it/home/")
    driver.switch_to.window(driver.window_handles[0])
    WebDriverWait(driver, 30).until(EC.title_is("Login"))
    menu = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "I-miei-conti-correnti-LV1")))
    menu.click()
    try:
        saldo = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "Saldo-e-movimenti-LV2")))
        saldo.click()
    except TimeoutException:
        logger.log(10, "not found saldo button!")
        exit(2)
    iframe_saldo = driver.find_element(By.ID, 'displayboardd')
    driver.switch_to.frame(iframe_saldo)
    data_inizio = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "UU00325_DTA_INIZIO_MOVIMENTI")))
    data_fine = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "UU00325_DTA_FINE_MOVIMENTI")))
    data_inizio.send_keys('01/01/2021')
    data_fine.send_keys('01/07/2021')
    time.sleep(5)

