import uvicorn
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import socketio
from typing import List, Dict

# -----------------------------------------------------------------------------
# In-memory data stores
# -----------------------------------------------------------------------------
users_db: Dict[int, Dict] = {}
products_db: Dict[int, Dict] = {}
user_id_counter = 1
product_id_counter = 1

# -----------------------------------------------------------------------------
# Socket.IO Server Setup
# -----------------------------------------------------------------------------
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

@sio.event
async def connect(sid, environ):
    print(f"Socket.IO client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Socket.IO client disconnected: {sid}")

@sio.on("join_room")
async def join_room(sid, room):
    await sio.enter_room(sid, room)
    print(f"Client {sid} joined room: {room}")

# -----------------------------------------------------------------------------
# FastAPI Application Setup
# -----------------------------------------------------------------------------
# This app will handle all standard HTTP routes
fastapi_app = FastAPI()

# -----------------------------------------------------------------------------
# API Router for Users
# -----------------------------------------------------------------------------
user_router = APIRouter(prefix="/api/user")

@user_router.get("/", response_model=List[Dict])
async def get_users():
    return list(users_db.values())

@user_router.post("/")
async def create_user(user: Dict):
    global user_id_counter
    new_user = {"id": user_id_counter, "name": user["name"], "email": user["email"]}
    users_db[user_id_counter] = new_user
    user_id_counter += 1
    await sio.emit("user_update", new_user, room="user_room")
    return new_user

@user_router.put("/{user_id}")
async def update_user(user_id: int, user: Dict):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = {"id": user_id, "name": user["name"], "email": user["email"]}
    users_db[user_id] = updated_user
    await sio.emit("user_update", updated_user, room="user_room")
    return updated_user

@user_router.delete("/{user_id}")
async def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = users_db.pop(user_id)
    await sio.emit("user_deleted", {"id": user_id}, room="user_room")
    return deleted_user

# -----------------------------------------------------------------------------
# API Router for Products
# -----------------------------------------------------------------------------
product_router = APIRouter(prefix="/api/products")

@product_router.get("/", response_model=List[Dict])
async def get_products():
    return list(products_db.values())

@product_router.post("/")
async def create_product(product: Dict):
    global product_id_counter
    new_product = {"id": product_id_counter, "name": product["name"], "price": product["price"]}
    products_db[product_id_counter] = new_product
    product_id_counter += 1
    await sio.emit("product_update", new_product, room="product_room")
    return new_product

@product_router.put("/{product_id}")
async def update_product(product_id: int, product: Dict):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    updated_product = {"id": product_id, "name": product["name"], "price": product["price"]}
    products_db[product_id] = updated_product
    await sio.emit("product_update", updated_product, room="product_room")
    return updated_product

@product_router.delete("/{product_id}")
async def delete_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    deleted_product = products_db.pop(product_id)
    await sio.emit("product_deleted", {"id": product_id}, room="product_room")
    return deleted_product

# Include the routers in the FastAPI app
fastapi_app.include_router(user_router)
fastapi_app.include_router(product_router)

# -----------------------------------------------------------------------------
# HTML User Interface
# -----------------------------------------------------------------------------
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI & Socket.IO</title>
    <style>
        body { font-family: sans-serif; }
        .container { display: flex; justify-content: space-around; }
        .section { width: 45%; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 5px 0; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        input { margin-bottom: 10px; padding: 5px; width: 100%; box-sizing: border-box; }
        button { padding: 8px 12px; }
    </style>
</head>
<body>
    <h1>Real-time FastAPI Server</h1>
    <div class="container">
        <div class="section">
            <h2>Users</h2>
            <ul id="user-list"></ul>
            <h3>Add/Update User</h3>
            <input type="text" id="user-id" placeholder="ID (for update)">
            <input type="text" id="user-name" placeholder="Name">
            <input type="email" id="user-email" placeholder="Email">
            <button onclick="addUser()">Add User</button>
            <button onclick="updateUser()">Update User</button>
        </div>
        <div class="section">
            <h2>Products</h2>
            <ul id="product-list"></ul>
            <h3>Add/Update Product</h3>
            <input type="text" id="product-id" placeholder="ID (for update)">
            <input type="text" id="product-name" placeholder="Name">
            <input type="number" id="product-price" placeholder="Price">
            <button onclick="addProduct()">Add Product</button>
            <button onclick="updateProduct()">Update Product</button>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <script>
        class WsClient {
            constructor(url, rooms) {
                this.socket = io(url, {
                    // No 'path' is needed; it defaults to /socket.io
                    transports: ['websocket'],
                    reconnection: true,
                    reconnectionAttempts: 5,
                    reconnectionDelay: 1000,
                });
                this.rooms = rooms;
                this.setupEventListeners();
            }

            setupEventListeners() {
                this.socket.on('connect', () => {
                    console.log('Connected to WebSocket server!');
                    this.joinRooms();
                });

                this.socket.on('disconnect', () => {
                    console.log('Disconnected from WebSocket server.');
                });

                this.socket.on('reconnect', (attemptNumber) => {
                    console.log(`Reconnected after ${attemptNumber} attempts.`);
                });
            }

            joinRooms() {
                this.rooms.forEach(room => {
                    this.socket.emit('join_room', room);
                });
            }

            on(event, callback) {
                this.socket.on(event, callback);
            }
        }

        const wsClient = new WsClient(window.location.origin, ['user_room', 'product_room']);

        // --- User UI Logic ---
        function renderUser(user) {
            const existingLi = document.getElementById(`user-${user.id}`);
            if (existingLi) {
                existingLi.innerHTML = `<b>${user.name}</b> (${user.email}) <button onclick="deleteUser(${user.id})">Delete</button>`;
            } else {
                const li = document.createElement('li');
                li.id = `user-${user.id}`;
                li.innerHTML = `<b>${user.name}</b> (${user.email}) <button onclick="deleteUser(${user.id})">Delete</button>`;
                document.getElementById('user-list').appendChild(li);
            }
        }

        function removeUser(userId) {
            const userLi = document.getElementById(`user-${userId}`);
            if (userLi) {
                userLi.remove();
            }
        }

        async function fetchUsers() {
            const response = await fetch('/api/user/');
            const users = await response.json();
            document.getElementById('user-list').innerHTML = '';
            users.forEach(renderUser);
        }

        async function addUser() {
            const name = document.getElementById('user-name').value;
            const email = document.getElementById('user-email').value;
            await fetch('/api/user/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email }),
            });
        }

        async function updateUser() {
            const id = document.getElementById('user-id').value;
            const name = document.getElementById('user-name').value;
            const email = document.getElementById('user-email').value;
            await fetch(`/api/user/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email }),
            });
        }

        async function deleteUser(id) {
            await fetch(`/api/user/${id}`, { method: 'DELETE' });
        }

        // --- Product UI Logic ---
        function renderProduct(product) {
            const existingLi = document.getElementById(`product-${product.id}`);
            if (existingLi) {
                existingLi.innerHTML = `<b>${product.name}</b> - $${product.price} <button onclick="deleteProduct(${product.id})">Delete</button>`;
            } else {
                const li = document.createElement('li');
                li.id = `product-${product.id}`;
                li.innerHTML = `<b>${product.name}</b> - $${product.price} <button onclick="deleteProduct(${product.id})">Delete</button>`;
                document.getElementById('product-list').appendChild(li);
            }
        }

        function removeProduct(productId) {
            const productLi = document.getElementById(`product-${productId}`);
            if (productLi) {
                productLi.remove();
            }
        }

        async function fetchProducts() {
            const response = await fetch('/api/products/');
            const products = await response.json();
            document.getElementById('product-list').innerHTML = '';
            products.forEach(renderProduct);
        }

        async function addProduct() {
            const name = document.getElementById('product-name').value;
            const price = parseFloat(document.getElementById('product-price').value);
            await fetch('/api/products/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, price }),
            });
        }

        async function updateProduct() {
            const id = document.getElementById('product-id').value;
            const name = document.getElementById('product-name').value;
            const price = parseFloat(document.getElementById('product-price').value);
            await fetch(`/api/products/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, price }),
            });
        }

        async function deleteProduct(id) {
            await fetch(`/api/products/${id}`, { method: 'DELETE' });
        }

        // --- WebSocket Event Handling ---
        wsClient.on('user_update', renderUser);
        wsClient.on('user_deleted', (data) => removeUser(data.id));
        wsClient.on('product_update', renderProduct);
        wsClient.on('product_deleted', (data) => removeProduct(data.id));

        // --- Initial Data Fetch ---
        window.onload = () => {
            fetchUsers();
            fetchProducts();
        };
    </script>
</body>
</html>
"""

@fastapi_app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content=html_content)

# This is the main ASGI app that Uvicorn will run.
# It handles Socket.IO requests and forwards all other requests to the FastAPI app.
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

if __name__ == "__main__":
    uvicorn.run("test_socket_3:app", host="0.0.0.0", port=8000, reload=True)