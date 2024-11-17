import json
from datetime import datetime


from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import JSON, create_engine, func
from sqlalchemy.types import BigInteger, DateTime

from sqlalchemy.ext.mutable import MutableDict

class Base(DeclarativeBase):
    pass


class TgLinkUsers(Base):
    __tablename__ = "tg_link"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_user_tg: Mapped[int] = mapped_column(BigInteger,unique=True)
    url: Mapped[str] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(nullable=True)
    category:Mapped[str] = mapped_column(nullable=True)
    priority:Mapped[str] = mapped_column(nullable=True)
    source:Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now())



    def __repr__(self) -> str:
        return f"User_table_id : {self.id},\nUser_tg_id: {self.id_user_tg}\nUsername_tg: {self.tg_username}\nDict_users: {self.dict_users}"


engine = create_engine("sqlite:///databasesqlite.db", echo=True)

Base.metadata.create_all(engine)
