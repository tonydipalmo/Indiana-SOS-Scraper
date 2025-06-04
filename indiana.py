import json
import os
import logging

from browser import Browser
from scraper import Scraper
from business import BusinessList
from vars import Variables
from search import Search

from datetime import datetime

from time import sleep
from random import randint

from bs4 import BeautifulSoup

from dotenv import load_dotenv

load_dotenv()

class BusinessDataError(Exception):
    pass

class Indiana:
    def __init__(self):
        self.vars = Variables()
        self.search = Search()
        self.browser = Browser(headless=self.vars.headless)
        
        self.run_status = ""
        self.current_business_id = ""
        self.total_pages_found = 0
        self.none_page_count = 0
        self.start_page = self.vars.start_page
        self.end_page = self.vars.end_page
        self.current_page = 1
        if self.start_page > 0:
            self.current_page = self.start_page
            
        self.total_records_recorded = 0
        self.total_records_found = 0
        self.total_commercial_ra = 0
        self.total_gov_persons = 0
        
        self.record_biz_without_gov = self.vars.record_biz_without_gov
        self.cycle_page_recording_biz = False
        self.cycle_page_running = False
        self.cycle_page_biz_count = 0
        self.cycle_page_count = 0
        self.cycle_page_results_table = ""
        self.cycle_page_current_biz = ""
        self.cycle_page_next_biz = ""
        
        self.not_recorded = []
        self.not_recorded_count = 0
        
        self.append_list = []
        self.business_list = BusinessList
                
        self.start_time = datetime.now()
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        self.handler = logging.FileHandler('logs\\indiana.log')
        self.handler.setLevel(logging.INFO)
        
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        
        self.logger.addHandler(self.handler)
        
    def open_home_page(self, browser: Browser) -> Browser:
        return browser.open_url(self.vars.HOME_URL)
    
    def get_inputs(self, search_phrase: str = ""):
        if self.vars.SEARCH_PHRASE == "" and search_phrase == "":
            self.vars.SEARCH_PHRASE = input("Please enter your search query:")
            print(f"You've entered {self.vars.SEARCH_PHRASE}.")
        else:
            if search_phrase != "":
                self.vars.SEARCH_PHRASE = search_phrase

                
        
        if self.vars.SEARCH_STATUS == "0":
            self.vars.SEARCH_STATUS = self.get_biz_input(name="status", input_id=self.vars.SEARCH_STATUS, options=self.vars.BIZ_STATUS_LIST)
        
        self.BIZ_OPTION_STATUS = {"name": "status", "element_id": self.vars.BIZ_STATUS, "user_input": self.vars.SEARCH_STATUS, "options": self.vars.BIZ_STATUS_LIST}
        self.BIZ_OPTIONS = [ self.BIZ_OPTION_STATUS ]
          
    def get_biz_input(self, name: str, input_id: str, options: list) -> int:
        print("What is the business "+name+"?")
        current_biz = 0
        for t in options:
            print(f"{current_biz} - {t}")
            current_biz+=1
            
        while True:
            try:
                user_input = input()
                input_id = int(user_input)
                if input_id >= len(options):
                    print("Invalid input. Please enter a valid number.")
                else:
                    return int(user_input)
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    
    def get_search_match_input(self) -> int:
        print("Please select how you'd like to match the search for this phrase (enter only a number):")
        current_match_option = 0
        for m in self.vars.MATCH_DICT:
            print(f"{current_match_option} - {m}")
            current_match_option+=1
            
        while True:
            try:
                user_input = input()
                self.vars.SEARCH_MATCH = int(user_input)
                if self.vars.SEARCH_MATCH > 2:
                    print("Invalid input. Please enter a valid number.")
                else:
                    return int(user_input)
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                
    def get_business_data(self, biz_id: str or int) -> str or None:
        scraper = Scraper(browser=self.browser.current_driver)
        business_data = scraper.run()
        
        return business_data
        
    def record_business(self, biz_id: str):
        self.cycle_page_recording_biz = True
        self.run_status = f"Recording business {biz_id}"
        
        results = self.get_business_data(biz_id)
        self.total_gov_persons+=results["Gov Persons Found"]
        
        if results != None:
            if results["Business ID"] == biz_id:
                
                if self.record_biz_without_gov:
                    self.append_list.append(results["Business Details"])
                    self.total_records_recorded+=1
                else:
                    if results["Gov Persons Found"] != 0:
                        self.append_list.append(results["Business Details"])
                        self.total_records_recorded+=1
                    else:
                        self.not_recorded.append(results["Business Details"])
                    
                self.cycle_page_recording_biz = False
                return True
            else:
                raise BusinessDataError("Incorrect Business ID was selected")
        else:
            raise BusinessDataError("Results table is none")
            
    def _is_403_page(self, browser):
        html = browser.current_driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        if soup.title.text == "403 Forbidden":
            self.run_status = "403 Error! Sleeping for 30 seconds..."
            sleep(30)
            
            return True
        else:
            return False
    
    def _handle_page_new_cycle(self):
        if self.cycle_page_running == False:
            self.cycle_page_count = 1
            self.cycle_page_results_table = self.search.get_results_table(self.browser)
            self.cycle_page_running = True

        biz_row = self.cycle_page_results_table[(self.cycle_page_count-1)]
        self.cycle_page_biz_count = len(self.cycle_page_results_table)
        
        biz_id = biz_row.text.strip()
        
        if self.cycle_page_count < len(self.cycle_page_results_table):
            self.cycle_page_next_biz = self.cycle_page_results_table[self.cycle_page_count].text.strip()
            
        self.cycle_page_current_biz = biz_id
        
    def _handle_page_update(self):
        self.cycle_page_count+=1
        
        self.cycle_page_current_biz = self.cycle_page_next_biz
        
        if self.cycle_page_count < self.cycle_page_biz_count:
            self.cycle_page_next_biz = self.cycle_page_results_table[self.cycle_page_count].text.strip()
        else:
            self.cycle_page_next_biz = ""
            
        if self.none_page_count > 0:
            self.none_page_count = 0
        
        if self.cycle_page_count > self.cycle_page_biz_count:
            self._handle_page_reset()
        
    def _handle_page_reset(self):
        self.current_page+=1
        self.cycle_page_running = False
        self.cycle_page_next_biz = ""
        self.cycle_page_current_biz = ""
            
    def _handle_page_str(self, current_page):
        if current_page == "Home":
            self.run_status = f"Searching for phrase: {self.vars.SEARCH_PHRASE}"
            self.search.go(self.browser, self.vars.SEARCH_PHRASE)
        elif current_page == "Loading":
            self.run_status = "Loading results..."
        elif current_page == "Details" or current_page == "Commercial RA":
            if current_page != "Commercial RA":
                try:
                    if self.record_business(self.cycle_page_current_biz):
                        self.run_status = f"Recorded biz {self.cycle_page_current_biz}"
                        self._handle_page_update()
                except BusinessDataError as e:
                    if self.not_recorded_count > 6:
                        self.not_recorded.append(self.cycle_page_current_biz)
                        self.run_status = f"Recording biz failed {self.cycle_page_current_biz}"
                        self.not_recorded_count = 0
                        self._handle_page_update()
                    else:
                        self.not_recorded_count+=1
                    print(f"Handled Error: {e}")
            else:
                self.run_status = "Commercial RA found!"
                self.total_commercial_ra+=1
                self._handle_page_update()
            self.browser.current_driver.find_element("xpath",self.vars.BACK_BUTTON).click()
        else:
            self.run_status = f"Currently on page {self.current_page}"
            
        return True
    
    def _handle_page_int(self, current_page):
        if self.total_pages_found == 0 and self.total_records_found == 0:
            self.total_pages_found = self.vars.get_total_pages(self.browser)
            self.total_records_found = self.vars.get_total_records(self.browser)
        if current_page == self.current_page:
            self.run_status = f"Currently on page {self.current_page}"
            if self.cycle_page_running:
                if self.cycle_page_current_biz != "":
                    self.run_status = f"Clicking biz {self.cycle_page_current_biz}"
                    self.search.click_business(self.browser, self.cycle_page_current_biz)
            else:
                self._handle_page_new_cycle()
        else:
            self.run_status = f"Navigating to page {self.current_page}"
            self.search.navigate_to_page(self.browser, self.current_page)
            
        return True
    
    def _handle_page_none(self):
        if self._is_403_page(self.browser):
            self.run_status = "Going back to to homepage!"
            self.open_home_page(self.browser)
        else:
            if self.vars.get_current_page(self.browser) == None:
                if self.none_page_count > 2:
                    self.run_status = "Going back to to homepage!"
                    self.open_home_page(self.browser)
                    
                    self.none_page_count = 0
                else:
                    self.run_status = "Error... Current page is None"
                    self.none_page_count+=1
                    
                sleep(3)
            
        return True
        
    def print_stats(self):
        print("---------------- < RUN STATS > ----------------")
        print("Status: "+self.run_status)
        page = self.vars.get_current_page(self.browser)
        print(f"Current page: {page}")
        print(f"Cycling page {self.current_page} of {self.total_pages_found} pages found")
        print("Search Phrase: "+self.vars.SEARCH_PHRASE)
        
        print("\n")
        time_lapsed = self.vars.get_lapsed_time(self.start_time, datetime.now())
        print(f"TTL: {time_lapsed}")
        
        hourly = self.vars.get_hourly_rate(self.start_time, (self.total_records_recorded+len(self.not_recorded)+self.total_commercial_ra))
        if hourly != None:
            print(f"{hourly} records/hr")
        
        percentage = self.vars.get_percentage_completed(self.total_records_found, (self.total_records_recorded+len(self.not_recorded)+self.total_commercial_ra))
        if percentage != None:
            print(f"{percentage}% complete")
            
        etc = self.vars.calculate_etc(self.start_time, self.total_records_found, (self.total_records_recorded+len(self.not_recorded)+self.total_commercial_ra))
        if etc != None:
            print(f"ETC: {etc}")
            
        print("\n")

        if self.total_records_found != 0:
            print(f"Biz list count: {len(self.append_list)}")
            print(f"Recorded {self.total_records_recorded} of {self.total_records_found} records found")
            print(f"Total Governing Persons found: {self.total_gov_persons}")
        
        if self.total_commercial_ra > 0:
            print(f"Total commercial business RA's found: {self.total_commercial_ra}")
        
        not_recorded_count = len(self.not_recorded)
        if not_recorded_count > 0:
            print(f"Total businesses skipped: {not_recorded_count}")
            
        print("---------------- < / RUN STATS > ----------------")
        
    def next_step(self) -> None:
        current_page = self.vars.get_current_page(self.browser)
        
        hourly = self.vars.get_hourly_rate(self.start_time, self.total_records_recorded)
        
        if isinstance(current_page, str):
            str_results = self._handle_page_str(current_page)
            if str_results:
                if hourly != None and hourly < 400:
                    sleep(1)
                else:
                    sleep(randint(1,2))
        elif isinstance(current_page, int):
            int_results = self._handle_page_int(current_page)
            if int_results:
                if hourly != None and hourly < 400:
                    sleep(randint(1,2))
                else:
                    sleep(randint(2, randint(3, 6)))
        elif current_page == None:
            none_results = self._handle_page_none()
            if none_results:
                sleep(randint(5,7))
        
            
    def save(self):
        self.business_list = BusinessList.validate({"name":self.vars.SEARCH_PHRASE, "city":os.getenv('CITY'), "business_list": self.append_list})
        
        timestamp = datetime.now().strftime("%Y%d%m%H%H%S")
        
        with open(f"scraped_files\\{self.vars.SEARCH_PHRASE} {os.getenv('SEARCH_CITY')} {timestamp}.json", 'w') as f:
            json.dump(self.business_list.dict(), f)
            
        return self.business_list.dict()
                
    def run(self, search_phrase: str = "") -> dict:
        if self.start_page > 1 and self.current_page == 1:
            self.current_page = self.start_page
        
        print("Welcome to Indiana SOS Scraper")
    
        print("Getting inputs")
        self.get_inputs(search_phrase)
        
        print("Opening Home Page")
        self.open_home_page(self.browser)
        
        print("Indiana SOS Started!")
        
        self.run_status = "Running..."

        while True:
            self.next_step()
            
            self.print_stats()
            
            if self.end_page != 0:
                if self.current_page == (self.end_page + 1):
                    break
             
            if self.cycle_page_biz_count != 0 and self.current_page > self.total_pages_found and self.cycle_page_count > self.cycle_page_biz_count:
                break
         
        self.end_time = datetime.now()
        self.lapsed_time = self.vars.get_lapsed_time(self.start_time, self.end_time)
        
        self.run_status = "Run complete"
        
        results = self.save()
        
        return results
        
def main():
    print("Starting...")
    new = Indiana()
    new.run()

if __name__ == '__main__':
    main()  