import logging
from enum import Enum
from typing import Annotated

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException

from socialapi.database import comment_table, database, like_table, post_table
from socialapi.models.post import (
    Comment,
    CommentIn,
    PostLike,
    PostLikeIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
    UserPostWithLikes,
)
from socialapi.models.user import User
from socialapi.security import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)

# promise처럼 바로 return 해도 되나?

select_post_and_likes = (
    sqlalchemy.select(post_table, sqlalchemy.func.count(like_table.c.id).label("likes"))
    .select_from(post_table.outerjoin(like_table))
    .group_by(post_table.c.id)
)


async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)

    return await database.fetch_one(query)


@router.post("", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info("Creating post")

    data = {**dict(post), "user_id": current_user.id}
    query = post_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)

    return {**data, "id": last_record_id}


class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_likes = "most_likes"


@router.get("", response_model=list[UserPostWithLikes])
async def get_all_posts(sorting: PostSorting = PostSorting.new):
    logger.info("Getting all posts")  # 데코레이터로 요런 걸 직접 만들수도

    """
    match sorting:
        case PostSorting.new:
            query = select_post_and_likes.order_by(post_table.c.id.desc())
    """

    if sorting == PostSorting.new:
        query = select_post_and_likes.order_by(post_table.c.id.desc())
    elif sorting == PostSorting.old:
        query = select_post_and_likes.order_by(post_table.c.id.asc())
    elif sorting == PostSorting.most_likes:
        query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))

    logger.debug(query)

    return await database.fetch_all(query)


@router.post("/comments", response_model=Comment, status_code=201)
async def create_comment(
    comment: CommentIn,
    current_user: Annotated[User, Depends(get_current_user)],
):
    logger.info("Creating comment")

    post = await find_post(comment.post_id)
    if not post:
        logger.error(f"Post with id {comment.post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**dict(comment), "user_id": current_user.id}
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

    query = select_post_and_likes.where(post_table.c.id == post_id)
    logger.debug(query)

    post = await database.fetch_one(query)
    if not post:
        logger.error(f"Post with post id {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    # App Join?
    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }


@router.post("/like", response_model=PostLike, status_code=201)
async def like_post(
    like: PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info("Liking post")

    post = await find_post(like.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**dict(like), "user_id": current_user.id}
    query = like_table.insert().values(data)

    logger.debug(query)
    last_record_id = await database.execute(query)

    return {**data, "id": last_record_id}
