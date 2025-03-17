from enum import IntEnum
from typing import List, Optional

from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field

api = FastAPI()

class Priority(IntEnum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1


class TodoBase(BaseModel):
    todo_name: str = Field(..., min_lentgh=3, max_length=512, description='Name of the todo')
    todo_description: str = Field(..., description='description of the todo')
    priority: Priority = Field(default=Priority.LOW, description='Priority of the todo')


class TodoCreate(TodoBase):
    pass


class Todo(TodoBase):
    todo_id: int = Field(..., description='ID if the todo')


class TodoUpdate(BaseModel):
    todo_name: Optional[str]= Field(None, min_lentgh=3, max_length=512, description='Name of the todo')
    todo_description: Optional[str] = Field(None, description='description of the todo')
    priority: Optional[Priority] = Field(None, description='Priority of the todo')



all_todos = [
    Todo(todo_id=1, todo_name='Sports', todo_description="Go to the gym", priority=Priority.MEDIUM),
    Todo(todo_id=2, todo_name='Read', todo_description="Read 30 minutes", priority=Priority.MEDIUM),
    Todo(todo_id=3, todo_name='History', todo_description="Edit document", priority=Priority.LOW),
    Todo(todo_id=4, todo_name='Eat', todo_description="Eat with appetite and between 2000 and 2500 ccal", priority=Priority.MEDIUM),
    Todo(todo_id=5, todo_name='Programming', todo_description="Practise programming", priority=Priority.HIGH),
]


@api.get('/todos', response_model=List[Todo])
def get_todos(first_n: int = None):
    if first_n:
        return all_todos[:first_n]
    else:
        return all_todos
    

@api.get('/todos/{todo_id}', response_model=Todo)
def get_todo(todo_id: int):
    for todo in all_todos:
        if todo.todo_id == todo_id:
            return todo
        
    raise HTTPException(status_code=404, detail='Todo not found')
    

@api.post('/todos', response_model=Todo)
def create_todo(todo: TodoCreate):
    new_todo_id = max(todo.todo_id for todo in all_todos) + 1

    new_todo = Todo(todo_id = new_todo_id,
                    todo_name = todo.todo_name,
                    todo_description = todo.todo_description,
                    priority = todo.priority)

    all_todos.append(new_todo)

    return new_todo


@api.put('/todos/{todo_id}', response_model=Todo)
def update_todo(todo_id: int, updated_todo: TodoUpdate):
    for todo in all_todos:
        if todo.todo_id == todo_id:
            if updated_todo.todo_name is not None:
                todo.todo_name = updated_todo.todo_name
            if updated_todo.todo_description is not None:
                todo.todo_description = updated_todo.todo_description
            if updated_todo.priority is not None:
                todo.priority = updated_todo.priority
            return todo
        
    raise HTTPException(status_code=404, detail='Todo not found')


@api.delete('/todos/{todo_id}', response_model=Todo)
def delete_todo(todo_id: int):
    for index, todo in enumerate(all_todos):
        if todo.todo_id == todo_id:
            delete_todo = all_todos.pop(index)
            return delete_todo
        
    raise HTTPException(status_code=404, detail='Todo not found')

if __name__ == '__main__':
    uvicorn.run('main:api', reload=True)