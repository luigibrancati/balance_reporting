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
    driver.get("https://banking.hellobank.it/it/login/")
    driver.switch_to.window(driver.window_handles[0])
    try:
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        button.click()
    except TimeoutException:
        logger.log(10, "not found!")
        pass
    iframe = driver.find_element_by_css_selector(".hbLoginContent > iframe")
    driver.switch_to.frame(iframe)
    user = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "_real_username")))
    password = driver.find_element(By.ID, "_real_password")
    user.send_keys("3195140723")
    password.send_keys("938975")
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "login-button")))
    login_button.click()
    driver.refresh()
    if driver.title == 'SCA':
        iframe_sca = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "iframe_app-layer")))
        driver.switch_to.frame(iframe_sca)
        spinner = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "spinner")))
        if spinner:
            driver.refresh()
        else:
            logger.log(10, "Not Authenticated")
            exit(2)
    WebDriverWait(driver, 30).until(EC.title_is("home"))
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

