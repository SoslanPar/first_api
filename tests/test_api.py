import pytest
from httpx import AsyncClient, ASGITransport

from main import api

@pytest.mark.asyncio
async def test_get_todo():
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
       response = await ac.get("/todos")

       assert response.status_code == 200
       data = response.json()
       assert len(data) == 5

    
@pytest.mark.asyncio
async def test_post_todo():
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as ac:
       response = await ac.post("/todos", json={
           "todo_name": "Gym",
           "todo_description": "Pump",
           "priority": 3,
           "username": "Soslan",
       })

       assert response.status_code == 200

       data = response.json()

       assert data == {"todo_name": "Gym",
           "todo_description": "Pump",
           "priority": 3,
           "username": "Soslan",
           "todo_id": 6}