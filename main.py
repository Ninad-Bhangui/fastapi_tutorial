from fastapi import FastAPI,Query, Path, Body
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class User(BaseModel):
    username: str
    full_name: Optional[str] = None

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/")
async def get_items(skip: int =0, limit: int = 10,q: Optional[str] = Query(..., min_length=3, max_length=50, regex="^fixedquery$", alias="item-query",deprecated=True)):
    results = {"items":fake_items_db[skip: skip + limit]}
    if q:
        results.update({"q":q})
    return results

@app.get("/items/{item_id}")
async def read_item(item_id: int = Path(..., title="The ID of the item to get", gt=0, le=1000), q: Optional[str] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"item_id": item_id, "q": q})
    if not short:
        item.update({"descripton": "This is an amazing item with a long description"})
    return item

@app.post("/items/")
async def create_item(item: Item, user: User, importance: int = Body(None, gt =0)):
    print(importance)
    results = {"item": item, "user": user, "importance": importance}
    return results

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: Optional[str] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

#This cannot be above /users/me otherwise this would match /users/me with user_id=me
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

@app.get("/model/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}