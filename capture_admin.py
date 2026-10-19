from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=1400,950')
driver = webdriver.Chrome(options=options)

try:
    driver.get('http://127.0.0.1:5000/admin')
    time.sleep(1)

    # Use correct gate-passkey id
    inp = driver.find_element(By.ID, 'gate-passkey')
    inp.clear()
    inp.send_keys('Rovic1925#')
    driver.find_element(By.ID, 'btn-submit-gate').click()
    time.sleep(3)

    driver.save_screenshot(r'C:\Users\Lorenz\.gemini\antigravity-ide\brain\df7c23d3-d007-476d-95bd-fc28a95b58fd\localhost_admin_main.png')

    # Switch to keys tab
    driver.execute_script("""
        const keyTab = document.getElementById('nav-keys') || Array.from(document.querySelectorAll('.admin-nav-item, button, a')).find(el => el.textContent.trim().toLowerCase().includes('keys') || el.textContent.trim().toLowerCase().includes('inventory'));
        if (keyTab) keyTab.click();
    """)
    time.sleep(2)

    # Check a box to show batch action bar
    boxes = driver.find_elements(By.CSS_SELECTOR, '.key-checkbox')
    if boxes:
        boxes[0].click()
        time.sleep(1)

    driver.save_screenshot(r'C:\Users\Lorenz\.gemini\antigravity-ide\brain\df7c23d3-d007-476d-95bd-fc28a95b58fd\localhost_admin_keys.png')
    print('Both admin screenshots successfully saved!')
finally:
    driver.quit()
