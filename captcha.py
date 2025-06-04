import re
import os

from time import sleep
from random import randint

from twocaptcha import TwoCaptcha

from twocaptcha.solver import ValidationException
from twocaptcha.api import NetworkException, ApiException
from selenium.common.exceptions import TimeoutException

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup


from dotenv import load_dotenv

load_dotenv()

class Captcha:
    def __init__(self, browser):
        self.SITE_KEY = os.getenv("2CAPTCHA_SITE_KEY")
        self.API_KEY = os.getenv("2CAPTCHA_API_KEY")
        
        if os.getenv("USER_AGENT") != "":
            self.USER_AGENT = os.getenv("USER_AGENT")
        else:
            self.USER_AGENT = ""
        
        self.config = {
                    'server': '2captcha.com',
                    'apiKey': self.API_KEY,
                    'callback': 'https://your.site.com/',
                    'defaultTimeout': 300,
                    'recaptchaTimeout': 600,
                    'pollingInterval': 10,
        }
        
        self.browser = browser
        
        self.solver = TwoCaptcha(**self.config)
        
    def get_balance(self):
        return self.solver.balance()
        
    def is_visible(self):
        try:
            Captcha_Form = self.browser.find_element("xpath","//form[@id='captcha-form']")
            if Captcha_Form.is_displayed():
                return True
            else:
                return False
        except Exception:
            return False
        
    def apply_token(self, token):
        try:
            self.browser.current_driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "{}";'.format(token))
        except Exception as e:
            return("Could not apply token... Exception: "+str(e))
        else:
            return "Token Applied"
    
    def get_id(self, url):
        try:
            result = self.solver.recaptcha(sitekey=self.SITE_KEY, url=url)
            #print(result)
            split_string = str(result).split(":", 1)
            substring = split_string[0]
            #print(substring)
            
            if (substring == "{'captchaId'"):
                strip_beginning = re.sub("{'captchaId': '", "", str(result))
                captcha_id = re.sub("'}", "", strip_beginning)
                return captcha_id
            else:
                print("could not find captcha ID")
                return 0
        except ValidationException as e:
            # invalid parameters passed
          print(e)
          return 0
        except NetworkException as e:
          # network error occurred
          print(e)
          return 0
        except ApiException as e:
          # api respond with error
          print(e)
          return 0
        except TimeoutException as e:
          # captcha is not solved so far
          print(e)
          return 0
      
    def get_response(self, id):
        response_url = "https://2captcha.com/res.php?key="+self.API_KEY+"&action=get&id="+id
        
        while True:
            try:        
                PageRequest = Request(response_url,data=None,headers={'User-Agent': self.USER_AGENT})
                PageResponse = urlopen(PageRequest)
                PageHtml = PageResponse.read()
                PageSoup = BeautifulSoup(PageHtml, 'html.parser')
                SoupText = str(PageSoup)
            except Exception as e:
                print("Could not generate page request for captcha. Exception: "+str(e))
            else:
                if SoupText == "ERROR_CAPTCHA_UNSOLVABLE" or SoupText == "ERROR_WRONG_CAPTCHA_ID" or SoupText == "ERROR_TOKEN_EXPIRED" or SoupText == "ERROR: NNNN" or SoupText == "ERROR_DUPLICATE_REPORT":
                    self.solver.report(id, False)
                    return SoupText
                elif str(PageSoup) == "CAPCHA_NOT_READY":
                    #print("Waiting for capcha response...")
                    rand = randint(1,5)
                    #print("sleeping for "+str(rand)+" seconds")
                    sleep(rand)
                else:
                    split_string = str(PageSoup).split("|", 1)
                    if len(split_string) > 0:
                        substring = split_string[1]
                        #self.solver.report(id, True)
                        return substring
                        break      
        #print(PageSoup)
        return PageSoup
      
    def solve(self):
        while True:
            try:
                captcha_id = self.get_id(self.browser.current_driver.current_url)
            except:
                print("Could not find captcha ID")
                sleep(1)
            else:
                if captcha_id != 0 or captcha_id != None:
                    print("Captcha ID is: "+str(captcha_id))
                    try:
                        cap_res = self.get_response(captcha_id)
                    except:
                        print("Could not get captcha response")
                    else:
                        if cap_res == "ERROR_CAPTCHA_UNSOLVABLE" or cap_res == "ERROR_TOKEN_EXPIRED" or cap_res == "ERROR_WRONG_CAPTCHA_ID":
                            print("Captcha failed... Restarting captcha")
                            self.browser.current_driver.refresh()
                            sleep(1)
                            continue
                        else:
                            print("Capcha Token: "+cap_res)
                            self.apply_token(token=cap_res)
                            print("Token Applied")
                            return True
                else:
                    print("Capcha ID is nothing.....")
                    return 0
