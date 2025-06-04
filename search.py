from browser import Browser
from captcha import Captcha
from vars import Variables

from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

class Search:
    def __init__(self):
        self.vars = Variables()
        self.BIZ_OPTION_STATUS = {"name": "status", "element_id": self.vars.BIZ_STATUS, "user_input": self.vars.SEARCH_STATUS, "options": self.vars.BIZ_STATUS_LIST}
        self.BIZ_OPTIONS = [ self.BIZ_OPTION_STATUS ]

    def select_biz_option(self, browser: Browser, biz_option: dict) -> str:
        select_element = browser.current_driver.find_element(By.ID, biz_option["element_id"])
        select = Select(select_element)
        select.select_by_value(str(biz_option["user_input"]))
        
        return(f"{biz_option['user_input']} has been clicked.")
    
    def open_home_page(self, browser: Browser) -> Browser:
        return browser.open_url(self.vars.HOME_URL)

    def get_results_table(self, browser: Browser) -> BeautifulSoup:
        html = browser.current_driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        
        resultsTable = soup.findAll('a', href="#")
        
        for r in resultsTable:
            if r.text.strip() == "Go to Page":
                resultsTable.remove(r)

        return resultsTable
    
    def is_business_visible(self, browser: Browser, biz_id: str or int) -> bool:
        try:
            if browser.current_driver.find_element("xpath",f"//a[contains(., '{biz_id}')]").is_displayed():
                return True
            else:
                return False
        except Exception:
            return False
        
    def click_business(self, browser: Browser, biz_id: str or int) -> str:
        if self.is_business_visible(browser, biz_id):
            browser.current_driver.find_element("xpath","//a[contains(., '"+biz_id+"')]").click()
            WebDriverWait(browser.current_driver, 15).until(EC.url_changes)
            return "Business Clicked"
        else:
            return(f"Biz ID {biz_id} is not visisble")
        
    def navigate_to_page(self, browser: Browser, page: int) -> None:
        try:
            browser.current_driver.find_element("xpath", "//input[@id='txtCommonPageNo']").click()
            browser.current_driver.find_element("xpath", "//input[@id='txtCommonPageNo']").send_keys(str(page))
            browser.current_driver.find_element("name", "lkGoPage").click()
        except Exception:
            sleep(1)
        else:
            sleep(1)
            
    def go(self, browser: Browser, phrase: str, page_num: int = 1) -> str:
        cap = Captcha(browser)
        cap_results = cap.solve()
        if cap_results:
            if cap_results != 0:
                if self.vars.SEARCH_MATCH == "1":
                    browser.current_driver.find_element("xpath", self.vars.STARTS_WITH_BUTTON).click()
                    print("Clicked 'Starts With' Button")
                elif self.vars.SEARCH_MATCH == "2":
                    browser.current_driver.find_element("xpath", self.vars.EXACT_MATCH_BUTTON).click()
                    print("Clicked 'Exact Match' Button")
                    
                browser.current_driver.find_element("xpath", self.vars.BIZ_NAME_INPUT)
                print("Clicked business name input field")
                
                browser.current_driver.find_element("xpath", self.vars.BIZ_NAME_INPUT).clear()
                print("Cleared business name input field")
                
                browser.current_driver.find_element("xpath", self.vars.BIZ_NAME_INPUT).send_keys(phrase)
                print("Typed our phrase in the input field")
                
                for o in self.BIZ_OPTIONS:
                    if o["user_input"] != 0:
                        self.select_biz_option(browser, o)
    
                if self.vars.SEARCH_CITY != "":
                    BizCityInput = browser.current_driver.find_element("name", "txtCity")
                    BizCityInput.click()
                    BizCityInput.clear()
                    BizCityInput.send_keys(self.vars.SEARCH_CITY)
                    
                if self.vars.SEARCH_STREET != "":
                    BizAddyInput = browser.current_driver.find_element("name", "txtStreetAddress1")
                    BizAddyInput.click()
                    BizAddyInput.clear()
                    BizAddyInput.send_keys(self.vars.SEARCH_STREET)
                    
                if self.vars.SEARCH_ZIP != "":
                    BizZipInput = browser.current_driver.find_element("name", "txtZipCode")
                    BizZipInput.click()
                    BizZipInput.clear()
                    BizZipInput.send_keys(self.vars.SEARCH_ZIP)
    
    
                browser.current_driver.find_element("xpath", "//input[@id='btnSearch']").click()
                
                print("Search Button Clicked. Loading...")
                
                return "Search completed"
            else:
                print("Captcha ID is 0... Refreshing Home Page!")
                browser.current_driver.open_url(self.vars.HOME_URL)
                sleep(5)
        else:
            return "Captcha failed..."