import os
import re
import time

from browser import Browser

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

class Variables:
    def __init__(self):
        self.USE_PROXY = False
        self.headless = True
        self.record_biz_without_gov = True
        self.start_page = 0
        self.end_page = 0
        
        self.HOME_URL = "https://bsd.sos.in.gov/PublicBusinessSearch"
        self.LOADING_URL = "https://bsd.sos.in.gov/PublicBusinessSearch#"
        self.DETAILS_URL = "https://bsd.sos.in.gov/PublicBusinessSearch/BusinessInformationFromIndex"
        
        self.SEARCH_PHRASE = os.getenv("SEARCH_PHRASE")
        self.SEARCH_MATCH = os.getenv("SEARCH_MATCH")
        self.SEARCH_TYPE = os.getenv("SEARCH_TYPE")
        self.SEARCH_STATUS = os.getenv("SEARCH_STATUS")
        self.SEARCH_NAME_TYPE = os.getenv("SEARCH_NAME_TYPE")
        self.SEARCH_CITY = os.getenv("SEARCH_CITY")
        self.SEARCH_STREET = os.getenv("SEARCH_STREET")
        self.SEARCH_ZIP = os.getenv("SEARCH_ZIP")
        self.SEARCH_MODE = os.getenv("SEARCH_MODE")

        '''
        ##### Business Search Page Info
        '''
        self.CONTAINS_BUTTON = "//input[@id='rdContains']"
        self.STARTS_WITH_BUTTON = "//input[@id='rdStartsWith']"
        self.EXACT_MATCH_BUTTON = "//input[@id='rdExactMatch']"
        self.MATCH_DICT = {"Contains": self.CONTAINS_BUTTON, "Start With": self.STARTS_WITH_BUTTON, "Exact Match": self.EXACT_MATCH_BUTTON}
        
        self.BIZ_NAME_INPUT = "//input[@id='txtBusinessName']"
        self.BIZ_ID_INPUT = "//input[@id='txtBusinessID']"
        self.FILING_NUMBER_INPUT = "//input[@id='txtFilingNumber']"
        self.REGISTERED_AGENT_INPUT = "//input[@id='txtAgent']"
        self.INCORPORATOR_INPUT = "//input[@id='txtPrincipalName']"
        
        self.SEARCH_BUTTON = "//input[@id='btnSearch']"
        self.RESET_BUTTON = "//input[@id='btnReset']"
        
        '''
        ##### Business Advanced Search Info
        '''
        self.BIZ_STATUS = "BusinessStatus"
        self.BIZ_TYPE = "BusinessEntityType"
        self.BIZ_NAME_TYPE = "ddlNameType"
        self.BIZ_TYPE_LIST = ["None (Search for All)", "Business Commercial Registered Agent", "CRA Both", "Domestic Agricultural Coop", "Domestic Benefit Corporation", "Domestic Business Trust", "Domestic Financial Institution", "Domestic For-Profit Corporation", "Domestic Insurance Corporation", "Domestic Limited Liability Company", "Domestic Limited Liability Partnership", "Domestic Limited Partnership", "Domestic Master LLC", "Domestic Miscellaneous", "Domestic Nonprofit Corporation", "Domestic Professional Benefit Corporation", "Domestic Professional Corporation", "Domestic Series", "Foreign Agricultural Coop", "Foreign Benefit Corporation", "Foreign Business Trust", "Foreign Financial Institution", "Foreign For-Profit Corporation", "Foreign Insurance Corporation", "Foreign Limited Liability Corporation", "Foreign Limited Liability Partnership", "Foreign Limited Partnership", "Foreign Master LLC", "Foreign Miscellaneous", "Foreign Nonprofit Corporation", "Foreign Professional Benefit Corporation", "Foreign Professional Corporation", "Foreign Series", "Individual Commercial Registered Agent"]
        self.BIZ_STATUS_LIST = ["None (Search for All)", "Active", "Admin Dissolved", "Inactive", "Cancelled", "Voluntarily Dissolved", "Revoked", "Withdrawn", "Merged", "Judicially Dissolved", "Non-Qualified Merged", "Surrendered", "Reserved", "Expired", "Abandoned", "Converted", "Pending Admin Dissolution", "Pending Revocation", "Pending Conversion", "Converted Out", "Pending", "Past Due", "Pending Domestication", "Pending Surrender", "Pending Merger", "Voluntarily Dissolved (Name Protected)", "Pending Share Exchange", "NSF", "Terminated"]
        self.BIZ_NAME_TYPE_LIST = ["None (Search for All)", "RESERVED NAME", "LEGAL NAME", "FOREIGN LEGAL NAME", "ALTERNATE NAME", "SERIES LEGAL NAME", "FOREIGN SERIES LEGAL NAME", "ALTERNATE SERIES NAME", "ASSUMED BUSINESS NAME", "FORMER NAME"]
        self.BIZ_STREET_INPUT = "//input[@id='txtStreetAddress1']"
        self.BIZ_CITY_INPUT = "//input[@id='txtCity']"
        self.BIZ_ZIP_INPUT = "//input[@id='txtZipCode']"
        self.BIZ_TITLES = ["Business Name", "Business ID", "Entity Type", "Business Status", "Creation Date", "Principal Office Address", "Jurisdiction of Formation"]
        
        '''
        ##### Business Results Info
        '''
        self.ERROR_MESSAGE = "//input[@id='hdnErrorMessage']"
        self.NO_DATA_FOUND_MESSAGE = "//li[contains(., 'No data found.')]"
        self.PROCESSING_MESSAGE = "//div[@id='process']"
        self.NEXT_BUTTON = '//a[contains(text(),"Next")]'
        self.BACK_BUTTON = "//input[@id='btnBack']"
        self.PAGE_INFO_TEXT = "//li[@class='pageinfo']"
        self.RETURN_BUTTON = "//input[@id='btnReturn']"
        
        self.Total_Pages = {"Home": "//h1[contains(text(),'your one-stop source')]", "Commercial RA": '//td[contains(text(),"Commerical Registered Agent Details")]', "Results":'//td[contains(text(),"Business Search")]', "Details": '//td[contains(text(),"Business Details")]', "Loading": "//div[@id='process']"}
    
    def get_lapsed_time(self, start_time, time_to_lapse: datetime) -> str:
        time_lapsed = time_to_lapse - start_time
        
        convert = time.strftime("%H:%M:%S", time.gmtime(time_lapsed.seconds))
        
        return convert
    
    def get_hourly_rate(self, start_time, records_recorded) -> int or None:
        if records_recorded != 0:
            return int((records_recorded * 3600) / (datetime.now() - start_time).seconds)
        else:
            return None
        
    def get_percentage_completed(self, records_found, records_recorded) -> round or None:
        if records_found != 0 and records_recorded != 0:
            return round(((records_recorded / records_found) * 100), 2)
        else:
            return None
        
    def get_total_pages(self, browser: Browser) -> int:
        pageinfo = browser.current_driver.find_element("xpath","//li[@class='pageinfo']").text
        split = pageinfo.split(",")[0]
        pages = re.sub("Page 1 of ", "", split)
        
        self.total_pages_found = int(pages)
        
        return int(pages)
    
    def get_current_page(self, browser: Browser) -> str or int:
        for page in self.Total_Pages:
            try:
                if browser.current_driver.find_element("xpath", self.Total_Pages[page]).is_displayed():
                    if page == "Results":
                        page_number = self.get_current_page_number(browser)
                        return page_number
                    else:
                        return page
            except Exception:
                pass
                
    def get_current_page_number(self, browser: Browser) -> int:
        pageinfo = browser.current_driver.find_element("xpath","//li[@class='pageinfo']").text
        front_split = pageinfo.split(",")[0]
        back_split = front_split.split(" of ")[0]
        page_num = re.sub("Page ", "", back_split)
        
        return int(page_num)
        
    def get_total_records(self, browser: Browser) -> int:
        pageinfo = browser.current_driver.find_element("xpath","//li[@class='pageinfo']").text
        split_total = pageinfo.split(",")[1]
        split_biz = split_total.split(" of ")[1]
        stripped_biz_found = split_biz.strip()
        
        return int(stripped_biz_found)
    
    def calculate_etc(self, start_time, records_found, records_recorded) -> str or None:
        lapsed_time = (datetime.now() - start_time).seconds
        if records_recorded == 0:
            return None
        
        rate_of_progress = records_recorded / lapsed_time
        remaining_work = records_found - records_recorded
        etc = remaining_work / rate_of_progress if remaining_work > 0 else 0
        
        convert = time.strftime("%H:%M:%S", time.gmtime(int(etc)))
        
        return convert