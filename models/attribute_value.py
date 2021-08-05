from typing import Optional
from pydantic import BaseModel


class AttributeValue(BaseModel):
    content: str
    link: Optional[str]