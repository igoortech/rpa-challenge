import os
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openpyxl

SELENOID_URL = os.environ.get("SELENOID_URL", "http://192.168.56.101:4444/wd/hub")
HEADLESS = os.environ.get("HEADLESS", "false").lower() == "true"
SITE_URL = "https://rpachallenge.com"
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", ".")
EXCEL_PATH = os.path.join(OUTPUT_DIR, "challenge.xlsx")
SCREENSHOT_PATH = os.path.join(OUTPUT_DIR, "screenshot.png")

FIELD_MAP = {
    "First Name":     "labelFirstName",
    "Last Name":      "labelLastName",
    "Company Name":   "labelCompanyName",
    "Role in Company": "labelRole",
    "Address":        "labelAddress",
    "Email":          "labelEmail",
    "Phone Number":   "labelPhone",
}


def build_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.set_capability("browserName", "chrome")
    options.set_capability("browserVersion", "110.0")
    options.set_capability("selenoid:options", {
        "name": "RPA Challenge",
        "sessionTimeout": "5m",
        "enableVNC": not HEADLESS,
    })
    return webdriver.Remote(command_executor=SELENOID_URL, options=options)


def download_excel(driver):
    link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(., 'Download Excel')]"))
    )
    href = link.get_attribute("href")
    user_agent = driver.execute_script("return navigator.userAgent")
    req = urllib.request.Request(href, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req) as resp:
        with open(EXCEL_PATH, "wb") as f:
            f.write(resp.read())


def read_excel():
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb.active
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if any(v is not None for v in row):
            rows.append(dict(zip(headers, row)))
    return rows


def fill_field(driver, label_text, value):
    # Locate input via its sibling/parent label text
    input_el = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//label[contains(normalize-space(.), '{label_text}')]"
            f"/following-sibling::input | "
            f"//label[contains(normalize-space(.), '{label_text}')]"
            f"/..//input",
        ))
    )
    input_el.clear()
    input_el.send_keys(str(value) if value is not None else "")


def fill_form(driver, row_data):
    for label_text in FIELD_MAP:
        value = row_data.get(label_text, "")
        fill_field(driver, label_text, value)


def submit_form(driver):
    btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit'] | //button[@type='submit']"))
    )
    btn.click()


def main():
    driver = build_driver()
    try:
        driver.get(SITE_URL)

        # Download and read Excel before starting the timer
        download_excel(driver)
        data = read_excel()

        # Start the challenge timer
        start_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Start')]"))
        )
        start_btn.click()

        for row in data:
            fill_form(driver, row)
            submit_form(driver)
            time.sleep(0.3)  # brief pause to let the DOM re-render between rounds

        # Wait for congratulations screen and take screenshot
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".congratulations"))
        )
        driver.save_screenshot(SCREENSHOT_PATH)
        print(f"Done! Screenshot saved to {SCREENSHOT_PATH}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
