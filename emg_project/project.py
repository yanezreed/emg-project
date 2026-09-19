import requests

STATUS_URL = "https://status.render.com/api/v2/status.json"

def main():
    response = requests.get(STATUS_URL)
    print(response)

if __name__ == "__main__":
    main()