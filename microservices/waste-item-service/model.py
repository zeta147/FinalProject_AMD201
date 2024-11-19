from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field, EmailStr

from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from bson import ObjectId

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

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


class UpdateWasteItemModel(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    sorting_instructions: Optional[str] = None
    created_by_username: Optional[str] = None
    created_by_email: Optional[EmailStr] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Expired Food",
                "category": "Food Waste",
                "sorting_instructions": "dawdadwada",
                "created_by_username": "Jane Doe",
                "created_by_email": "jdoe@example.com",
            }
        },
    )


class WasteItemCollection(BaseModel):
    waste_items: List[WasteItemModel]

