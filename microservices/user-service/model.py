from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field, EmailStr

from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from bson import ObjectId

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

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


class UpdateUserModel(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    course: Optional[str] = None
    challenge: Optional[str] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
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


class LoginModel(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "password": "123456",
            }
        },
    )


class WasteItemModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    category: str = Field(...)
    sorting_instructions: str = Field(...)
    created_by_username: str = Field(...)
    created_by_email: EmailStr = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Expired Food",
                "category": "Food Waste",
                "sorting_instructions": "dawdawda",
                "created_by_username": "Jane Doe",
                "created_by_email": "jdoe@example.com",
            }
        },
    )

class WasteItemCollection(BaseModel):
    waste_items: List[WasteItemModel]
