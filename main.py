from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from time import sleep
import os
from selenium.common.exceptions import NoSuchElementException

responses_url = os.environ.get('responses')
google_form_url = 'https://forms.gle/4nQjYwNeHqJHcRU5A'
zillow_url = 'https://www.zillow.com/homes/for_rent/1-_beds/' \
             '?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3Anull' \
             '%2C%22mapBounds%22%3A%7B%22west%22%3A-122.56276167822266%2C%22east%22%3A-122.30389632177734' \
             '%2C%22south%22%3A37.69261345230467%2C%22north%22%3A37.857877098316834%7D%2C%22isMapVisible%22' \
             '%3Atrue%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B' \
             '%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value' \
             '%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse' \
             '%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf' \
             '%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22price%22%3A%7B%22max' \
             '%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%7D%2C%22isListVisible%22%3Atrue%2C' \
             '%22mapZoom%22%3A12%7D'


def get_data_from_zillow():

    BROWSER_HEADER = {
        "Accept-Language": "en-US",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    }

    response = requests.get(url=zillow_url, headers=BROWSER_HEADER)
    response.raise_for_status()
    raw_data = response.text

    soup = BeautifulSoup(raw_data, 'html.parser')
    addresses = soup.find_all(name='address', class_='list-card-addr')
    prices = soup.find_all(name='div', class_='list-card-price')
    links = soup.find_all(name='a', class_='list-card-img')
    address_list = [address.getText() for address in addresses]
    price_list = [price.getText() for price in prices]
    link_list = [link.get('href') for link in links]

    for i in range(len(link_list)):
        if 'http' not in link_list[i]:
            link_list[i] = 'https://www.zillow.com' + link_list[i]

    return address_list, price_list, link_list


def fill_google_form(addresses: list, prices: list, links: list):
    chrome_driver = '/Users/mukulperiwal/Downloads/chromedriver'
    driver = webdriver.Chrome(executable_path=chrome_driver)

    driver.get(google_form_url)

    for i in range(len(addresses)):
        try:
            submit_another_response = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div/div[4]/a')
        except NoSuchElementException:
            pass
        else:
            submit_another_response.click()
            sleep(3)

        address = driver.find_element_by_xpath('//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]'
                                               '/div/div[1]/div/div[1]/input')
        address.send_keys(addresses[i])

        price = driver.find_element_by_xpath('//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]'
                                             '/div/div[1]/div/div[1]/input')
        price.send_keys(prices[i])

        link = driver.find_element_by_xpath('//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]'
                                            '/div/div[1]/div/div[1]/input')
        link.send_keys(links[i])

        submit = driver.find_element_by_xpath('//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div/div')
        submit.click()

        sleep(3)

    driver.quit()


def responses_to_excel():
    chrome_driver = '/Users/mukulperiwal/Downloads/chromedriver'
    driver = webdriver.Chrome(executable_path=chrome_driver)

    driver.get(responses_url)

    create_spreadsheet = driver.find_element_by_xpath('//*[@id="ResponsesView"]/div/div[1]/div[1]/div[2]/div[1]/div/div'
                                                      )
    create_spreadsheet.click()


addresses, prices, links = get_data_from_zillow()
fill_google_form(addresses, prices, links)
responses_to_excel()
