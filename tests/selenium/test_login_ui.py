import os
import pytest
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
SELENIUM_URL = os.getenv("SELENIUM_URL", "")
SCREENSHOT_DIR = "tests/selenium/screenshots"


def get_auth_headers():
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"username": "admin", "password": "password123"},
        timeout=10,
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def send_result(test_name, status, execution_time, result_text):
    headers = get_auth_headers()

    response = requests.post(
        f"{BACKEND_URL}/test-runs",
        json={
            "test_name": test_name,
            "test_type": "ui",
            "status": status,
            "result": result_text,
            "execution_time": execution_time,
        },
        headers=headers,
        timeout=10,
    )
    print("UI result sent:", response.status_code, test_name, status)
    response.raise_for_status()


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    if SELENIUM_URL:
        return webdriver.Remote(
            command_executor=SELENIUM_URL,
            options=chrome_options,
        )

    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )


def save_screenshot(driver, filename):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = os.path.join(SCREENSHOT_DIR, filename)
    driver.save_screenshot(path)
    print("Saved screenshot:", path)


def wait_for_login_page(driver):
    wait = WebDriverWait(driver, 15)
    username_input = wait.until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    password_input = wait.until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    login_button = wait.until(
        EC.element_to_be_clickable((By.ID, "login-button"))
    )
    return username_input, password_input, login_button


def wait_for_message(driver):
    wait = WebDriverWait(driver, 10)
    message = wait.until(
        EC.presence_of_element_located((By.ID, "message"))
    )
    return message.text


def test_login_success_ui():
    if os.getenv("CI") == "true":
        pytest.skip("Skipping Selenium UI tests in CI")

    test_name = "UI Login Success Test"
    start_time = time.time()
    driver = None

    try:
        driver = get_driver()
        driver.get(FRONTEND_URL)

        username_input, password_input, login_button = wait_for_login_page(driver)

        username_input.clear()
        username_input.send_keys("admin")
        password_input.clear()
        password_input.send_keys("password123")
        login_button.click()

        message = wait_for_message(driver)
        assert message == "Login successful"

        execution_time = time.time() - start_time
        send_result(
            test_name,
            "passed",
            execution_time,
            "Selenium success login test passed",
        )

    except Exception as e:
        execution_time = time.time() - start_time

        if driver is not None:
            try:
                save_screenshot(driver, "login_success_failure.png")
            except Exception as screenshot_error:
                print("Screenshot save failed:", screenshot_error)

        try:
            send_result(
                test_name,
                "failed",
                execution_time,
                f"Selenium success login test failed: {str(e)}",
            )
        except Exception as report_error:
            print("Failed to report UI test result:", report_error)

        raise

    finally:
        if driver is not None:
            driver.quit()


def test_login_failure_ui():
    if os.getenv("CI") == "true":
        pytest.skip("Skipping Selenium UI tests in CI")

    test_name = "UI Login Failure Test"
    start_time = time.time()
    driver = None

    try:
        driver = get_driver()
        driver.get(FRONTEND_URL)

        username_input, password_input, login_button = wait_for_login_page(driver)

        username_input.clear()
        username_input.send_keys("wronguser")
        password_input.clear()
        password_input.send_keys("wrongpass")
        login_button.click()

        message = wait_for_message(driver)
        assert message == "Invalid username or password"

        execution_time = time.time() - start_time
        send_result(
            test_name,
            "passed",
            execution_time,
            "Selenium invalid login test passed",
        )

    except Exception as e:
        execution_time = time.time() - start_time

        if driver is not None:
            try:
                save_screenshot(driver, "login_failure_failure.png")
            except Exception as screenshot_error:
                print("Screenshot save failed:", screenshot_error)

        try:
            send_result(
                test_name,
                "failed",
                execution_time,
                f"Selenium invalid login test failed: {str(e)}",
            )
        except Exception as report_error:
            print("Failed to report UI test result:", report_error)

        raise

    finally:
        if driver is not None:
            driver.quit()