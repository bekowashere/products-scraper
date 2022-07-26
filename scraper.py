import json
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


# while=True
# break line :325 [ REMOVE FOR INFINITY LOOP ]
# if j == 31 [ NOW: TOTAL PRODUCTS COUNT 31]

def collect_products():
    driver.get('https://b2b.mercanlar.com/')
    time.sleep(1)

    email_input = driver.find_element(By.ID, 'LoginEmail')
    email_input.send_keys('fatih@turkeyautoparts.com')

    password_input = driver.find_element(By.ID, 'LoginPassword')
    password_input.send_keys('Fatih123')
    password_input.send_keys(Keys.RETURN)

    try:
        search_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'btn-genel-arama'))
        )
        print("Searching is ready!")

        # ORİJİNAL: spare_part_brand
        part_brand_dropdown = driver.find_element(By.ID, 'spare_part_brand')
        select_part_brand = Select(part_brand_dropdown)
        # select_part_brand.select_by_visible_text('ORİJİNAL')
        select_part_brand.select_by_value('ORİJİNAL')
        time.sleep(1)

        # MERCEDES: spare_car_brand_name
        car_brand_dropdown = driver.find_element(By.ID, 'spare_car_brand_name')
        select_car_brand = Select(car_brand_dropdown)
        select_car_brand.select_by_value('MERCEDES')
        time.sleep(1)
        print("MARKA: ORİJİNAL, ARAÇ: MERCEDES")

        search_btn = driver.find_element(By.ID, 'btn-genel-arama')
        search_btn.click()

    except TimeoutException:
        print("Loading took too much time [SEARCH]")

    try:
        # class=col-xs-12 result-container
        products_container = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'result-container'))
        )
        print("Products are ready to collect")

        # class="product-item-wrapper "
        product_items = driver.find_elements(By.CLASS_NAME, 'product-item-wrapper ')
        j = len(product_items)
        print(f'Total products = {j}')

        for product_item in product_items:
            product_item_html = product_item.get_attribute("outerHTML")
            soup = BeautifulSoup(product_item_html, 'html.parser')
            label_names = soup.find_all('label', {'class': 'key'})

            oem_code = ""
            original_code = ""
            spare_part_brand = ""
            recital_no = ""
            description = ""
            rg = ""
            stock_status = []
            currency_price = ""
            gross_lira_price = ""
            net_lira_price = ""
            kdv_net_lira_price = ""

            for label_name in label_names:

                key_value = label_name.get_text()
                if key_value == "Üretici Kodu":
                    oem_code_element = label_name.next_sibling.next_sibling
                    oem_code = oem_code_element.get_text().strip()
                if key_value == "Orijinal Numara":
                    original_code_element = label_name.next_sibling.next_sibling
                    original_code = original_code_element.get_text().strip()
                if key_value == "Marka":
                    spare_part_brand_element = label_name.next_sibling.next_sibling
                    spare_part_brand = spare_part_brand_element.get_text().strip()
                if key_value == "Resital No":
                    recital_no_element = label_name.next_sibling.next_sibling
                    recital_no = recital_no_element.get_text().strip()
                if key_value == "Açıklama":
                    description_element = label_name.next_sibling.next_sibling
                    description = description_element.get_text().strip()
                if key_value == "RG":
                    rg_element = label_name.next_sibling.next_sibling
                    rg = rg_element.get_text().strip()
                if key_value == "Stok Durumu":
                    stock_span_elements = soup.find_all('span', {'class': 'stock-state'})
                    for span_element in stock_span_elements:
                        if span_element.attrs['class'][1] == "in-stock":
                            text_element = span_element.next_sibling
                            location = text_element.get_text().strip()

                            stock = {
                                "status": "in-stock",
                                "location": location
                            }
                            stock_status.append(stock)
                        if span_element.attrs['class'][1] == "critical":
                            text_element = span_element.next_sibling
                            location = text_element.get_text().strip()

                            stock = {
                                "status": "critical",
                                "location": location
                            }
                            stock_status.append(stock)
                        if span_element.attrs['class'][1] == "en-route":
                            text_element = span_element.next_sibling
                            location = text_element.get_text().strip()

                            stock = {
                                "status": "en-route",
                                "location": location
                            }
                            stock_status.append(stock)
                        if span_element.attrs['class'][1] == "ask":
                            text_element = span_element.next_sibling
                            location = text_element.get_text().strip()

                            stock = {
                                "status": "ask",
                                "location": location
                            }
                            stock_status.append(stock)
                        if span_element.attrs['class'][1] == "out-of-stock":
                            text_element = span_element.next_sibling
                            location = text_element.get_text().strip()

                            stock = {
                                "status": "out-of-stock",
                                "location": location
                            }
                            stock_status.append(stock)
                if key_value == "Döviz Fiyatı":
                    currency_price_element = label_name.next_sibling.next_sibling
                    currency_price = currency_price_element.get_text().strip()
                if key_value == "Brüt TL Fiyatı":
                    gross_lira_price_element = label_name.next_sibling.next_sibling
                    gross_lira_price = gross_lira_price_element.get_text().strip()
                if key_value == "Net TL Fiyatı":
                    net_lira_price_element = label_name.next_sibling.next_sibling
                    net_lira_price = net_lira_price_element.get_text().strip()
                if key_value == "KDV Dahil Net Fiyat":
                    kdv_net_lira_price_element = label_name.next_sibling.next_sibling
                    kdv_net_lira_price = kdv_net_lira_price_element.get_text().strip()

            product = {
                "oem_code": oem_code,
                "original_code": original_code,
                "spare_part_brand": spare_part_brand,
                "recital_no": recital_no,
                "description": description,
                "rg": rg,
                "stock_status": stock_status,
                "currency_price": currency_price,
                "gross_lira_price": gross_lira_price,
                "net_lira_price": net_lira_price,
                "kdv_net_lira_price": kdv_net_lira_price
            }

            print(f'{oem_code} added successfully')

            with open('products.json', 'a', encoding="UTF-8") as f:
                json.dump(product, f, indent=2)
                f.write(',\n')
            time.sleep(1)

        try:
            while True:
                load_more_button = driver.find_element(By.CLASS_NAME, 'btn-load-more')
                load_more_button.click()
                print("New products loading..")
                loading_spinner = WebDriverWait(driver, 300).until(
                    EC.invisibility_of_element_located((By.ID, 'loader-wrapper'))
                )
                print("New products loaded")

                new_product_items = driver.find_elements(By.CLASS_NAME, 'product-item-wrapper ')
                newList = new_product_items[j:]
                for prod in newList:
                    prod_item_html = prod.get_attribute("outerHTML")
                    prod_soup = BeautifulSoup(prod_item_html, 'html.parser')
                    labels = prod_soup.find_all('label', {'class': 'key'})

                    _oem_code = ""
                    _original_code = ""
                    _spare_part_brand = ""
                    _recital_no = ""
                    _description = ""
                    _rg = ""
                    _stock_status = []
                    _currency_price = ""
                    _gross_lira_price = ""
                    _net_lira_price = ""
                    _kdv_net_lira_price = ""

                    for label in labels:
                        key = label.get_text()
                        if key == "Üretici Kodu":
                            _oem_code_element = label.next_sibling.next_sibling
                            _oem_code = _oem_code_element.get_text().strip()
                        if key == "Orijinal Numara":
                            _original_code_element = label.next_sibling.next_sibling
                            _original_code = _original_code_element.get_text().strip()
                        if key == "Marka":
                            _spare_part_brand_element = label.next_sibling.next_sibling
                            _spare_part_brand = _spare_part_brand_element.get_text().strip()
                        if key == "Resital No":
                            _recital_no_element = label.next_sibling.next_sibling
                            _recital_no = _recital_no_element.get_text().strip()
                        if key == "Açıklama":
                            _description_element = label.next_sibling.next_sibling
                            _description = _description_element.get_text().strip()
                        if key == "RG":
                            _rg_element = label.next_sibling.next_sibling
                            _rg = _rg_element.get_text().strip()
                        if key == "Stok Durumu":
                            _stock_span_elements = prod_soup.find_all('span', {'class': 'stock-state'})
                            for _span_element in _stock_span_elements:
                                if _span_element.attrs['class'][1] == "in-stock":
                                    _text_element = _span_element.next_sibling
                                    _location = _text_element.get_text().strip()

                                    _stock = {
                                        "status": "in-stock",
                                        "location": _location
                                    }
                                    _stock_status.append(_stock)
                                if _span_element.attrs['class'][1] == "critical":
                                    _text_element = _span_element.next_sibling
                                    _location = _text_element.get_text().strip()

                                    _stock = {
                                        "status": "critical",
                                        "location": _location
                                    }
                                    _stock_status.append(_stock)
                                if _span_element.attrs['class'][1] == "en-route":
                                    _text_element = _span_element.next_sibling
                                    _location = _text_element.get_text().strip()

                                    _stock = {
                                        "status": "en-route",
                                        "location": _location
                                    }
                                    _stock_status.append(_stock)
                                if _span_element.attrs['class'][1] == "ask":
                                    _text_element = _span_element.next_sibling
                                    _location = _text_element.get_text().strip()

                                    _stock = {
                                        "status": "ask",
                                        "location": _location
                                    }
                                    _stock_status.append(_stock)
                                if _span_element.attrs['class'][1] == "out-of-stock":
                                    _text_element = _span_element.next_sibling
                                    _location = _text_element.get_text().strip()

                                    _stock = {
                                        "status": "out-of-stock",
                                        "location": _location
                                    }
                                    _stock_status.append(_stock)
                        if key == "Döviz Fiyatı":
                            _currency_price_element = label.next_sibling.next_sibling
                            _currency_price = _currency_price_element.get_text().strip()
                        if key == "Brüt TL Fiyatı":
                            _gross_lira_price_element = label.next_sibling.next_sibling
                            _gross_lira_price = _gross_lira_price_element.get_text().strip()
                        if key == "Net TL Fiyatı":
                            _net_lira_price_element = label.next_sibling.next_sibling
                            _net_lira_price = _net_lira_price_element.get_text().strip()
                        if key == "KDV Dahil Net Fiyat":
                            _kdv_net_lira_price_element = label.next_sibling.next_sibling
                            _kdv_net_lira_price = _kdv_net_lira_price_element.get_text().strip()

                    product = {
                        "oem_code": _oem_code,
                        "original_code": _original_code,
                        "spare_part_brand": _spare_part_brand,
                        "recital_no": _recital_no,
                        "description": _description,
                        "rg": _rg,
                        "stock_status": _stock_status,
                        "currency_price": _currency_price,
                        "gross_lira_price": _gross_lira_price,
                        "net_lira_price": _net_lira_price,
                        "kdv_net_lira_price": _kdv_net_lira_price
                    }

                    print(f'{_oem_code} added successfully')

                    with open('products.json', 'a', encoding="UTF-8") as f:
                        json.dump(product, f, indent=2)
                        f.write(',\n')
                    time.sleep(1)

                j = len(new_product_items) + 1
                print(f'Total products = {j}')
                if j == 31:
                    break
        except StaleElementReferenceException:
            print("Load More Error [LOAD-WHILE]")

    except TimeoutException:
        print("Loading took too much time [RESULTS]")


collect_products()
