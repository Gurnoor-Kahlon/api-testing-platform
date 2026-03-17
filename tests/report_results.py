import requests

API_URL = "http://localhost:8000/test-runs"


def send_test_result(name, status, duration):
    try:
        response = requests.post(
            API_URL,
            json={
                "test_name": name,
                "status": status,
                "result": f"{name} {status}",
                "execution_time": duration
            },
            headers={
                "Authorization": "Bearer testtoken123"
            }
        )
        print("Sent:", response.status_code)
    except Exception as e:
        print("Error sending test result:", e)