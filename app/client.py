import requests

def check_root_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 400:
            print("Запрос успешен, код 200.")
        else:
            exit(-1)
    except requests.RequestException as e:
        exit(-1)


check_root_url("http://localhost:8080")