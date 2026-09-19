import requests

def main():
    response = requests.get("https://status.render.com/api/v2/status.json")
    print(response)

if __name__ == "__main__":
    main()