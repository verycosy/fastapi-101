import logging

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

logger = logging.getLogger(__name__)

# promise처럼 바로 return 해도 되나?


async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)

    return await database.fetch_one(query)


@router.post("", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    logger.info("Creating post")

    data = dict(post)
    query = post_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)

    return {**data, "id": last_record_id}


@router.get("", response_model=list[UserPost])
async def get_all_posts():
    logger.info("Getting all posts")  # 데코레이터로 요런 걸 직접 만들수도
    query = post_table.select()

    logger.debug(query)

    return await database.fetch_all(query)


@router.post("/comments", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    logger.info("Creating comment")

    post = await find_post(comment.post_id)
    if not post:
        logger.error(f"Post with id {comment.post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    data = dict(comment)
    query = comment_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)

    return {**data, "id": last_record_id}


@router.get("/{post_id}/comments", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    logger.info("Getting comments on post")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)

    return await database.fetch_all(query)


@router.get("/{post_id}", response_model=UserPostWithComments)
async def get_post_width_comments(post_id: int):
    logger.info("Getting post and its comments")

    post = await find_post(post_id)
    if not post:
        logger.error(f"Post with post id {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    # App Join?
    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
