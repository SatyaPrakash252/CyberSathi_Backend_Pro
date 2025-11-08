import requests

def get_location():
    try:
        loc = requests.get("https://ipapi.co/json/").json()
        return loc.get("city"), loc.get("region")
    except:
        return None, None
