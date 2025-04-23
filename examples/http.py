import requests

BASE_URL = "http://192.168.1.150/api"

def set_voltage(voltage):
    try:
        response = requests.post(f"{BASE_URL}/set_voltage", json={"voltage": voltage})
        return response.json()
    except Exception as e:
        return f"Error: {e}"

def get_voltage():
    try:
        response = requests.get(f"{BASE_URL}/get_voltage")
        return response.json()
    except Exception as e:
        return f"Error: {e}"

# Ejemplo de uso
print(set_voltage(10))
print(get_voltage())
