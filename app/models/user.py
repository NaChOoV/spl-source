from app.models.base_model import BaseSchema


class AbmUser(BaseSchema):
    external_id: int
    run: str
    first_name: str
    last_name: str


class UserAccess(BaseSchema):
    location: int
    entry_at: str
    exit_at: str | None = None


class User(BaseSchema):
    image_url: str | None
    run: str
    first_name: str
    last_name: str
    access_history: list[UserAccess]
