from tabnanny import check

from passlib.context import CryptContext

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument

from model import UserModel, UserCollection, UpdateUserModel, LoginModel, WasteItemModel, WasteItemCollection


app = FastAPI(
    title="Waste category API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)
MONGO_URL = "mongodb+srv://vipham0938606944:mongodb1472004!@microservice-database.qg2cb.mongodb.net/?retryWrites=true&w=majority&appName=Microservice-Database"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["sorting-waste-app"]
user_collection = db.get_collection("Users")
waste_item_collection = db.get_collection("WasteItems")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


@app.post(
    "/users/login/",
    response_description="register a new user",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def login(form_data : LoginModel = Body(...)):
    input_email = form_data.email
    user_dict = await user_collection.find_one({"email": input_email})
    if not user_dict:
        raise HTTPException(status_code=400, detail="Email not found")
    hashed_password = user_dict["password"]
    input_password = form_data.password
    if not verify_password(input_password, hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return {"email": user_dict["email"], "Login": "successfully logged in"}


@app.post(
    "/users/register/",
    response_description="Add new user",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_user(user: UserModel = Body(...)):
    inserted_user = user.model_dump(by_alias=True, exclude={"id"})
    inserted_email = inserted_user["email"]
    user_dict = await user_collection.find_one({"email": inserted_email})
    if user_dict:
        raise HTTPException(status_code=403, detail="Email already registered")

    inserted_user["challenge"] = inserted_user["challenge"].lower()

    inserted_user["password"] = get_password_hash(inserted_user["password"])
    new_user = await user_collection.insert_one(
        inserted_user
    )
    created_user = await user_collection.find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user

@app.get(
    "/users/",
    response_description="List all users",
    response_model=UserCollection,
    response_model_by_alias=False,
)
async def list_users():
    return UserCollection(users = await user_collection.find().to_list(1000))

@app.get(
    "/users/{id}",
    response_description="Get a single user",
    response_model=UserModel,
    response_model_by_alias=False,
)
async def show_user(id: str):
    if (
        user := await user_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return user

    raise HTTPException(status_code=404, detail=f"User {id} not found")

@app.get(
    "/users/{id}/items",
    response_description="Get all the waste items that this user created",
    response_model=WasteItemCollection,
    response_model_by_alias=False,
)
async def show_user_items(id: str):
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if (len(user) > 0):
        return WasteItemCollection(waste_items = await waste_item_collection.find({"email" : user["email"]}).to_list(1000))
    raise HTTPException(status_code=404, detail=f"User {id} not found")

@app.put(
    "/users/{id}",
    response_description="Update a user",
    response_model=UserModel,
    response_model_by_alias=False,
)
async def update_user(id: str, user: UpdateUserModel = Body(...)):
    # get the new value of each attribute
    user = {
        key: value for key, value in user.model_dump(by_alias=True).items() if value is not None
    }

    if("email" in user):
        user_dict = await user_collection.find_one({"email": user["email"]})
        if(len(user_dict) > 0):
            raise HTTPException(status_code=403, detail="Email already registered")

    if("challenge" in user):
        user["challenge"] = user["challenge"].lower()

    if ("password" in user):
        user["password"] = get_password_hash(user["password"])

    if len(user) >= 1:
        update_result = await user_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": user},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"User {id} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_user := await user_collection.find_one({"_id": id})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {id} not found")


@app.delete("/users/{id}", response_description="Delete a user")
async def delete_user(id: str):
    delete_result = await user_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"User {id} not found")
