from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument

from model import WasteItemModel, WasteItemCollection, UpdateWasteItemModel


app = FastAPI(
    title="Waste item Course API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)
MONGO_URL = "mongodb+srv://vipham0938606944:mongodb1472004!@microservice-database.qg2cb.mongodb.net/?retryWrites=true&w=majority&appName=Microservice-Database"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["sorting-waste-app"]
waste_item_collection = db.get_collection("WasteItems")


@app.post(
    "/waste_items/",
    response_description="Add new waste item",
    response_model=WasteItemModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_waste_item(waste_item: WasteItemModel = Body(...)):
    inserted_item = waste_item.model_dump(by_alias=True, exclude={"id"})
    inserted_item["category"] = inserted_item["category"].lower()
    new_waste_item = await waste_item_collection.insert_one(
        inserted_item
    )
    created_waste_item = await waste_item_collection.find_one(
        {"_id": new_waste_item.inserted_id}
    )
    return created_waste_item


@app.get(
    "/waste_items/",
    response_description="List all waste items",
    response_model=WasteItemCollection,
    response_model_by_alias=False,
)
async def list_waste_items():
    return WasteItemCollection(waste_items=await waste_item_collection.find().to_list(1000))


@app.get(
    "/waste_items/{id}",
    response_description="Get a single waste item",
    response_model=WasteItemModel,
    response_model_by_alias=False,
)
async def show_waste_item(id: str):
    if (
        waste_item := await waste_item_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return waste_item

    raise HTTPException(status_code=404, detail=f"Waste item {id} not found")


@app.put(
    "/waste_items/{id}",
    response_description="Update a waste item",
    response_model=WasteItemModel,
    response_model_by_alias=False,
)
async def update_waste_item(id: str, waste_item: UpdateWasteItemModel = Body(...)):
    waste_item = {
        key: value for key, value in waste_item.model_dump(by_alias=True).items() if value is not None
    }
    if("category" in waste_item):
        waste_item["category"] = waste_item["category"].lower()

    if len(waste_item) >= 1:
        update_result = await waste_item_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": waste_item},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Waste item {id} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_waste_item := await waste_item_collection.find_one({"_id": id})) is not None:
        return existing_waste_item

    raise HTTPException(status_code=404, detail=f"Waste item {id} not found")


@app.delete("/waste_items/{id}", response_description="Delete a waste item")
async def delete_waste_item(id: str):
    delete_result = await waste_item_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Waste item {id} not found")
