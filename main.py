from fastapi import FastAPI, Cookie, Header, File, UploadFile,Query, Path, Body
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl

class Image(BaseModel):
    url: HttpUrl
    name: str

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class Item(BaseModel):
    name: str = Field(...,example="Foo")
    description: Optional[str] = Field(None, title="Description", max_length=300, example="Nice item")
    price: float = Field(...,gt=0,description="The price must be greater than zero", example=3.5)
    tax: Optional[float] = Field(None,example=0.5)
    tags: List[str] = Field([],example=['a','b'])
    image: Optional[Image] = Field(None,example={"url": "https://imgur.com/foo.png", "name": "foo.png"})

    class Config:
        scheme_extra = {
            "example": {
                "name": "Foo",
                "description": "Nice item",
                "price": 35.4,
                "tax": 3.2,
                "image": {
                    "url": "https://imgur.com/foo.png",
                    "name": "foo.png"
                }
            }
        }

class User(BaseModel):
    username: str
    full_name: Optional[str] = None

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/cookies/")
async def read_cookies(cookie_id: Optional[str] = Cookie(None)):
    return {"cookie_id": cookie_id}

@app.get("/headers/")
async def read_header(user_agent: Optional[str] = Header(None),accept: Optional[str] = Header(None),cache_control: Optional[str] = Header(None)):
    return {"User-Agent": user_agent, "Accept": accept, "Cache-Control": cache_control}

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

@app.post("/items/", response_model=Item)
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

@app.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}