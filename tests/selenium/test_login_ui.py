import os
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
SCREENSHOT_DIR = "tests/selenium/screenshots"


def get_auth_headers():
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"username": "admin", "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def send_result(test_name, status, execution_time, result_text):
    headers = get_auth_headers()

    requests.post(
        f"{BACKEND_URL}/test-runs",
        json={
            "test_name": test_name,
            "test_type": "ui",
            "status": status,
            "result": result_text,
            "execution_time": execution_time
        },
        headers=headers
    )


def save_screenshot(driver, filename):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = os.path.join(SCREENSHOT_DIR, filename)
    driver.save_screenshot(path)


def test_login_success_ui():
    test_name = "UI Login Success Test"
    start_time = time.time()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        driver.get(FRONTEND_URL)

        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.ID, "login-button").click()

        message = driver.find_element(By.ID, "message").text
        assert message == "Login successful"

        execution_time = time.time() - start_time
        send_result(test_name, "passed", execution_time, "Selenium success login test passed")

    except Exception:
        execution_time = time.time() - start_time
        save_screenshot(driver, "login_success_failure.png")
        send_result(test_name, "failed", execution_time, "Selenium success login test failed")
        raise

    finally:
        driver.quit()


def test_login_failure_ui():
    test_name = "UI Login Failure Test"
    start_time = time.time()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        driver.get(FRONTEND_URL)

        driver.find_element(By.ID, "username").send_keys("wronguser")
        driver.find_element(By.ID, "password").send_keys("wrongpass")
        driver.find_element(By.ID, "login-button").click()

        message = driver.find_element(By.ID, "message").text
        assert message == "Invalid username or password"

        execution_time = time.time() - start_time
        send_result(test_name, "passed", execution_time, "Selenium invalid login test passed")

    except Exception:
        execution_time = time.time() - start_time
        save_screenshot(driver, "login_failure_failure.png")
        send_result(test_name, "failed", execution_time, "Selenium invalid login test failed")
        raise

    finally:
        driver.quit()