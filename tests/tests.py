from hotClaimer.hotClaimer import HotClaimer, isUpgradable
import unittest
# from selenium.webdriver.common.by import By
# import time
# import random


class TestHotAmount(unittest.TestCase):
    def setUp(self):
        self.account = HotClaimer("ac3", "test_sessions")
        pass

    def test_hot_amount(self):
        print(isUpgradable("us3r0unknown.tg"))


if __name__ == '__main__':
    unittest.main()
