from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('file:///C:/Users/BENSSID/Documents/Site Math info/test_pyscript.html')
    time.sleep(5)  # Wait for PyScript to load
    editor_html = page.evaluate('document.querySelector(".py-editor") ? document.querySelector(".py-editor").outerHTML : "Not found"')
    print("--- EDITOR HTML ---")
    print(editor_html)
    browser.close()
