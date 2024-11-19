from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field, EmailStr

from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from bson import ObjectId

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

class ChallengeModel(BaseModel):
    # The primary key for the StudentModel, stored as a `str` on the instance.
    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    category: str = Field(...)
    description: str = Field(...)
    difficulty_level: int = Field(..., le=10)
    scoring_criteria: str = Field(...)
    created_by_username: str = Field(...)
    created_by_email: EmailStr = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "category": "Food waste",
                "description": "expired food",
                "difficulty_level": "2",
                "scoring_criteria": "a lot of food are wasting",
                "created_by_username": "Jane Doe",
                "created_by_email": "jdoe@example.com",
            }
        },
    )


class UpdateChallengeModel(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[int] = None
    scoring_criteria: Optional[str] = None
    created_by_username: str = Field(...)
    created_by_email: EmailStr = Field(...)
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "category": "Food waste",
                "description": "expired food",
                "difficulty_level": "2",
                "scoring_criteria": "a lot of food are wasting",
                "created_by_username": "Jane Doe",
                "created_by_email": "jdoe@example.com",
            }
        },
    )


class ChallengeCollection(BaseModel):
    challenges: List[ChallengeModel]


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    age: int = Field(None, le=100, description="Age of the user (only accept maximum 100)")
    email: EmailStr = Field(...)
    password: str = Field(...)
    course: str = Field(None)
    challenge: str = Field(None, description="category of the challenge")
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "age": "18",
                "email": "jdoe@example.com",
                "password": "123456",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "challenge": "food waste",
            }
        },
    )

class UserCollection(BaseModel):
    users: List[UserModel]
