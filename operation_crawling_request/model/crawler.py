import os
import sys
import json
import chromedriver_autoinstaller
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent))
from common import CWD


class Crawler:
    driver_info_path = f"{CWD}/driver_info.json"

    def __init__(self):
        self.chrome_data = json.load(
            open(self.driver_info_path, "r")) if os.path.exists(self.driver_info_path) \
            else dict.fromkeys(["version", "path"])
        self.chrome_driver_update()
        self.driver = self.chrome_driver_set()

    def chrome_driver_update(self):
        chrome_version = chromedriver_autoinstaller.get_chrome_version()
        chrome_path = chromedriver_autoinstaller.install().replace('\\', '/')

        if self.chrome_data["version"] != chrome_version or self.chrome_data["path"] != chrome_path:
            print("Update Chrome Driver...")
            self.chrome_data["version"] = chrome_version
            self.chrome_data["path"] = chrome_path
            with open(self.driver_info_path, 'w') as f:
                json.dump(self.chrome_data, f, indent=4)
                f.close()
            print("Complete")
        else:
            print("Chrome Driver is up to date.")

    def chrome_driver_set(self):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
        ch_options = Options()
        ch_options.add_experimental_option("detach", True)
        ch_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        ch_options.add_argument('headless')
        ch_options.add_argument(f"User-Agent={header['User-Agent']}")
        driver = webdriver.Chrome(self.chrome_data["path"], options=ch_options)
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

    def close(self):
        self.driver.quit()

    @staticmethod
    def selenium_wait(driver, by, path, t=10):
        WebDriverWait(driver, t).until(ec.visibility_of_element_located((by, path)))


if __name__ == "__main__":
    crawler = Crawler()
