from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument

from model import ChallengeModel, ChallengeCollection, UpdateChallengeModel, UserModel, UserCollection


app = FastAPI(
    title="Challenges API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)
MONGO_URL = "mongodb+srv://vipham0938606944:mongodb1472004!@microservice-database.qg2cb.mongodb.net/?retryWrites=true&w=majority&appName=Microservice-Database"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["sorting-waste-app"]
challenge_collection = db.get_collection("Challenges")
user_collection = db.get_collection("Users")


@app.post(
    "/challenges/",
    response_description="Add new challenge",
    response_model=ChallengeModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_challenge(challenge: ChallengeModel = Body(...)):
    inserted_challenge = challenge.model_dump(by_alias=True, exclude={"id"})
    inserted_challenge["category"] = inserted_challenge["category"].lower()

    new_challenge = await challenge_collection.insert_one(
        inserted_challenge
    )
    created_challenge = await challenge_collection.find_one(
        {"_id": new_challenge.inserted_id}
    )
    return created_challenge


@app.get(
    "/challenges/",
    response_description="List all challenges",
    response_model=ChallengeCollection,
    response_model_by_alias=False,
)
async def list_challenges():
    return ChallengeCollection(challenges=await challenge_collection.find().to_list(1000))

@app.get(
    "/challenges/{id}",
    response_description="Get a single challenge",
    response_model=ChallengeModel,
    response_model_by_alias=False,
)
async def show_challenge(id: str):
    if (
        challenge := await challenge_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return challenge

    raise HTTPException(status_code=404, detail=f"Challenge {id} not found")


# Version 1
@app.get(
    "/challenges/{id}/users",
    response_description="Get a single challenge",
    response_model=UserCollection,
    response_model_by_alias=False,
)
async def show_challenge(id: str):
    challenge = await challenge_collection.find_one({"_id": ObjectId(id)})
    if(challenge):
        return UserCollection(users = await user_collection.find({"challenge": challenge["category"]}).to_list(1000))

    raise HTTPException(status_code=404, detail=f"Challenge {id} not found")




@app.put(
    "/challenges/{id}",
    response_description="Update a challenge",
    response_model=ChallengeModel,
    response_model_by_alias=False,
)
async def update_challenge(id: str, challenge: UpdateChallengeModel = Body(...)):
    challenge = {
        key: value for key, value in challenge.model_dump(by_alias=True).items() if value is not None
    }

    if("category" in challenge):
        challenge["category"] = challenge["category"].lower()

    if len(challenge) >= 1:
        update_result = await challenge_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": challenge},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Challenge {id} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_challenge := await challenge_collection.find_one({"_id": id})) is not None:
        return existing_challenge

    raise HTTPException(status_code=404, detail=f"Challenge {id} not found")


@app.delete("/challenges/{id}", response_description="Delete a challenge")
async def delete_challenge(id: str):
    delete_result = await challenge_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Challenge {id} not found")
