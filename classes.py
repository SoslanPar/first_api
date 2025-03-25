from enum import IntEnum
from typing import List, Optional, Annotated, AnyStr

from fastapi import FastAPI, HTTPException, Depends
import uvicorn

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic_settings import SettingsConfigDict, BaseSettings

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select


class Base(DeclarativeBase):
    pass


class TodoModel(Base):
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(primary_key=True)
    todo_name: Mapped[str]
    todo_description: Mapped[str]
    priority: Mapped[int]
    username: Mapped[str]


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[str]
    user_password: Mapped[str]


# class AuthXConfig(BaseSettings):
#     JWT_SECRET_KEY: str = "SECRET_KEY"
#     JWT_ACCESS_COOKIE_NAME: str = 'my_access_token'
#     JWT_TOKEN_LOCATION: list = ['cookies']
#     # model_config = SettingsConfigDict(env_file='.env')


class UserLoginScheme(BaseModel):
    user_email: EmailStr = Field(..., description='User email')
    user_password: str = Field(..., description='Hash_password')


class Priority(IntEnum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1


class TodoBase(BaseModel):
    todo_name: str = Field(..., min_lentgh=2, max_length=512, description='Name of the todo')
    todo_description: str = Field(..., max_length=128, description='Description of the todo')
    priority: Priority = Field(default=Priority.LOW, description='Priority of the todo')
    username: str = Field(..., min_length=2, max_length=64, description='Username')

    model_config = ConfigDict(extra='forbid') # Запрет на лишние поля


class TodoCreate(TodoBase):
    pass


class Todo(TodoBase):
    todo_id: int = Field(..., description='ID if the todo')


class TodoUpdate(BaseModel):
    todo_name: Optional[str]= Field(None, min_lentgh=3, max_length=512, description='Name of the todo')
    todo_description: Optional[str] = Field(None, description='description of the todo')
    priority: Optional[Priority] = Field(None, description='Priority of the todo')
    username: Optional[str] = Field(None, min_length=2, max_length=64, description='Username')
    user_email: Optional[EmailStr] = Field(None, description='User email')


all_todos = [
    Todo(todo_id=1, todo_name='Sports', todo_description="Go to the gym", priority=Priority.MEDIUM, username='Soslan',),
    Todo(todo_id=2, todo_name='Read', todo_description="Read 30 minutes", priority=Priority.MEDIUM, username='Soslan',),
    Todo(todo_id=3, todo_name='History', todo_description="Edit document", priority=Priority.LOW, username='Soslan',),
    Todo(todo_id=4, todo_name='Eat', todo_description="Eat with appetite and between 2000 and 2500 ccal", priority=Priority.MEDIUM, username='Soslan',),
    Todo(todo_id=5, todo_name='Programming', todo_description="Practise programming", priority=Priority.HIGH, username='Soslan',)
]
