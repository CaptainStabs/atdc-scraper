# %%
import requests
import pandas as pd

# %%
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import urllib

class WebDriver:
    def __init__(self):
        self.options = Options()
        # self.options.add_argument('--headless')
        # self.options.add_argument('--no-sandbox')
        # self.options.headless = True  
        # self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("start-maximized")
        self.driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=self.options)

        

    def fetch_event_times(self, url):
        try:
            self.driver.get("https://portal.atdc.org/" + url)
            
            wait = WebDriverWait(self.driver, 15)
            element = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="event-navbar"]/div[1]/div[2]/div[1]/div[2]/div[2]/span/ul/li[4]/a'
            )))

            href = element.get_attribute('href')
            
            ics = urllib.parse.unquote(href.split('/')[-1])
            ics = ics.replace("&", '\n').replace("%20", " ")

            start_match = re.search(r'startdt=(.+)', ics)
            end_match = re.search(r'enddt=(.+)', ics)

            startdt = start_match.group(1) if start_match else None
            enddt = end_match.group(1) if end_match else None

            meta = self.driver.find_element(By.XPATH, '//*[@id="event-navbar"]/div[1]/div[2]/div[1]/div[2]/div[1]/div/span').text

            return startdt, enddt, meta
        except Exception as e:
            print(f"Error with URL: {url}\n{e}")
            return None, None


    def close(self):
        self.driver.quit()
  

scraper = WebDriver()

tqdm.pandas()

df = pd.read_csv('events_no_ics.csv')
df[['startdt', 'enddt', 'meta']] = df['url'].progress_apply(
    lambda url: pd.Series(scraper.fetch_event_times(url) or (None, None, None))
)
df.to_csv('events_final.csv', index=False)


scraper.close()


