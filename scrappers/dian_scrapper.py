import time
from random import randint
from typing import Dict, List

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from models import DianInvoice

DIAN_URL = 'https://catalogo-vpfe.dian.gov.co/User/SearchDocument'


class DianScrapper:

    def __init__(self):
        self.invoices_data = []

    def get_dian_invoices(self, invoice_ids: list[str]) -> List[Dict[str, str]]:
        self.driver = webdriver.Chrome()

        self.driver.get(DIAN_URL)

        for invoice_id in invoice_ids:
            self.get_window_information(invoice_id)
        self.driver.quit()
        return self.invoices_data

    def get_element(self, by: str, value: str) -> (WebElement | None):
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            return None

    def get_window_information(self, invoice_id: str):
        cufe_input = self.get_element(By.ID, "DocumentKey")
        search_button = self.get_element(By.CLASS_NAME, "search-document")
        if not cufe_input or not search_button:
            return
        cufe_input.clear()
        cufe_input.send_keys(invoice_id)
        time.sleep(randint(40, 100) / 100)
        search_button.click()
        found_error = False
        if invoice_id not in self.driver.current_url:
            time.sleep(randint(40, 100) / 100)
            search_button = self.get_element(By.CLASS_NAME, "search-document")
            search_button.click()
            if invoice_id not in self.driver.current_url:
                found_error = True
        if found_error:
            return
        divs_with_with_details = self.driver.find_elements(By.CLASS_NAME, "row-fe-details")
        invoice_raw_details = " ".join([div.text for div in divs_with_with_details])
        invoice_data = self.parse_details(invoice_raw_details)
        self.invoices_data.append(invoice_data)
        invoice_data['cufe'] = invoice_id
        invoice_data['link_graphic_representation'] = self.driver.current_url
        self.driver.back()

    @staticmethod
    def parse_details(raw_details: str) -> Dict[str, str | dict]:
        raw_details = raw_details.replace("Descargar PDF ", "")
        content_lines = raw_details.split("\n")
        result = {}
        current_entity_information = ""
        for line in content_lines:
            split_line = line.split(": ")
            if len(split_line) == 1:
                if line == "DATOS DEL EMISOR":
                    current_entity_information = "seller_information"
                    result[current_entity_information] = {}
                if line == "DATOS DEL RECEPTOR":
                    current_entity_information = "receiver_information"
                    result[current_entity_information] = {}

            if len(split_line) == 2:
                if split_line[0] in ["NIT", "Nombre"]:
                    if isinstance(result.get(current_entity_information), dict):
                        result[current_entity_information][split_line[0]] = split_line[1].strip()
                else:
                    result[split_line[0]] = split_line[1].strip()
        return result
