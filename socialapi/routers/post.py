from fastapi import APIRouter, HTTPException

from socialapi.database import comment_table, database, post_table
from socialapi.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)

router = APIRouter()

# promise처럼 바로 return 해도 되나?


async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.post("", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    data = dict(post)
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)

    return {**data, "id": last_record_id}


@router.get("", response_model=list[UserPost])
async def get_all_posts():
    query = post_table.select()
    return await database.fetch_all(query)


@router.post("/comments", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = dict(comment)
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)

    return {**data, "id": last_record_id}


@router.get("/{post_id}/comments", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)


@router.get("/{post_id}", response_model=UserPostWithComments)
async def get_post_width_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # App Join?
    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
