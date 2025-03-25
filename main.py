from enum import IntEnum
from typing import List, Optional, Annotated, AnyStr

from fastapi import FastAPI, HTTPException, Depends, Response, File, UploadFile
from fastapi.responses import StreamingResponse, FileResponse

import uvicorn

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic_settings import SettingsConfigDict, BaseSettings

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

from authx import AuthX, AuthXConfig

from hashlib import sha256

from classes import *

    
api = FastAPI()


engine = create_async_engine('sqlite+aiosqlite:///todos_and_users.db')

# with engine.connect() as conn:
#     conn.execute('CREATE TABLE ToDos IF NOT EXIST')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


#"Data base"
@api.post('/setup_databases', tags=['Database'])
async def setup_todo_databese():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all) # Base.metadata само создаёт все таблицы, которые унаследовались от Base
    return {'ok': True}


@api.post('/add_todo_db', tags=['Database'])
async def add_todo_to_db(todo: Todo, session: SessionDep):
    new_todo = TodoModel(
        todo_name=todo.todo_name,
        todo_description=todo.todo_description,
        priority=todo.priority,
        username=todo.username
        )
    session.add(new_todo)
    await session.commit()
    return {'ok': True}

@api.post('/add_user_db', tags=['Database'])
async def add_user_to_db(user: UserLoginScheme, session: SessionDep):
    new_user = UserModel(
        user_email = user.user_email,
        user_password = sha256(user.user_password.encode()).hexdigest()
    )
    session.add(new_user)
    await session.commit()
    return {'ok': True}

@api.get('/todo_db', tags=['Database'])
async def get_todo_from_db(session: SessionDep):
    query = select(TodoModel)
    result = await session.execute(query)
    return result.scalars().all()

@api.get('/user_db', tags=['Database'])
async def get_todo_from_db(session: SessionDep):
    query = select(UserModel)
    print(query)
    result = await session.execute(query)
    return result.scalars().all()


#"Authorisation"
# config = AuthXConfig()
# security = AuthX(config=config)

# @api.post('/login', tags=['Authorisation'])
# def login(credentials: UserLoginScheme, response: Response):
#     if credentials.user_email == 'test@yandex.ru' and credentials.user_password == 'test':
#         token = security.create_access_token(uid='12345')
#         response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
#         return {"access_token": token}
#     raise HTTPException(status_code=401, detail='Incorrect username or password')
    
# @api.get('/protected', tags=['Authorisation'], dependencies=[Depends(security.access_token_required)])
# def protected():
#     return {'data': 'TOP SECRET'}


#"To Do"
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
                    username = todo.username)

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
                
            return todo
        
    raise HTTPException(status_code=404, detail='Todo not found')

@api.delete('/todos/{todo_id}', tags=['To do'])
def delete_todo(todo_id: int) -> Todo:
    for index, todo in enumerate(all_todos):
        if todo.todo_id == todo_id:
            delete_todo = all_todos.pop(index)
            return delete_todo
        
    raise HTTPException(status_code=404, detail='Todo not found')


"Files"
@api.post("/file", tags=['Files'])
async def upload_file(uploaded_file: UploadFile):
    file = uploaded_file.file
    file_name = uploaded_file.filename
    with open(f"1_{file_name}", "wb") as f:
        f.write(file.read())

@api.post("/many_files", tags=['Files'])
async def upload_files(uploaded_files: list[UploadFile]):
    for index, uploaded_file in enumerate(uploaded_files):
        file = uploaded_file.file
        filename = uploaded_file.filename
        with open(f"{index + 1}_{filename}", "wb") as f:
            f.write(file.read())

@api.get('/file/{filename}', tags=['Files'])
async def get_file(filename: str):
    return FileResponse(filename)

def iterfile(filename: str):
    with open(filename, "rb") as f:
        while chunk := f.read(1024 * 1024): #возвращает частями
            yield chunk

@api.get('/file/streaming/{filename}', tags=['Files'])
async def get_streaming_file(filename: str):
    return StreamingResponse(iterfile(filename), media_type='video/mp4') # загружает частями

if __name__ == '__main__':
    uvicorn.run('main:api', reload=True)