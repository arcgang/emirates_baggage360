"""Authentication and authorization schemas."""
from pydantic import BaseModel


class PrincipalContext(BaseModel):
    """Current authenticated principal context."""
    user_id: str
    role: str
    display_name: str
    scopes: list[str]
