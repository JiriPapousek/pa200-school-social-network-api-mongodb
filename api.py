import schemas
import auth
import logging
import crud

from database import db
from auth import get_current_active_user

from fastapi import Depends, status, FastAPI, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from schemas import User
import tools

app = FastAPI()
logger = logging.getLogger('uvicorn.error')


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user, auth_passed = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not auth_passed:
        if user is not None:
            await tools.send_failed_auth_message(user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/courses")
async def get_courses(current_user: User = Depends(get_current_active_user)):
    courses = await crud.get_courses(db)
    return courses


@app.get("/classes")
async def get_courses(current_user: User = Depends(get_current_active_user)):
    classes = await crud.get_classes(db)
    return classes


@app.post("/course/{course_id}/post")
async def create_post_in_course(text: str,
                                course_id: str,
                                current_user: User = Depends(get_current_active_user)):
    course_found = False

    for user_course_id in current_user.course_ids:
        if course_id == user_course_id:
            course_found = True
            break

    course = await crud.get_course(db, course_id)
    if course is None:
        course_found = False

    if not course_found:
        raise HTTPException(status_code=400,
                            detail="Invalid course ID; either does not exist, or user does not have an access")
    post = await crud.create_post_in_course(db, text, current_user, course)
    return post


@app.post("/class/{class_id}/post")
async def create_post_in_class(text: str,
                                class_id: str,
                                current_user: User = Depends(get_current_active_user)):
    class_found = False

    for user_class_id in current_user.class_ids:
        if class_id == user_class_id:
            class_found = True
            break

    a_class = await crud.get_class(db, class_id)
    if a_class is None:
        class_found = False

    if not class_found:
        raise HTTPException(status_code=400,
                            detail="Invalid class ID; either does not exist, or user does not have an access")
    post = await crud.create_post_in_class(db, text, current_user, a_class)
    return post


@app.get("/course/{course_id}/wall")
async def get_wall_for_course(course_id: str,
                             current_user: User = Depends(get_current_active_user)):
    if course_id not in current_user.course_ids:
        raise HTTPException(status_code=400,
                            detail="Invalid course ID; either does not exist, or user does not have an access")
    posts = await crud.get_posts_for_course(db, course_id)
    return posts


@app.get("/class/{class_id}/wall")
async def get_wall_for_class(class_id: str,
                             current_user: User = Depends(get_current_active_user)):
    if class_id not in current_user.class_ids:
        raise HTTPException(status_code=400,
                            detail="Invalid class ID; either does not exist, or user does not have an access")
    posts = await crud.get_posts_for_class(db, class_id)
    return posts


@app.get("/user/info")
async def user_info(current_user: User = Depends(get_current_active_user)):
    user = schemas.UserPermissions(**dict(current_user))
    return user


@app.delete("/post/post_id}")
async def remove_post(post_id: str,
                      current_user: User = Depends(get_current_active_user)):
    post = await crud.get_post(db, post_id)
    logger.info(post)
    if post is None:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    elif post.author_id != str(current_user.id) and \
       (not current_user.is_teacher or
       (str(post.class_id) not in current_user.class_ids and
       str(post.course_id) not in current_user.course_ids)):
        raise HTTPException(status_code=403,
                            detail="User does not have permissions to delete this post")

    await crud.remove_post(db, post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/wall")
async def get_wall(current_user: User = Depends(get_current_active_user)):
    posts = []
    for class_id in current_user.class_ids:
        posts += await crud.get_posts_for_class(db, class_id)
    for course_id in current_user.course_ids:
        posts += await crud.get_posts_for_course(db, course_id)
    return posts


@app.post("/post/{post_id}/like")
async def like_post(post_id: str,
                    current_user: User = Depends(get_current_active_user)):
    post = await crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    elif post.author_id != str(current_user.id) and \
       str(post.class_id) not in current_user.class_ids and \
       str(post.course_id) not in current_user.course_ids:
        raise HTTPException(status_code=403,
                            detail="User does not have an access to given post")
    elif str(current_user.id) in post.likes_user_ids:
        raise HTTPException(status_code=400, detail="User already liked this post")
    _, post = await crud.like_post(db, post, current_user)
    return post


@app.delete("/post/{post_id}/like")
async def remove_like_from_post(post_id: str,
                    current_user: User = Depends(get_current_active_user)):
    post = await crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    elif post.author_id != str(current_user.id) and \
         str(post.class_id) not in current_user.class_ids and \
         str(post.course_id) not in current_user.course_ids:
        raise HTTPException(status_code=403,
                            detail="User does not have an access to given post")
    elif str(current_user.id) not in post.likes_user_ids:
        raise HTTPException(status_code=400, detail="User has not liked this post")
    await crud.remove_like_from_post(db, post, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/post/{post_id}/comment")
async def add_comment(text: str,
                      post_id: str,
                      current_user: User = Depends(get_current_active_user)):
    post = await crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    elif post.author_id != str(current_user.id) and \
         str(post.class_id) not in current_user.class_ids and \
         str(post.course_id) not in current_user.course_ids:
        raise HTTPException(status_code=403,
                            detail="User does not have an access to given post")
    comment = await crud.create_comment(db, text, post, current_user)
    return comment


@app.get("/post/{post_id}/comments")
async def get_comments(post_id: str,
                       current_user: User = Depends(get_current_active_user)):
    post = await crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    elif post.author_id != str(current_user.id) and \
         str(post.class_id) not in current_user.class_ids and \
         str(post.course_id) not in current_user.course_ids:
        raise HTTPException(status_code=403,
                            detail="User does not have an access to given post")

    comments = await crud.get_comments_for_post(db, post)
    return comments


@app.delete("/comment/{comment_id}")
async def remove_comment(comment_id: str,
                         current_user: User = Depends(get_current_active_user)):
    comment = await crud.get_comment(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=400, detail="Invalid comment ID")
    post = await crud.get_post(db, comment.post_id)
    if comment.author_id != str(current_user.id) and \
        str(post.class_id) not in current_user.class_ids and \
        str(post.course_id) not in current_user.course_ids:
        raise HTTPException(status_code=403,
                            detail="User does not have an access to the given comment")

    await crud.remove_comment(db, comment)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/comment/{comment_id}/like")
async def like_comment(comment_id: str,
                       current_user: User = Depends(get_current_active_user)):
    comment = await crud.get_comment(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=400, detail="Invalid comment ID")
    post = await crud.get_post(db, comment.post_id)
    if comment.author_id != str(current_user.id) and \
        str(post.class_id) not in current_user.class_ids and \
        str(post.course_id) not in current_user.course_ids:
        raise HTTPException(status_code=403,
                            detail="User does not have an access to the given comment")
    if str(current_user.id) in comment.likes_user_ids:
        raise HTTPException(status_code=400, detail="User already liked this comment")
    _, comment = await crud.like_comment(db, comment, current_user)
    return comment


@app.delete("/comment/{comment_id}/like")
async def remove_like_from_comment(comment_id: str,
                                   current_user: User = Depends(get_current_active_user)):
    comment = await crud.get_comment(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=400, detail="Invalid comment ID")
    post = await crud.get_post(db, comment.post_id)
    if comment.author_id != str(current_user.id) and \
        str(post.class_id) not in current_user.class_ids and \
        str(post.course_id) not in current_user.course_ids:
        raise HTTPException(status_code=403,
                            detail="User does not have an access to the given comment")
    if str(current_user.id) not in comment.likes_user_ids:
        raise HTTPException(status_code=400, detail="User has not liked this comment")

    await crud.remove_like_from_comment(db, comment, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)