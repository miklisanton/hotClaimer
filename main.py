from proxytg import TelegramAccount
import time
from selenium.webdriver.common.by import By
import json
import os
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING,  # Set the logging level
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format of the log messages
                    datefmt='%Y-%m-%d %H:%M:%S',  # Date format
                    handlers=[logging.StreamHandler()])  # Log to the console

class HotClaimer(TelegramAccount):
    def __init__(self, name, sessions_dir):
        super().__init__(name, sessions_dir)
        try:
            self.load_hot_local_storage()
            logger.warning(f'Loaded hot wallet local storage for {self.account_name}')
        except FileNotFoundError:
            self.save_hot_local_storage()
            logger.warning(f'Saved hot wallet local storage for {self.account_name}')

    def save_hot_local_storage(self):
        self.driver.get('https://web.telegram.org')
        input('Press Enter after importing hot wallet account')
        iframe = self.driver.find_element(By.XPATH, "//iframe")
        self.driver.switch_to.frame(iframe)
        time.sleep(5)
        local_storage = self.driver.execute_script('return window.localStorage')
        with open(os.path.join(self.sessions_dir, f'{self.account_name}_hot_local_storage.json'), 'w') as file:
            json.dump(local_storage, file)

    def load_hot_local_storage(self):
        # Open hot wallet iframe
        self.driver.get("https://web.telegram.org/k/#@herewalletbot")
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, ".new-message-bot-commands").click()
        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, ".autocomplete-peer-helper-list-element:nth-child(1)").click()
        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, ".anchor-url > strong").click()
        time.sleep(2)
        self.driver.find_element(By.XPATH, "/html/body/div[7]/div/div[2]/button[1]/div").click()
        time.sleep(2)
        # Switch to the iframe
        iframe = self.driver.find_element(By.XPATH, "//iframe")
        self.driver.switch_to.frame(iframe)
        time.sleep(2)
        with open(os.path.join(self.sessions_dir, f'{self.account_name}_hot_local_storage.json'), 'r') as file:
            local_storage = json.load(file)
            for key, value in local_storage.items():
                self.driver.execute_script(f"window.localStorage.setItem(arguments[0], arguments[1]);", key, value)
        self.driver.refresh()


acc = HotClaimer('acc1', 'sessions')
time.sleep(500)

