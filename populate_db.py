import asyncio

from time import sleep

import crud
import schemas as schemas
from database import db


async def populate_db():
    class1 = schemas.ClassCreate(name="1.B", user_ids=[])
    class2 = schemas.ClassCreate(name="2.A", user_ids=[])

    class1 = await crud.create_class(db, class1)
    sleep(1)
    class2 = await crud.create_class(db, class2)
    sleep(1)


    course1 = schemas.CourseCreate(name="Biology", user_ids=[])
    course2 = schemas.CourseCreate(name="English", user_ids=[])
    course3 = schemas.CourseCreate(name="Mathematics", user_ids=[])

    course1 = await crud.create_course(db, course1)
    sleep(1)
    course2 = await crud.create_course(db, course2)
    sleep(1)
    course3 = await crud.create_course(db, course3)
    sleep(1)

    student1 = schemas.UserCreate(username="jiri.pap@gmail.com", password="2aoRs2VHXuvPHQ", is_teacher=False)
    student2 = schemas.UserCreate(username="chudovsky@mail.muni.cz", password="4aMfcVKkHLAHDA", is_teacher=False)
    teacher1 = schemas.UserCreate(username="gesvindr@mail.muni.cz", password="rqB4N2pgVWLAW3", is_teacher=True)
    teacher2 = schemas.UserCreate(username="jevocin@mail.muni.cz", password="oZzYb3tN7f8o5D", is_teacher=True)

    student1 = await crud.create_user(db, student1)
    sleep(1)
    student2 = await crud.create_user(db, student2)
    sleep(1)
    teacher1 = await crud.create_user(db, teacher1)
    sleep(1)
    teacher2 = await crud.create_user(db, teacher2)
    sleep(1)

    student1, course1 = await crud.associate_user_course(db, student1, course1)
    sleep(1)
    student1, course2 = await crud.associate_user_course(db, student1, course2)
    sleep(1)
    student1, class1 = await crud.associate_user_class(db, student1, class1)
    sleep(1)

    student2, course2 = await crud.associate_user_course(db, student2, course2)
    sleep(1)
    student2, course3 = await crud.associate_user_course(db, student2, course3)
    sleep(1)
    student2, class1 = await crud.associate_user_class(db, student2, class1)
    sleep(1)
    student2, class2 = await crud.associate_user_class(db, student2, class2)
    sleep(1)

    teacher1, course1 = await crud.associate_user_course(db, teacher1, course1)
    sleep(1)
    teacher1, course2 = await crud.associate_user_course(db, teacher1, course2)
    sleep(1)
    teacher1, class1 = await crud.associate_user_class(db, teacher1, class1)
    sleep(1)

    teacher2, course3 = await crud.associate_user_course(db, teacher2, course3)
    sleep(1)
    teacher2, class2 = await crud.associate_user_class(db, teacher2, class2)

asyncio.run(populate_db())
