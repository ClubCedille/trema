import requests

def verify_gh_user(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    return response.status_code == 200
