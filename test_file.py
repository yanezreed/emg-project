import requests

def test():

    print(f"Emg_project status: Starting\n\n")

    render_url_responce = request_render_url()
    render_status = get_render_status(render_url_responce)

    print_status(render_status)

def request_render_url():
    response = requests.get("https://status.render.com/api/v2/status.json", timeout = 5)
    # needs a quick time out otherwise the user may think the application has crashed...

    if response.status_code != 200:
        print("Did not recieve a responce from render.")
        return None
    else:
        return response

def get_render_status(render_url_responce):

    if render_url_responce == None:
        return None
    
    else:
        python_dict = render_url_responce.json()
        return python_dict["status"]["description"]

def print_status(render_status):

    if render_status == None:
        print("Render status not included in responce.")

    else:
        print(f"Render status: {render_status}\n\n")
