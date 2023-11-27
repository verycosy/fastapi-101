import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, Request, Response

os.environ["ENV_STATE"] = "test"

from socialapi.database import database, user_table  # noqa: E402
from socialapi.main import app  # noqa: E402


# 모든 테스트에서 한 번만 수행
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


# 매 테스트마다 수행
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


# def client의 반환값이 의존성으로 주입됨
# 변수 이름만으로..이래도 되나..?
@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@test.com", "password": "1234"}

    await async_client.post("/register", json=user_details)

    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)

    user_details["id"] = user.id

    return user_details


@pytest.fixture()
async def confirmed_user(registered_user: dict) -> dict:
    query = (
        user_table.update().where(user_table.c.email == registered_user["email"])
    ).values(confirmed=True)
    await database.execute(query)
    return registered_user


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict) -> str:
    response = await async_client.post("/token", json=confirmed_user)

    return response.json()["access_token"]


@pytest.fixture(autouse=True)
def mock_httpx_client(mocker):
    mocked_client = mocker.patch("socialapi.tasks.httpx.AsyncClient")

    mocked_async_client = Mock()
    response = Response(status_code=200, content="", request=Request("POST", "//"))
    mocked_async_client.post = AsyncMock(return_value=response)
    mocked_client.return_value.__aenter__.return_value = mocked_async_client

    return mocked_async_client
