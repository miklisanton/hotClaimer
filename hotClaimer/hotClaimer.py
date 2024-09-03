from proxytg import TelegramAccount
import time
from selenium.webdriver.common.by import By
import json
import os
import logging
import random
import base64
import requests


logger = logging.getLogger(__name__)


class HotClaimer(TelegramAccount):
    def __init__(self, name, sessions_dir):
        super().__init__(name, sessions_dir)
        self.hot_login = ""
        self.needs_upgrade = False
        try:
            self.hot_login = self.load_hot_local_storage()
            print(self.hot_login)
            needs_upgrade = isUpgradable(self.hot_login)
            print(needs_upgrade)
            logger.warning(f'Loaded hot wallet local storage for {self.account_name}')
            loaded = True
        except FileNotFoundError:
            self.save_hot_local_storage()
            loaded = True
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
        username = ""
        if not os.path.exists(os.path.join(self.sessions_dir, f'{self.account_name}_hot_local_storage.json')):
            raise FileNotFoundError
        self.open_hot_app()
        time.sleep(2)
        # Switch to the iframe
        iframe = self.driver.find_element(By.XPATH, "//iframe")
        self.driver.switch_to.frame(iframe)
        time.sleep(2)
        with open(os.path.join(self.sessions_dir, f'{self.account_name}_hot_local_storage.json'), 'r') as file:
            local_storage = json.load(file)
            username = next(iter(local_storage))
            for key, value in local_storage.items():
                self.driver.execute_script(f"window.localStorage.setItem(arguments[0], arguments[1]);", key, value)
        self.driver.refresh()

        return username

    def open_hot_app(self):
        self.driver.get("https://web.telegram.org/k/#@herewalletbot")
        time.sleep(random.randint(10, 12))
        self.driver.find_element(By.CSS_SELECTOR, ".new-message-bot-commands").click()
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, ".autocomplete-peer-helper-list-element:nth-child(1)").click()
        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, ".anchor-url > strong").click()
        time.sleep(2)
        self.driver.find_element(By.XPATH, "/html/body/div[7]/div/div[2]/button[1]/div").click()

    def claim(self):
        self.open_hot_app()
        time.sleep(2)
        # Switch to the iframe
        iframe = self.driver.find_element(By.XPATH, "//iframe")
        self.driver.switch_to.frame(iframe)
        time.sleep(random.randint(20, 25))
        storage = self.driver.find_element(By.XPATH, "//*[@id='root']/div/div/div[1]/div/div/div[4]/div[2]/div")
        self.driver.execute_script("arguments[0].scrollIntoView(true)", storage)
        storage.click()
        time.sleep(2)
        # Check news(if available) or claim
        self.driver.find_element(By.XPATH, "//*[@id='root']/div/div/div[2]/div/div[3]/div/div[2]/div[2]/button").click()
        time.sleep(2)
        # Claim
        try:
            self.driver.find_element(By.XPATH, "//*[@id='root']/div/div/div[2]/div/div[3]/div/div[2]/div[2]/button").click()
        except Exception:
            raise Exception("Claim button not clickable")
        # 

    def upgrade_storage(self):
        # Get current storage level

        amount = self.account.driver.find_element(By.XPATH,
                                          "//*[@id='root']/div/div/div[2]/div/div[2]/div[3]/p[2]")
        print(amount.text)


def isUpgradable(account_id, rpc_url="https://rpc.mainnet.near.org"):

    upgradesMap = {'0': 0.2, '1': 1, '2': 2, '3': 5, '4': 15, '5': 100000}
    try:
        # Encode the account ID to base64
        json_string = json.dumps({"account_id": account_id}).encode('utf-8')
        args_base64 = base64.b64encode(json_string).decode('utf-8')

        # Prepare the payload
        payload = {
            "jsonrpc": "2.0",
            "id": "dontcare",
            "method": "query",
            "params": {
                "request_type": "call_function",
                "finality": "optimistic",
                "account_id": "game.hot.tg",
                "method_name": "get_user",
                "args_base64": args_base64,
            }
        }

        # Send the HTTP POST request
        response = requests.post(rpc_url, json=payload)
        response.raise_for_status()

        # Parse the JSON response
        rpc_response = response.json()
        result = rpc_response['result']['result']

        game_state = json.loads(bytes(result).decode('utf-8'))

        if game_state is None:
            return False

        balance = int(game_state.get('balance')) / 10 ** 6
        firespace = game_state.get('firespace')

        if upgradesMap[str(firespace)] < balance:
            return True

        return False

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise Exception(f"Failed to process response: {e}")
