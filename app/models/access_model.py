from app.models.base_model import BaseSchema


class Location(BaseSchema):
    id: int
    name: str


class Access(BaseSchema):
    external_id: int
    run: str
    full_name: str
    entry_at: str
    exit_at: str | None = None
    activity: str
    location: str
