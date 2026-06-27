## FastAPI for a beginner
FastAPI is a Python framework for building web APIs. In simple words, you write Python functions, and FastAPI turns them into URLs that other programs can call

#### Basic building blocks
1. FastAPI() app  
   * This creates the web application.
   * Think of it as the main engine of your API.
2. Route decorators  
   * **@app.get("/")** means: when someone visits `/`, run this function.
   * Other common ones are `@app.post()`,` @app.put()`, and `@app.delete()`.
3. Route functions  
   * These are normal Python functions.
   * They contain the logic for each endpoint.
4. Return values  
   * If you return a dictionary, FastAPI turns it into JSON automatically.
   * Example: return {"pong": 1}
5. Status codes and errors
   * status_code=200 means success.
   * HTTPException is used when something goes wrong.
6. Response object
   * Response lets you return raw text or custom content types.
   In your TEMPLATE  example, /metrics returns plain text.

#### The simple flow
When a user or another app calls an endpoint:

- 1. The request reaches FastAPI.
* 2. FastAPI matches the URL to the correct route.
* 3. It runs the Python function for that route.
* 4. It sends the result back as an HTTP response.

 `Client → URL → Python function → JSON/text response`

 A FastAPI app is usually made of:

- one app object,
- several route functions,
- and a server that runs it.
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello"}
```

### how FastAPI handles?:
 * request methods
 * path parameters 
 * query parameters
 * request bodies

#### 1. Request methods
So far, you used `@app.get("/")`.

That means:
- GET is used to read data
- Common methods are:
```
GET → read
POST → create
PUT → update
DELETE → remove
```
```
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
def get_items():
    return {"message": "list items"}

@app.post("/items")
def create_item():
    return {"message": "item created"}
```
2. Path parameters
These are values inside the URL.
eg:
```
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```
If you visit:
 * /users/5
then user_id becomes 5.

3. Query parameters
These are values added after ? in the URL.

Example:
```
@app.get("/search")
def search(q: str = None):
    return {"query": q}
```
Visit:

`/search?q=fastapi`
and you get:
```
{"query": "fastapi"}
```
4. Request body
For sending data like JSON, you use a request body.

Example:
```
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
def create_item(item: Item):
    return {"message": "created", "item": item}
```
Here:
  * Item is a data model
  * FastAPI reads the JSON body and validates it

---
#### next useful topics are:

* request and response models
* validation
* dependency injection
* routers
