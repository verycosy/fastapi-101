from contextlib import asynccontextmanager

from fastapi import FastAPI

from socialapi.database import database
from socialapi.routers.post import router as post_router


# setup, teardown...
@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(post_router, prefix="/posts")
