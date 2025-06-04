from vars import Variables

from bs4 import BeautifulSoup

from business import Business, BusinessDetails, GoverningPerson, RegisteredAgent

from time import sleep

class Scraper:
    def __init__(self, browser):
        self.browser = browser
        self.vars = Variables()
        
        self.html = browser.page_source
        self.soup = BeautifulSoup(self.html, 'html.parser')
        
        self.governing_persons_data = ""
        self.registered_agent_data = ""
        self.business_data = ""
        
        self.current_item = ""
        self.business_dict = {}
        self.agent_dict = {}
        self.governing_person_names  = []
        self.governing_persons_found = 0
        self.registered_agent = ""
        
    def get_data_from_pannels(self) -> dict:
        data_pannels = self.soup.find_all('div', class_='data_pannel')
        
        data = {}
        
        for data in data_pannels:
            tags = data.find_all()

            for tag in tags:
                if str(tag.string) != "None":
                    stripped_text = str(tag.string).strip()
                    if "Business Details" == stripped_text:
                        data["Business Details"] = data
                        self.business_data = data
                        break
                    if "Governing Person Information" == stripped_text:
                        data["Governing Person"] = data
                        self.governing_persons_data = data
                        break
                    if "Registered Agent Information" == stripped_text:
                        data["Registered Agent"] = data
                        self.registered_agent_data = data
                        break
        return data
    
    def extract_governing_persons_count(self) -> int:
        try:
            table = self.governing_persons_data.find('table')
            strip_x = table.text.replace("\n", "")
            split_gov = strip_x.split("Governing Person Information", 1)
            split_gov_final = split_gov[1].split("Page 1 of ", 1)
            splitgovPages = split_gov_final[1]
            govPages = int(splitgovPages.split(", records 1 to ",1)[0])
        except Exception:
            return False
        else:
            return govPages
    
    def extract_governing_persons_data(self) -> list[GoverningPerson]:
        governing_persons = []
        
        current_gov_page  = 1
        gov_pages = 1
        if self.extract_governing_persons_count():
            gov_pages = self.extract_governing_persons_count()
            
        while current_gov_page <= gov_pages:
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            table = soup.find('table', id="grid_principalList")
            table_body = table.find('tbody')
            
            gov_rows = table_body.find_all('tr')

            for row in gov_rows:
                data = row.select('td')
                person_dict = {}
                person_dict['Title'] = data[0].text.strip()
                person_dict['Name'] = data[1].text.strip()
                person_dict['Address'] = data[2].text.strip()
                
                governing_persons.append(GoverningPerson.validate(person_dict))
                self.governing_persons_found+=1
                
            if current_gov_page < gov_pages:
                try:
                    self.browser.find_element("xpath", self.vars.NEXT_BUTTON).click()
                except Exception:
                    pass
                else:
                    current_gov_page+=1
                    sleep(3)
                    self.get_data_from_pannels()
            else:
                break

        return governing_persons

    
    def extract_registered_agent_data(self) -> RegisteredAgent:
        table_data = self.registered_agent_data.find('table')
        rows = table_data.find_all('tr')
        
        for row in rows:
            data = row.select('td')
            if len(data) > 1:
                self.agent_dict[data[0].text.replace(":","").strip()] = data[1].text.strip()
                
        return RegisteredAgent.validate(self.agent_dict)
    
    def extract_business_details_data(self) -> BusinessDetails:
        table_data = self.business_data.find('table')
        all_rows = table_data.find_all('tr')
            
        row_count = 1
        for row in all_rows:
            if row_count != 1:
                row_data = row.select('td')
                for rows_data in row_data:
                    cell_value = str(rows_data.text.strip().replace(":",""))
                    
                    if self.current_item == "":
                        if cell_value in self.vars.BIZ_TITLES:
                            self.current_item = cell_value

                    if self.current_item != "":
                        if self.current_item != cell_value:
                            self.business_dict[self.current_item] = cell_value
                            self.current_item = ""
                    
            row_count+=1
            
        return BusinessDetails.validate(self.business_dict)
    
    def run(self) -> dict:
        self.get_data_from_pannels()
        
        business_details = self.extract_business_details_data()
        
        if self.governing_persons_data != "":
            self.governing_person_names = self.extract_governing_persons_data()
            
        if self.registered_agent_data != "":    
            self.registered_agent = self.extract_registered_agent_data()
            
        return {"Business ID": self.business_dict["Business ID"], "Business Details": Business(business_name=self.business_dict["Business Name"], business_details=business_details, governing_persons=self.governing_person_names, registered_agent=self.registered_agent), "Gov Persons Found": self.governing_persons_found }
            