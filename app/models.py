from sqlmodel import SQLModel, Field

class EstadoPartida(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
