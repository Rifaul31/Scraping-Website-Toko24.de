import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
PATH = "C:\Program Files (x86)\chromedriver.exe"

# Selenium Options
options = Options()
options.headless = True
options.add_argument("--windows-size=1920,1080")

# Install Driver
driver = webdriver.Chrome(options = options, executable_path = PATH)

url = "https://toko24.de/lebensmittel/" # The food section in toko24.de

def scrollDownPage(driver):
    #Scroll Down Page
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Accessing the Website and Getting the HTML File
def getPage(url, driver):
    driver.get(url) 
    
    scrollDownPage(driver)
    while True:
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'Weitere Artikel laden'))
            ).click()
            scrollDownPage(driver)
        except:
            print("No More Pages Left")
            break

    soup = BeautifulSoup((driver.page_source).encode('utf-8'), 'lxml')
    driver.quit()
    return soup

# Scraping Item Category type
def getProductCategory(soup):
    product_category = soup.find('li', class_='navigation--entry is--active has--sub-categories has--sub-children')
    product_category = product_category.find_all('li', role='menuitem')
    for product in product_category:
        print(product.a.text)

# Scraping Individual Product Info
def GetProductInfo(soup):
    product_name = []
    product_price = []
    product_details = []
    product_info = soup.find('div', class_='listing')
    product_info = product_info.find_all('div', class_='product--info')
    for product in product_info:
        # a_tag = product_info.find_all('a', class_'product--title')
        product_name.append(product.find('a', class_='product--title')['title'])
        product_price.append(product.find('div', class_='product--price').span.text.split()[0]) # Split is added to remove the unreadable euro symbol
        product_details.append(product.find('div', class_='price--unit')['title'])

    return (product_name, product_price, product_details)

soup = getPage(url, driver)
product_name, product_price, product_details = GetProductInfo(soup)

scraped_data = pd.DataFrame({'Name': product_name, 'Price (in Euros)': product_price, 'Details': product_details})
scraped_data.to_csv(("Foods Product.csv"))
