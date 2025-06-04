import os
import zipfile

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from dotenv import load_dotenv

load_dotenv()

class Browser:
    def __init__(self, headless=False, incognito=False):
        self.USE_PROXY = False
        self.PROXY_HOST = os.getenv("PROXY_HOST")
        self.PROXY_USER = os.getenv("PROXY_USER")
        self.PROXY_PASS = os.getenv("PROXY_PASS")
        self.PROXY_PORT = os.getenv("PROXY_PORT")
        
        self.USER_AGENT = os.getenv("USER_AGENT")
        self.CHROME_DRIVER_LOCATION = os.getenv("CHROME_DRIVER_LOCATION")
        
        self.headless = headless
        self.incognito = incognito
        
        self.current_driver = ""
        
    def open_url(self, url):
        if isinstance(self.current_driver, bool):
            self.current_driver = ""
        
        if self.current_driver == "":
            self.current_driver = self.new_chrome_driver()
            
        return self.current_driver.get(url)
    
    def current_url(self):
        return self.current_driver.current_url
        
    def new_chrome_driver(self):
        s = Service(self.CHROME_DRIVER_LOCATION)
        
        if self.USE_PROXY:
            PROXY_URL = self.PROXY_HOST +":"+str(self.PROXY_PORT)
            
            print("Using Proxy: "+PROXY_URL)
        
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """
            
            background_js = """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                    singleProxy: {
                        scheme: "http",
                        host: "%s",
                        port: parseInt(%s)
                    },
                    bypassList: ["localhost"]
                    }
                };
            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }
            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """ % (self.PROXY_HOST, self.PROXY_PORT, self.PROXY_USER, self.PROXY_PASS)
        
        #path = os.path.dirname(os.path.abspath(__file__))
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('--headless')
        if self.USE_PROXY:
            pluginfile = os.getcwd()+'\\proxy-plugins\\'+self.PROXY_HOST+'_proxy_auth_plugin.zip'
    
            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            try:
                chrome_options.add_extension(pluginfile)
                #print("Added Extension")
            except:
                print("Couldn't add plugin to Chrome")
        if self.USER_AGENT!="":
            chrome_options.add_argument('--user-agent=%s' % self.USER_AGENT)
            #print("Added User Agent\n")
        if self.headless:
            chrome_options.add_argument("--headless")
        if self.incognito:
            chrome_options.add_argument("--incognito")
            
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
            
        try:
            driver = webdriver.Chrome(service=s,options=chrome_options)
        except Exception as e:
            print("Could not create driver...")
            print(e)
            return False
        else:
            self.current_driver = driver
            return driver
            
        
def main():
    browser = Browser()
    return browser

if __name__ == '__main__':
    main()
            