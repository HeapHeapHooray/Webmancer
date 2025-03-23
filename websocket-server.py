#!/usr/bin/env python

import asyncio
from websockets.server import serve
import websockets
import json

from bs4 import BeautifulSoup

green = True

sessions = {}
current_id = 0

def create_session(websocket,admin=False):
    global sessions
    global current_id
    session = {"socket": websocket,"id": current_id,"address": websocket.remote_address,"admin": admin,"session_requests": []}
    sessions[session["address"]] = session
    current_id += 1
    return session

def get_session_by_id(id):
    for key,session in sessions.items():
        if session["id"] == id:
            return session
    return None

def get_session(websocket):
    return sessions[websocket.remote_address]
        

async def echo(websocket):
    async def send_command(command: str,data: str):
        await websocket.send(json.dumps({"command": command,"data": data}))
    async def alert(data: str):
        await send_command("alert",data)
    
    while True:
        try:
            message = await websocket.recv()

            print(message)
            if message == "init_session":
                print("Initializing Session...",sessions)
                await websocket.send("session_id: " + str(create_session(websocket)["id"]))
            if message == "init_admin_session":
                print("Initializing Admin Session...")
                await websocket.send("session_id: " + str(create_session(websocket,admin=True)["id"]))
                print("sessions:",sessions)
                
            session = get_session(websocket)

            if session["admin"] and message == "get_all_sessions":
                ids = []
                for key,session in sessions.items():
                    if not session["admin"]:
                        ids.append(session["id"])
                response = {"response": ids}
                await websocket.send(json.dumps(response))

            if len(session["session_requests"]):
                req = session["session_requests"].pop()
                await send_command(req[1][0],req[1][1])
                await websocket.recv()
                response = await websocket.recv()
                await get_session_by_id(req[0])["socket"].send(response)
            
            if message[0] != "{":
                continue
            parsed_message = json.loads(message)
            
            if "command" in parsed_message.keys():
                if not session["admin"]:
                    continue

            if parsed_message["command"] == "send":
                dest_id = int(parsed_message["sending_to"])
                data = parsed_message["message"]
                await get_session_by_id(dest_id)["socket"].send(data)

            if parsed_message["command"] == "get_html":
                session_id = parsed_message["session_id"]
                # Appends current section's id to the read requests of the session specified by session_id
                get_session_by_id(session_id)["session_requests"].append((session["id"],("read_html","")))
                await get_session_by_id(session_id)["socket"].send("i")

            if parsed_message["command"] == "get_title":
                session_id = parsed_message["session_id"]
                # Appends current section's id to the read requests of the session specified by session_id
                get_session_by_id(session_id)["session_requests"].append((session["id"],("get_title","")))
                await get_session_by_id(session_id)["socket"].send("i")
                
            
            #await send_command("alert","hello")
        except websockets.exceptions.ConnectionClosedOK:
            #global sessions
            try:
                del sessions[websocket.remote_address]
            except:
                pass

async def main():
    async with serve(echo, "localhost", 8765,max_size=None):
        await asyncio.Future()  # run forever

asyncio.run(main()) 
