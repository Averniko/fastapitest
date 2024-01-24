import websockets
from fastapi import FastAPI, WebSocket, APIRouter, Request, Response, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

app = FastAPI()

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

templates = Jinja2Templates(directory="templates")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.get("/get")
async def get_chat_page(request: Request) -> Response:
    return templates.TemplateResponse("chat.html", {"request": request})


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


@router.post("/test-message")
async def test_message(request: Request):
    client_id = 1
    async with websockets.connect(f"ws://localhost:8000/chat/ws/{client_id}") as websocket:
        await websocket.send("Hello, Server!")
        response = await websocket.recv()
        print(f"Received: {response}")
