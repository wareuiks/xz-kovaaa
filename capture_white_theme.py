from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=1400,950')
driver = webdriver.Chrome(options=options)

try:
    # 1. Login view
    driver.get('http://127.0.0.1:5000/login')
    time.sleep(1)
    driver.save_screenshot(r'C:\Users\Lorenz\.gemini\antigravity-ide\brain\df7c23d3-d007-476d-95bd-fc28a95b58fd\white_login_preview.png')

    # 2. Admin gate & main
    driver.get('http://127.0.0.1:5000/admin')
    time.sleep(1)
    inp = driver.find_element(By.ID, 'gate-passkey')
    inp.clear()
    inp.send_keys('Rovic1925#')
    driver.find_element(By.ID, 'btn-submit-gate').click()
    time.sleep(3)
    driver.save_screenshot(r'C:\Users\Lorenz\.gemini\antigravity-ide\brain\df7c23d3-d007-476d-95bd-fc28a95b58fd\white_admin_main.png')

    # 3. Keys tab
    boxes = driver.find_elements(By.CSS_SELECTOR, '.key-checkbox')
    if boxes:
        boxes[0].click()
        time.sleep(1)
    driver.save_screenshot(r'C:\Users\Lorenz\.gemini\antigravity-ide\brain\df7c23d3-d007-476d-95bd-fc28a95b58fd\white_admin_keys.png')

    # 4. User Dashboard
    driver.get('http://127.0.0.1:5000/dashboard')
    time.sleep(2)
    driver.save_screenshot(r'C:\Users\Lorenz\.gemini\antigravity-ide\brain\df7c23d3-d007-476d-95bd-fc28a95b58fd\white_dashboard_preview.png')

    print('Captured all white-theme screenshots!')
finally:
    driver.quit()
