import socketio

# mgr = socketio.AsyncRedisManager(url="redis://localhost:6379/0") 
sio = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=[]
)

@sio.event
async def connect(sid, environ):
    print(f"✅ Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")

@sio.event
async def my_event(sid, data):
    print(f"📦 Received data from {sid}: {data}")
    await sio.emit("response", {"data": "Message received!"}, to=sid)