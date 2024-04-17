import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver(headless_mode):
    """Setup the Chrome WebDriver with optional headless mode."""
    chrome_options = Options()
    if headless_mode:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36')

    driver = webdriver.Chrome(options=chrome_options)
    return driver

max_pages = int(input("Enter the number of pages to scrape (Enter 0 to scrape all available pages): "))
outputFileName = input("Enter the File Name: ")
browser_mode = input("Enter 'headless' to run the browser in headless mode, or press Enter to run in standard mode: ")
headless_mode = True if browser_mode.lower() == 'headless' else False

driver = setup_driver(headless_mode)  # Setup WebDriver with user's choice for headless mode 
url = "https://www.myntra.com/personal-care"

if max_pages == 0:
    max_pages = float('inf')  # Set to infinity to attempt scraping all pages

try:
    page_number = 1
    while True:
        driver.get(url + f"?p={page_number}")

        try:
            products = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "product-base"))
            )
        except TimeoutException:
            print(f"Error: Products didn't load within the timeout period on page {page_number}.")
            break

        product_data = []
        for product in products:
            try:
                # Initialize dictionary for storing product details
                product_details = {
                    "brand": None,
                    "price": None,
                    "rating": None,
                    "name": None,
                    "actual_price": None,
                    "discounted_price": None,
                    "product_discount_percentage": None,
                    "breadcrumb": None,
                    "product_url": None
                }

                # Extract product details and populate the dictionary
                product_details["brand"] = product.find_element(By.CLASS_NAME, "product-brand").text
                product_details["price"] = product.find_element(By.CLASS_NAME, "product-discountedPrice").text
                product_details["rating"] = product.find_element(By.CLASS_NAME, "product-ratingsContainer").text
                product_details["name"] = product.find_element(By.CLASS_NAME, "product-product").text
                product_details["actual_price"] = product.find_element(By.CLASS_NAME, "product-strike").text
                product_details["discounted_price"] = product.find_element(By.CLASS_NAME, "product-discountedPrice").text
                product_details["product_discount_percentage"] = product.find_element(By.CLASS_NAME, "product-discountPercentage").text
                product_details["breadcrumb"] = driver.find_element(By.CSS_SELECTOR, "span.breadcrumbs-crumb[style='font-size: 14px; margin: 0px;']").text
                product_url_element = product.find_element(By.CSS_SELECTOR, "a[data-refreshpage='true']")
                product_details["product_url"] = product_url_element.get_attribute("href")

                product_data.append(product_details)

            except NoSuchElementException as e:
                missing_field = str(e).split(" ")[-1]
                print(f"Error: {missing_field} not found in the product. Skipping this product.")

        mode = 'a' if os.path.exists(outputFileName + ".csv") else 'w'
        # Write data to CSV after each page
        with open(outputFileName + ".csv", mode, newline='', encoding="utf-8") as csvfile:
            fieldnames = list(product_details.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if mode == 'w':
                writer.writeheader()
            writer.writerows(product_data)

        print(f"Data from page {page_number} successfully saved")
        page_number += 1

        if page_number > max_pages:
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
