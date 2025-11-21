import threading
import csv
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

# -----------------------------
# CONFIGURATION
# -----------------------------
CHATBOT_URL = "http://192.168.0.56:5000/"
EDGE_DRIVER_PATH = r"D:\PythonSeleniumproject\PythonProject\Seleniumbasics\drivers\msedgedriver.exe"

TOTAL_USERS = 100
MESSAGES_PER_USER = 10
TEST_DURATION_SECONDS = 1800  # 30 min
MIN_DELAY = 120  # 2 mins
MAX_DELAY = 240  # 4 mins

MESSAGE_LIST = [
    "hi",
    "how are you",
    "tell me a joke",
    "what is hr policy",
    "who are you",
    "tell me about leave policy",
    "salary date",
    "define overtime",
    "what is your name",
    "bye"
]

# -----------------------------
# SAFE SEND
# -----------------------------
def safe_send(driver, msg):
    for _ in range(3):
        try:
            box = driver.find_element(By.ID, "input")
            send_btn = driver.find_element(By.ID, "send")
            box.clear()
            box.send_keys(msg)
            send_btn.click()
            return True
        except StaleElementReferenceException:
            time.sleep(0.5)
    return False

# -----------------------------
# GET BOT REPLY
# -----------------------------
def get_bot_reply(driver):
    xpath = "(//div[@class='msg bot'])[last()]"
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        timeout = time.time() + 20
        while time.time() < timeout:
            try:
                reply = driver.find_element(By.XPATH, xpath).text.strip()
                if reply:
                    return reply
            except:
                pass
            time.sleep(0.3)
    except:
        return ""
    return ""

# -----------------------------
# USER THREAD SESSION
# -----------------------------
def user_session(uid):
    try:
        options = webdriver.EdgeOptions()
        options.add_argument("--headless=new")

        service = Service(EDGE_DRIVER_PATH)
        driver = webdriver.Edge(service=service, options=options)
        driver.get(CHATBOT_URL)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "input"))
        )

        print(f"🧍User {uid} started")

        # CSV File
        file = open(f"user_{uid}_30min_test.csv", "w", newline="", encoding="utf-8")
        writer = csv.writer(file)
        writer.writerow(["Message #", "User Msg", "Bot Reply", "Response Time"])

        for msg_index in range(MESSAGES_PER_USER):
            msg = MESSAGE_LIST[msg_index]

            safe_send(driver, msg)
            start = time.time()
            reply = get_bot_reply(driver)
            end = round(time.time() - start, 2)

            writer.writerow([msg_index + 1, msg, reply, end])
            print(f"User {uid} → {msg} → {reply[:40]}")

            # random delay 2–4 mins
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            time.sleep(delay)

        file.close()
        driver.quit()
        print(f"✅ User {uid} completed")

    except Exception as e:
        print(f"❌ User {uid} failed: {e}")

# -----------------------------
# START USERS
# -----------------------------
print("🚀 Starting 100 users for a 30-minute distributed load test...\n")

threads = []
for u in range(1, TOTAL_USERS + 1):
    t = threading.Thread(target=user_session, args=(u,))
    t.start()
    threads.append(t)
    time.sleep(0.2)  # slow start

# Wait for all threads
for t in threads:
    t.join()

print("\n🎉 30-minute load test completed!")
