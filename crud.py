import schemas
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user(db, username: str):
    user = await db["users"].find_one({"username": username})
    if user is None:
        return None
    return schemas.User(**user)


async def create_user(db, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = schemas.User(username=user.username, hashed_password=hashed_password, is_teacher=user.is_teacher)
    db_user = jsonable_encoder(db_user)
    new_user = await db['users'].insert_one(db_user)
    created_user = await db['users'].find_one({"_id": new_user.inserted_id})
    return schemas.User(**created_user)


async def get_class(db, id: str):
    a_class = await db['classes'].find_one({"_id": id})
    if a_class is None:
        return None
    return schemas.Class(**a_class)


async def create_class(db, a_class: schemas.ClassCreate):
    db_class = schemas.Class(name=a_class.name)
    db_class = jsonable_encoder(db_class)
    new_class = await db['classes'].insert_one(db_class)
    created_class = await db['classes'].find_one({"_id": new_class.inserted_id})
    return schemas.Class(**created_class)


async def get_course(db, id: str):
    course = await db['courses'].find_one({"_id": id})
    if course is None:
        return None
    return schemas.Course(**course)


async def get_courses(db):
    courses = await db['courses'].find({}).to_list(1000)
    result = []
    for course in courses:
        result.append(schemas.Course(**course))
    return result


async def get_classes(db):
    classes = await db['classes'].find({}).to_list(1000)
    result = []
    for a_class in classes:
        result.append(schemas.Course(**a_class))
    return result


async def create_course(db, course: schemas.CourseCreate):
    db_course = schemas.Class(name=course.name)
    db_course = jsonable_encoder(db_course)
    new_course = await db['courses'].insert_one(db_course)
    created_course = await db['courses'].find_one({"_id": new_course.inserted_id})
    return schemas.Course(**created_course)


async def associate_user_course(db, user: schemas.User, course: schemas.Course):
    new_user = user
    new_user.course_ids.append(str(course.id))
    update_result = await db['users'].update_one({"_id": str(user.id)}, {"$set": {"course_ids": new_user.course_ids}})
    updated_user = await db['users'].find_one({"_id": str(user.id)})

    new_course = course
    new_course.user_ids.append(str(updated_user['_id']))
    update_result = await db['courses'].update_one({"_id": str(course.id)}, {"$set": {"user_ids": new_course.user_ids}})
    updated_course = await db['courses'].find_one({"_id": str(course.id)})

    return schemas.User(**updated_user), schemas.Course(**updated_course)


async def associate_user_class(db, user: schemas.User, a_class: schemas.Class):
    new_user = user
    new_user.class_ids.append(str(a_class.id))
    update_result = await db['users'].update_one({"_id": str(user.id)}, {"$set": {"class_ids": new_user.class_ids}})
    updated_user = await db['users'].find_one({"_id": str(user.id)})

    new_class = a_class
    new_class.user_ids.append(str(updated_user['_id']))
    new_class = await db['classes'].update_one({"_id": str(a_class.id)}, {"$set": {"user_ids": new_class.user_ids}})
    updated_class = await db['classes'].find_one({"_id": str(a_class.id)})

    return schemas.User(**updated_user), schemas.Class(**updated_class)


async def create_post_in_course(db, text: str, user: schemas.User, course: schemas.Course):
    db_post = schemas.Post(text=text, author_id=str(user.id), course_id=str(course.id))
    db_post = jsonable_encoder(db_post)
    new_post = await db['posts'].insert_one(db_post)
    created_post = await db['posts'].find_one({'_id': new_post.inserted_id})
    return schemas.Post(**created_post)


async def create_post_in_class(db, text: str, user: schemas.User, a_class: schemas.Class):
    db_post = schemas.Post(text=text, author_id=str(user.id), class_id=str(a_class.id))
    db_post = jsonable_encoder(db_post)
    new_post = await db['posts'].insert_one(db_post)
    created_post = await db['posts'].find_one({'_id': new_post.inserted_id})
    return schemas.Post(**created_post)


async def get_posts_for_course(db, course_id):
    posts = await db['posts'].find({'course_id': course_id}).to_list(1000)
    return posts


async def get_posts_for_class(db, class_id):
    posts = await db['posts'].find({'class_id': class_id}).to_list(1000)
    return posts


async def get_post(db, id: str):
    post = await db['posts'].find_one({"_id": id})
    if post is None:
        return None
    return schemas.Post(**post)


async def remove_post(db, post: schemas.Post):
    result = await db['posts'].delete_one({'_id': str(post.id)})
    return result


async def like_post(db, post: schemas.Post, user: schemas.User):
    user.likes_post_ids.append(str(post.id))
    update_result = await db['users'].update_one({'_id': str(user.id)},
                                                 {"$set": {"likes_post_ids": user.likes_post_ids}})
    updated_user = await db['users'].find_one({"_id": str(user.id)})

    post.likes_user_ids.append(str(user.id))
    update_result = await db['posts'].update_one({'_id': str(post.id)},
                                                 {"$set": {"likes_user_ids": post.likes_user_ids}})
    updated_post = await db['posts'].find_one({"_id": str(post.id)})

    return updated_user, updated_post


async def remove_like_from_post(db, post: schemas.Post, user: schemas.User):
    user.likes_post_ids.remove(str(post.id))
    update_result = await db['users'].update_one({'_id': str(user.id)},
                                                 {"$set": {"likes_post_ids": user.likes_post_ids}})
    updated_user = await db['users'].find_one({"_id": str(user.id)})

    post.likes_user_ids.remove(str(user.id))
    update_result = await db['posts'].update_one({'_id': str(post.id)},
                                                 {"$set": {"likes_user_ids": post.likes_user_ids}})
    updated_post = await db['posts'].find_one({"_id": str(post.id)})

    return updated_user, updated_post


async def create_comment(db, text: str, post: schemas.Post, user: schemas.User):
    db_comment = schemas.Comment(text=text, post_id=str(post.id), author_id=str(user.id))
    db_comment = jsonable_encoder(db_comment)
    new_comment = await db['comments'].insert_one(db_comment)
    created_comment = await db['comments'].find_one({'_id': new_comment.inserted_id})

    post.comment_ids.append(created_comment['_id'])
    update_result = await db['posts'].update_one({'_id': str(post.id)},
                                                 {"$set": {"comment_ids": post.comment_ids}})
    updated_post = await db['posts'].find_one({"_id": str(post.id)})

    return schemas.Comment(**created_comment)


async def get_comments_for_post(db, post: schemas.Post):
    comments = await db['comments'].find({'post_id': str(post.id)}).to_list(1000)
    return comments


async def get_comment(db, id: str):
    comment = await db['comments'].find_one({"_id": id})
    if comment is None:
        return None
    return schemas.Comment(**comment)


async def remove_comment(db, comment: schemas.Comment):
    result = await db['comments'].delete_one({'_id': str(comment.id)})
    return result


async def like_comment(db, comment: schemas.Comment, user: schemas.User):
    user.likes_comment_ids.append(str(comment.id))
    update_result = await db['users'].update_one({'_id': str(user.id)},
                                                 {"$set": {"likes_comment_ids": user.likes_comment_ids}})
    updated_user = await db['users'].find_one({"_id": str(user.id)})

    comment.likes_user_ids.append(str(user.id))
    update_result = await db['comments'].update_one({'_id': str(comment.id)},
                                                 {"$set": {"likes_user_ids": comment.likes_user_ids}})
    updated_comment = await db['comments'].find_one({"_id": str(comment.id)})

    return updated_user, updated_comment


async def remove_like_from_comment(db, comment: schemas.Comment, user: schemas.User):
    user.likes_comment_ids.remove(str(comment.id))
    update_result = await db['users'].update_one({'_id': str(user.id)},
                                                 {"$set": {"likes_comment_ids": user.likes_comment_ids}})
    updated_user = await db['users'].find_one({"_id": str(user.id)})

    comment.likes_user_ids.remove(str(user.id))
    update_result = await db['comments'].update_one({'_id': str(comment.id)},
                                                 {"$set": {"likes_user_ids": comment.likes_user_ids}})
    updated_comment = await db['comments'].find_one({"_id": str(comment.id)})

    return updated_user, updated_comment
