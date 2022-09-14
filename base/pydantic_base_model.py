from pydantic import BaseModel, Extra


class PydanticBaseModel(BaseModel):
    ...

    class Config:
        extra = Extra.forbid
