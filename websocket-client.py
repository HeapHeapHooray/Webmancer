
import asyncio
from websockets.sync.client import connect
import json
import base64

websocket = connect("ws://localhost:8765",max_size=None)
websocket.send("init_admin_session")
message = websocket.recv()
print(f"Received: {message}")

class WebPage:
    def __init__(self,session_id: int):
        self._session_id = session_id
    def get_html(self):
        return get_html(self._session_id)
    def get_title(self):
        return get_title(self._session_id)
    def set_html(self,html):
        command = """{"command": "set_html","data": """ +'"'+base64.b64encode(html.encode()).decode() + '"'+"""}"""
        send_message(self._session_id,command)


import json

def get_webpages():
    return [WebPage(session_id) for session_id in get_sessions()]

def get_sessions():
    websocket.send("get_all_sessions")
    response = json.loads(websocket.recv())
    return response["response"]

def get_html(session: int):
    msg = {"command": "get_html","session_id": session}
    websocket.send(json.dumps(msg))
    response = json.loads(websocket.recv())
    return response["html"]

def get_title(session: int):
    msg = {"command": "get_title","session_id": session}
    websocket.send(json.dumps(msg))
    response = json.loads(websocket.recv())
    return response["title"]

def replace_images(session: int , image_url: str):
    html = get_html(session)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html)
    imgs = soup.find_all("img")
    for img in imgs:
        img.attrs["src"] = image_url
        img.attrs["srcset"] = image_url 
        
    new_html = soup.prettify()

    command = """{"command": "set_html","data": """+'"'+base64.b64encode(new_html.encode()).decode()+'"'+"""}"""
    
    send_message(session,command)

def send_message(session: int,message: str):
    msg = {"command": "send","sending_to": session,"message": message}
    websocket.send(json.dumps(msg))
