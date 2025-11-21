from appium import webdriver
import time

userName = "vishnu_REc56X"
accessKey = "sGPmYVj9tm4BEiCUicso"

desired_cap = {
    "platformName": "android",
    "deviceName": "Samsung Galaxy S23",          # You can change device
    "os_version": "13.0",

    # --- BrowserStack Required Caps ---
    "project": "My Python Appium Project",
    "build": "Python Appium Build",
    "name": "Live Test Run",                      # This name appears in dashboard

    # --- ENABLE LIVE VIDEO ---
    "browserstack.debug": True,                   # Enable Visual Logs
    "browserstack.video": True,                   # Enable Live Video
    "browserstack.networkLogs": True,             # Enable Network Logs
    "browserstack.console": "verbose",            # Enable Console logs

    # --- App under test ---
    "app": "bs://01bec48166b705369e4c838452133588cf42d3ff",
}

driver = webdriver.Remote(
    command_executor=f"http://{userName}:{accessKey}@hub.browserstack.com/wd/hub",
    desired_capabilities=desired_cap
)

print("Test started... You can watch it live on BrowserStack Dashboard.")

try:
    time.sleep(5)

    # Example:
    # driver.find_element(By.ID, "com.example:id/username").send_keys("test")

    print("Running actions...")
    time.sleep(10)

finally:
    driver.quit()
    print("Test finished.")
