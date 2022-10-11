import os
import json

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

ini_path = './driver_info.json'
chrome_data = json.load(open(ini_path, "r")) if os.path.exists(ini_path) else dict.fromkeys(["version", "path"])


def selenium_wait(driver, by, path, t=10):
    WebDriverWait(driver, t).until(ec.visibility_of_element_located((by, path)))


def chrome_driver_update():
    chrome_version = chromedriver_autoinstaller.get_chrome_version()
    chrome_path = chromedriver_autoinstaller.install().replace('\\', '/')

    if chrome_data["version"] != chrome_version or chrome_data["path"] != chrome_path:
        print("Update Chrome Driver...")
        chrome_data["version"] = chrome_version
        chrome_data["path"] = chrome_path
        with open('driver_info.json', 'w') as f:
            json.dump(chrome_data, f, indent=4)
            f.close()
        print("Complete")
    else:
        print("Chrome Driver is up to date.")


def chrome_driver_set():
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
    ch_options = Options()
    ch_options.add_experimental_option("detach", True)
    ch_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # ch_options.add_argument('headless')
    ch_options.add_argument(f"User-Agent={header['User-Agent']}")
    driver = webdriver.Chrome(chrome_data["path"], options=ch_options)
    driver.set_window_size(1920, 1080)
    driver.minimize_window()
    try : 
        driver_pid = f"{os.path.basename(os.path.dirname(os.path.realpath(__file__)))} || {driver.service.process.pid}\n"
        with open("D:\\chrome_driver_log.txt","a",encoding="utf-8") as file:
            file.write(driver_pid)
            file.flush()
    except : 
        pass
    return driver