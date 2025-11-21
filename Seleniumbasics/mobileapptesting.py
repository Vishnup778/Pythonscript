# Final full automation script: TC01 -> TC12
# Uses the locators you provided (Select Type, single Date EditText, remark EditText instance(2), Submit accessibility id)
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from appium.options.android import UiAutomator2Options
import time

# ========== CONFIG ==========
PIN = "1111"
DATE_VALUE = "10/08/2025"       # mm/dd/yyyy
PAST_DATE = "01/01/2020"        # for past-date test
WRONG_DATE = "2025/10/08"       # wrong format
FROM_HOUR = "10"
FROM_MINUTE = "45"
TO_HOUR = "12"
TO_MINUTE = "30"
HALF_FROM_HOUR = "09"
HALF_FROM_MIN = "00"
HALF_TO_HOUR = "13"
HALF_TO_MIN = "00"
INVALID_FROM_HOUR = "23"
INVALID_TO_HOUR = "08"
LEAVE_FULL = "Full Day"
LEAVE_HALF = "Half Day"
REMARK_TEXT = "Automation Test"
REMARK_SPECIAL = "Emoji 😊 & <>!@#"
REPEAT_DATE = DATE_VALUE

# ========== DRIVER SETUP ==========
options = UiAutomator2Options().load_capabilities({
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "MEmu",
    "appium:udid": "127.0.0.1:21503",
    "appium:appPackage": "com.zeta.zeta_ess",
    "appium:appActivity": ".MainActivity",
    "appium:noReset": True
})

driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", options=options)
wait = WebDriverWait(driver, 20)
driver.implicitly_wait(2)

results = {}  # store PASS/FAIL/SKIPPED/ERROR per TC

def log(msg):
    print(f"\n>>> {msg}")

def safe_click(locator, timeout=12):
    try:
        wait.until(EC.element_to_be_clickable(locator)).click()
        return True
    except Exception as e:
        print(f"   ⚠️ could not click {locator}: {e}")
        return False

def safe_find(locator, timeout=8):
    try:
        return wait.until(EC.presence_of_element_located(locator))
    except TimeoutException:
        return None

def exists(locator, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
        return True
    except TimeoutException:
        return False

def enter_pin(pin):
    el = safe_find((AppiumBy.CLASS_NAME, "android.widget.EditText"), timeout=10)
    if not el:
        return False
    try:
        el.click()
        el.clear()
        el.send_keys(pin)
        return True
    except Exception as e:
        print("   ⚠️ pin entry failed:", e)
        return False

def navigate_to_creation():
    # Self Services -> Leave -> LieuDay Request -> plus button (instance(1))
    if not safe_click((AppiumBy.ACCESSIBILITY_ID, "Self Services")):
        return False
    if not safe_click((AppiumBy.ACCESSIBILITY_ID, "Leave")):
        return False
    if not safe_click((AppiumBy.ACCESSIBILITY_ID, "LieuDay Request")):
        return False
    plus_locator = (AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().className("android.widget.Button").instance(1)')
    if not safe_click(plus_locator):
        return False
    # verify presence of Submit
    return exists((AppiumBy.ACCESSIBILITY_ID, "Submit"), timeout=8)

def set_date(date_str):
    # open date control then edit and set date
    if not safe_click((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.view.View").instance(8)')):
        return False
    if not safe_click((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.Button").instance(0)')):
        return False
    date_input = safe_find((AppiumBy.CLASS_NAME, "android.widget.EditText"))
    if not date_input:
        print("   ⚠️ date input not found")
        return False
    try:
        date_input.clear()
        date_input.send_keys(date_str)
    except Exception as e:
        print("   ⚠️ failed to enter date:", e)
        return False
    safe_click((AppiumBy.ACCESSIBILITY_ID, "OK"))
    return True

def set_time(instance_index, hour, minute, period):
    # open time edit by EditText instance index (0=From,1=To)
    if not safe_click((AppiumBy.ANDROID_UIAUTOMATOR,
                       f'new UiSelector().className("android.widget.EditText").instance({instance_index})')):
        return False
    if not safe_click((AppiumBy.ANDROID_UIAUTOMATOR,
                       'new UiSelector().className("android.widget.Button").instance(0)')):
        return False
    time_fields = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
    if len(time_fields) < 2:
        print("   ⚠️ time fields not found")
        return False
    try:
        time_fields[0].click(); time_fields[0].clear(); time_fields[0].send_keys(hour)
        time_fields[1].click(); time_fields[1].clear(); time_fields[1].send_keys(minute)
    except Exception as e:
        print("   ⚠️ error setting time:", e)
        return False
    safe_click((AppiumBy.ACCESSIBILITY_ID, period))
    safe_click((AppiumBy.ACCESSIBILITY_ID, "OK"))
    return True

def select_leave_type(leave_type_text):
    # Select Type uses accessibility id "Select Type"
    if not safe_click((AppiumBy.ACCESSIBILITY_ID, "Select Type")):
        return False
    # click exact option text (we use UiSelector text search)
    return safe_click((AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{leave_type_text}")'))

def enter_remark(text):
    # Use the locator you provided: EditText instance(2)
    try:
        remark = wait.until(EC.presence_of_element_located(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText").instance(2)')))
    except TimeoutException:
        print("   ⚠️ remark field not found")
        return False
    try:
        remark.click()
        remark.clear()
        remark.send_keys(text)
        return True
    except Exception as e:
        print("   ⚠️ failed to fill remark:", e)
        return False

def submit_and_handle_popup(expect_success=True, timeout=8):
    # Submit button accessibility id = "Submit"
    safe_click((AppiumBy.ACCESSIBILITY_ID, "Submit"))
    if expect_success:
        if exists((AppiumBy.ACCESSIBILITY_ID, "Saved Successfully"), timeout=timeout):
            print("   ✅ Found 'Saved Successfully' popup")
            safe_click((AppiumBy.ACCESSIBILITY_ID, "OK"))
            # After OK app goes to listing screen per your confirmation
            return True
        else:
            print("   ❌ Success popup not found")
            return False
    else:
        # Expect no success popup (validation expected)
        if exists((AppiumBy.ACCESSIBILITY_ID, "Saved Successfully"), timeout=timeout):
            print("   ❌ Unexpected success popup found")
            safe_click((AppiumBy.ACCESSIBILITY_ID, "OK"))
            return False
        else:
            print("   ✅ No success popup (expected)")
            return True

def cancel_and_back():
    # try Cancel accessibility id, else fallback to Android back
    if safe_click((AppiumBy.ACCESSIBILITY_ID, "Cancel")):
        return True
    try:
        driver.back()
        return True
    except Exception:
        return False

def find_in_listing_by_date(date_text, timeout=8):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{date_text}")')
            )
        )
        return True
    except TimeoutException:
        return False

# ================= START TESTS =================
log("START: Enter PIN")
if enter_pin(PIN):
    log("PIN entered")
else:
    log("PIN entry failed - aborting")
    driver.quit()
    raise SystemExit(1)

# TC01
tc = "TC01_Open_Creation"
try:
    log(tc + ": navigate to creation page")
    ok = navigate_to_creation()
    results[tc] = "PASS" if ok else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# TC02
tc = "TC02_Empty_Submit_Validation"
try:
    log(tc + ": press Submit with empty form")
    if not exists((AppiumBy.ACCESSIBILITY_ID, "Submit"), timeout=3):
        navigate_to_creation()
    ok = submit_and_handle_popup(expect_success=False)
    results[tc] = "PASS" if ok else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# Dismiss any leftover OK if present
if exists((AppiumBy.ACCESSIBILITY_ID, "OK"), timeout=2):
    safe_click((AppiumBy.ACCESSIBILITY_ID, "OK"))

# TC03 Full Day submit
tc = "TC03_FullDay_Submit"
try:
    log(tc + ": fill full day request and submit")
    navigate_to_creation()
    set_date(DATE_VALUE)
    set_time(0, FROM_HOUR, FROM_MINUTE, "AM")
    set_time(1, TO_HOUR, TO_MINUTE, "PM")
    select_leave_type(LEAVE_FULL)
    enter_remark(REMARK_TEXT)
    ok = submit_and_handle_popup(expect_success=True)
    results[tc] = "PASS" if ok else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# TC04 Half Day submit (both times required)
tc = "TC04_HalfDay_Submit"
try:
    log(tc + ": fill half day and submit (both times required)")
    navigate_to_creation()
    set_date(DATE_VALUE)
    set_time(0, HALF_FROM_HOUR, HALF_FROM_MIN, "AM")
    set_time(1, HALF_TO_HOUR, HALF_TO_MIN, "PM")
    select_leave_type(LEAVE_HALF)
    enter_remark(REMARK_TEXT)
    ok = submit_and_handle_popup(expect_success=True)
    results[tc] = "PASS" if ok else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# TC05 Invalid time range
tc = "TC05_Invalid_Time_Range"
try:
    log(tc + ": From > To should be invalid")
    navigate_to_creation()
    set_date(DATE_VALUE)
    set_time(0, INVALID_FROM_HOUR, "00", "PM")
    set_time(1, INVALID_TO_HOUR, "00", "AM")
    select_leave_type(LEAVE_FULL)
    enter_remark(REMARK_TEXT)
    ok = submit_and_handle_popup(expect_success=False)
    results[tc] = "PASS" if ok else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# TC06 Wrong date format
tc = "TC06_Date_Format_Validation"
try:
    log(tc + ": should reject wrong date format")
    navigate_to_creation()
    set_date(WRONG_DATE)
    set_time(0, FROM_HOUR, FROM_MINUTE, "AM")
    set_time(1, TO_HOUR, TO_MINUTE, "PM")
    select_leave_type(LEAVE_FULL)
    enter_remark(REMARK_TEXT)
    ok = submit_and_handle_popup(expect_success=False)
    results[tc] = "PASS" if ok else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# TC07 Past date
tc = "TC07_Past_Date_Validation"
try:
    log(tc + ": should reject past date")
    navigate_to_creation()
    set_date(PAST_DATE)
    set_time(0, FROM_HOUR, FROM_MINUTE, "AM")
    set_time(1, TO_HOUR, TO_MINUTE, "PM")
    select_leave_type(LEAVE_FULL)
    enter_remark(REMARK_TEXT)
    ok = submit_and_handle_popup(expect_success=False)
    results[tc] = "PASS" if ok else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# TC08 Special characters in remarks
tc = "TC08_Special_Chars_Remarks"
try:
    log(tc + ": special characters in remarks")
    navigate_to_creation()
    set_date(DATE_VALUE)
    set_time(0, FROM_HOUR, FROM_MINUTE, "AM")
    set_time(1, TO_HOUR, TO_MINUTE, "PM")
    select_leave_type(LEAVE_FULL)
    enter_remark(REMARK_SPECIAL)
    ok = submit_and_handle_popup(expect_success=True)
    results[tc] = "PASS" if ok else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# TC09 Cancel/back behavior
tc = "TC09_Cancel_Button"
try:
    log(tc + ": cancel should go back without saving")
    navigate_to_creation()
    set_date(DATE_VALUE)
    canceled = cancel_and_back()
    still_on_form = exists((AppiumBy.ACCESSIBILITY_ID, "Submit"), timeout=3)
    results[tc] = "PASS" if canceled and not still_on_form else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# TC10 Duplicate request
tc = "TC10_Duplicate_Request"
try:
    log(tc + ": duplicate request check")
    navigate_to_creation()
    set_date(REPEAT_DATE)
    set_time(0, FROM_HOUR, FROM_MINUTE, "AM")
    set_time(1, TO_HOUR, TO_MINUTE, "PM")
    select_leave_type(LEAVE_FULL)
    enter_remark(REMARK_TEXT)
    ok = submit_and_handle_popup(expect_success=False)
    results[tc] = "PASS" if ok else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# TC11 Logout and re-login persistence
tc = "TC11_Logout_ReLogin_Persistence"
try:
    log(tc + ": logout & re-login to check listing persistence")
    if safe_click((AppiumBy.ACCESSIBILITY_ID, "Logout")):
        time.sleep(2)
        if enter_pin(PIN):
            # open listing
            safe_click((AppiumBy.ACCESSIBILITY_ID, "Self Services"))
            safe_click((AppiumBy.ACCESSIBILITY_ID, "Leave"))
            safe_click((AppiumBy.ACCESSIBILITY_ID, "LieuDay Request"))
            found = find_in_listing_by_date(REPEAT_DATE)
            results[tc] = "PASS" if found else "FAIL"
        else:
            results[tc] = "SKIPPED - relogin failed"
    else:
        results[tc] = "SKIPPED - logout not found"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# TC12 Verify listing shows saved record
tc = "TC12_Verify_List_Shows_Saved_Record"
try:
    log(tc + ": verify listing contains a recently saved record")
    safe_click((AppiumBy.ACCESSIBILITY_ID, "Self Services"))
    safe_click((AppiumBy.ACCESSIBILITY_ID, "Leave"))
    safe_click((AppiumBy.ACCESSIBILITY_ID, "LieuDay Request"))
    found = find_in_listing_by_date(DATE_VALUE)
    results[tc] = "PASS" if found else "FAIL"
    print(f"   {tc} -> {results[tc]}")
except Exception as e:
    results[tc] = f"ERROR: {e}"
    print(e)

# ========== SUMMARY ==========
log("TESTS COMPLETE - SUMMARY")
for k, v in results.items():
    print(f" - {k}: {v}")

print("\nClosing app in 3 seconds...")
time.sleep(3)
driver.quit()
print("Done. Goodbye!")
