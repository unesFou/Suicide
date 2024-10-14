from odoo import models, api
import asyncio
import websockets
import json
import threading
from datetime import datetime

connected_clients = set()  # Set to store connected clients

class WebSocketServer(models.AbstractModel):
    _name = 'my_websocket_module.websocket_server'

    @api.model
    def _start_websocket_server(self):
        def run_server():
            async def handler(websocket, path):
                connected_clients.add(websocket)  # Add client to the set upon connection
                try:
                    while True:
                        data = {"message": f"Server time: {datetime.now()}"}
                        await websocket.send(json.dumps(data))
                        await asyncio.sleep(5)
                finally:
                    connected_clients.remove(websocket)  # Remove client from the set upon disconnection

            asyncio.set_event_loop(asyncio.new_event_loop())
            start_server = websockets.serve(handler, "localhost", 5000)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()

        # Start the WebSocket server in a separate thread
        websocket_thread = threading.Thread(target=run_server)
        websocket_thread.daemon = True
        websocket_thread.start()


    # def __init__(self, pool, cr):
    #     self._start_websocket_server()
    #     print("the web socket started on localhost:5000")
        
    # @api.model
    # def _auto_init(self):
        # Call the function to start the WebSocket server when Odoo starts
    
    @api.model
    async def send_json_data_to_clients(self, dict_data):
        # Loop through each connected client
        for websockett in connected_clients:
            try:
                await websockett.send(json.dumps(data))
            except Exception as e:
                # Handle any errors that occur during sending
                print(f"Error sending data to client: {e}")

