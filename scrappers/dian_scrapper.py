import time
import logging
from random import uniform
from typing import Dict, List

from fastapi import HTTPException
from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException, SessionNotCreatedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from schemas import DianEntitySh, DianEventSh, DianInvoiceSh
logger = logging.getLogger(__name__)

DIAN_URL = 'https://catalogo-vpfe.dian.gov.co/User/SearchDocument'
NUMBER_OF_RETRIES = 8


class DianScrapper:

    def __init__(self):
        self.invoices_data = []

    def get_dian_invoices(self, invoice_ids: list[str]) -> List[Dict[str, str | dict]]:
        if not invoice_ids:
            return []

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get(DIAN_URL)
            logger.info("Chrome driver started")
        except (WebDriverException, SessionNotCreatedException) as e:
            logger.error("Chrome driver failed")
            raise HTTPException(status_code=404, detail=str(e))

        for invoice_id in invoice_ids:
            self.get_window_information(invoice_id)
        self.driver.quit()
        return self.invoices_data

    def get_web_information_as_schemas(self, web_dian_invoices) -> Dict[str, DianInvoiceSh]:
        #TODO: review duplication
        dian_invoices = {}
        for scrapper_invoice in web_dian_invoices:
            seller_information = DianEntitySh(
                document=scrapper_invoice.get("seller_information", {}).get("NIT"),
                name=scrapper_invoice.get("seller_information", {}).get("Nombre")
            )

            receiver_information = DianEntitySh(
                document=scrapper_invoice.get("receiver_information", {}).get("NIT"),
                name=scrapper_invoice.get("receiver_information", {}).get("Nombre")
            )

            events = [
                DianEventSh(
                    eventNumber=event.get("code", ""),
                    eventName=event.get("description", "")
                ) for event in scrapper_invoice["events"]
            ]

            dian_invoices[scrapper_invoice["CUFE"]] = DianInvoiceSh(
                events=events,
                seller_information=seller_information,
                receiver_information=receiver_information,
                link_graphic_representation=scrapper_invoice["link_graphic_representation"]
            )
        return dian_invoices

    def get_element(self, by: str, value: str) -> (WebElement | None):
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            return None

    def get_window_information(self, invoice_id: str):
        logger.info("Searching invoice information")
        found_error = False
        for i in range(NUMBER_OF_RETRIES):
            cufe_input = self.get_element(By.ID, "DocumentKey")
            search_button = self.get_element(By.CLASS_NAME, "search-document")
            if not cufe_input or not search_button:
                return

            cufe_input.clear()
            cufe_input.send_keys(invoice_id)
            time.sleep(uniform(1, 5))
            search_button.click()
            if invoice_id in self.driver.current_url:
                found_error = False
                break
            found_error = True
            failed_reason = "unknown"
            error_div = self.get_element(By.CLASS_NAME, "field-validation-error")
            if error_div:
                failed_reason = error_div.text

            logger.error(f"Try {i+1}: Invoice search error, reason: {failed_reason}")
            time.sleep(uniform(1, 5))

        if found_error:
            logger.error(f"Could not get invoice information: {invoice_id}")
            return
        logger.info(f"Getting invoice information {invoice_id}")
        divs_with_with_details = self.driver.find_elements(By.CLASS_NAME, "row-fe-details")
        invoice_raw_details = " ".join([div.text for div in divs_with_with_details])
        invoice_data = self.parse_details(invoice_raw_details)
        invoice_events = self.get_invoice_events(self.get_element(By.ID, "container1"))
        pdf_link = self.get_element(By.CLASS_NAME, "downloadPDFUrl")
        self.invoices_data.append(invoice_data)
        invoice_data['cufe'] = invoice_id
        invoice_data['link_graphic_representation'] = pdf_link.get_attribute('href')
        invoice_data['events'] = invoice_events
        self.driver.get(DIAN_URL)

    def get_invoice_events(self, events_container) -> List[Dict]:
        events = []
        if not events_container:
            return events

        table_body = events_container.find_element(By.TAG_NAME, "tbody")
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if not len(columns) >= 3:
                break
            event = {
                "code": str(columns[0].text),
                "description": str(columns[1].text),
                "date": str(columns[2].text)
            }
            events.append(event)
        return events

    @staticmethod
    def parse_details(raw_details: str) -> Dict[str, str | dict | list]:
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
