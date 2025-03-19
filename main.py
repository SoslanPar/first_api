from enum import IntEnum
from typing import List, Optional, Annotated, AnyStr

from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

api = FastAPI()


class Base(DeclarativeBase):
    pass

class TodoModel(Base):
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(primary_key=True)
    todo_name: Mapped[str]
    todo_description: Mapped[str]
    priority: Mapped[int]
    username: Mapped[str]
    user_email: Mapped[str]


class Priority(IntEnum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1


class TodoBase(BaseModel):
    todo_name: str = Field(..., min_lentgh=2, max_length=512, description='Name of the todo')
    todo_description: str = Field(..., max_length=128, description='Description of the todo')
    priority: Priority = Field(default=Priority.LOW, description='Priority of the todo')
    username: str = Field(..., min_length=2, max_length=64, description='Username')
    user_email: EmailStr = Field(..., description='User email')

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
    Todo(todo_id=1, todo_name='Sports', todo_description="Go to the gym", priority=Priority.MEDIUM, username='Soslan', user_email='SP@yandex.ru'),
    Todo(todo_id=2, todo_name='Read', todo_description="Read 30 minutes", priority=Priority.MEDIUM, username='Soslan', user_email='SP@yandex.ru'),
    Todo(todo_id=3, todo_name='History', todo_description="Edit document", priority=Priority.LOW, username='Soslan', user_email='SP@yandex.ru'),
    Todo(todo_id=4, todo_name='Eat', todo_description="Eat with appetite and between 2000 and 2500 ccal", priority=Priority.MEDIUM, username='Soslan', user_email='SP@yandex.ru'),
    Todo(todo_id=5, todo_name='Programming', todo_description="Practise programming", priority=Priority.HIGH, username='Soslan', user_email='SP@yandex.ru'),
]


engine = create_async_engine('sqlite+aiosqlite:///todos.db')

# with engine.connect() as conn:
#     conn.execute('CREATE TABLE ToDos IF NOT EXIST')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@api.post('/setup_databes', tags=['Database'])
async def setup_databese():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {'ok': True}


@api.post('/todo_db', tags=['Database'])
async def add_todo_to_db(todo: Todo, session: SessionDep):
    new_todo = TodoModel(
        todo_name=todo.todo_name,
        todo_description=todo.todo_description,
        priority=todo.priority,
        username=todo.username,
        user_email=todo.user_email
        )
    session.add(new_todo)
    await session.commit()
    return {'ok': True}


@api.get('/todo_db', tags=['Database'])
async def get_todo_from_db(session: SessionDep):
    query = select(TodoModel)
    result = await session.execute(query)
    return result.scalars().all()


@api.get('/', tags = ['Hello'])
def print_hello():
    return 'Hello'


@api.get('/todos', tags=['To do'])
def get_todos(first_n: int = None) -> List[Todo]:
    if first_n:
        return all_todos[:first_n]
    else:
        return all_todos
    

@api.get('/todos/{todo_id}', tags=['To do'])
def get_todo(todo_id: int) -> Todo:
    for todo in all_todos:
        if todo.todo_id == todo_id:
            return todo
        
    raise HTTPException(status_code=404, detail='Todo not found')
    

@api.post('/todos', tags=['To do'])
def create_todo(todo: TodoCreate) -> Todo:
    new_todo_id = max(todo.todo_id for todo in all_todos) + 1

    new_todo = Todo(todo_id = new_todo_id,
                    todo_name = todo.todo_name,
                    todo_description = todo.todo_description,
                    priority = todo.priority,
                    username = todo.username,
                    user_email = todo.user_email)

    all_todos.append(new_todo)

    return new_todo


@api.put('/todos/{todo_id}', tags=['To do'])
def update_todo(todo_id: int, updated_todo: TodoUpdate) -> Todo:
    for todo in all_todos:
        if todo.todo_id == todo_id:

            if updated_todo.todo_name is not None:
                todo.todo_name = updated_todo.todo_name

            if updated_todo.todo_description is not None:
                todo.todo_description = updated_todo.todo_description

            if updated_todo.priority is not None:
                todo.priority = updated_todo.priority

            if updated_todo.username is not None:
                todo.username = updated_todo.username

            if updated_todo.user_email is not None:
                todo.user_email = updated_todo.user_email
                
            return todo
        
    raise HTTPException(status_code=404, detail='Todo not found')


@api.delete('/todos/{todo_id}', tags=['To do'])
def delete_todo(todo_id: int) -> Todo:
    for index, todo in enumerate(all_todos):
        if todo.todo_id == todo_id:
            delete_todo = all_todos.pop(index)
            return delete_todo
        
    raise HTTPException(status_code=404, detail='Todo not found')

if __name__ == '__main__':
    uvicorn.run('main:api', reload=True)