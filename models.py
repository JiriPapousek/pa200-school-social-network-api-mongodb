from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from database import Base


post_likes_table = Table(
    "post_likes",
    Base.metadata,
    Column("username", ForeignKey("users.username"), primary_key=True),
    Column("post_id", ForeignKey("posts.id"), primary_key=True)
)


comment_likes_table = Table(
    "comment_likes",
    Base.metadata,
    Column("username", ForeignKey("users.username"), primary_key=True),
    Column("comment_id", ForeignKey("comments.id"), primary_key=True)
)


class UserClassAssociation(Base):
    __tablename__ = "user_class"

    username = Column(ForeignKey("users.username"), primary_key=True)
    class_id = Column(ForeignKey("classes.id"), primary_key=True)
    from_date = Column(DateTime())
    to_date = Column(DateTime())

    in_class = relationship("Class", back_populates="users_associations", lazy='subquery')
    user = relationship("User", back_populates="classes_associations", lazy='subquery')


class UserCourseAssociation(Base):
    __tablename__ = "user_course"

    username = Column(ForeignKey("users.username"), primary_key=True)
    course_id = Column(ForeignKey("courses.id"), primary_key=True)
    from_date = Column(DateTime())
    to_date = Column(DateTime())

    user = relationship("User", back_populates="courses_associations", lazy='subquery')
    in_course = relationship("Course", back_populates="users_associations", lazy='subquery')


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    is_teacher = Column(Boolean)

    likes_posts = relationship("Post", secondary=post_likes_table, back_populates="likes", lazy='subquery')
    likes_comments = relationship("Comment", secondary=comment_likes_table, back_populates="likes", lazy='subquery')
    posts = relationship("Post", back_populates="author", lazy='subquery')
    comments = relationship("Comment", back_populates="author", lazy='subquery')
    classes_associations = relationship("UserClassAssociation", back_populates="user", lazy='subquery')
    courses_associations = relationship("UserCourseAssociation", back_populates="user", lazy='subquery')


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    date = Column(DateTime())
    author_username = Column(ForeignKey("users.username"))
    class_id = Column(ForeignKey("classes.id"))
    course_id = Column(ForeignKey("courses.id"))

    author = relationship("User", back_populates="posts")
    likes = relationship("User", secondary=post_likes_table, back_populates="likes_posts")
    comments = relationship("Comment", back_populates="post")
    in_class = relationship("Class", back_populates="posts")
    in_course = relationship("Course", back_populates="posts")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    users_associations = relationship("UserClassAssociation", back_populates="in_class")
    posts = relationship("Post", back_populates="in_class")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    users_associations = relationship("UserCourseAssociation", back_populates="in_course")
    posts = relationship("Post", back_populates="in_course")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    date = Column(DateTime())
    author_username = Column(ForeignKey("users.username"))
    post_id = Column(ForeignKey("posts.id"))

    author = relationship("User", back_populates="comments")
    likes = relationship("User", secondary=comment_likes_table, back_populates="likes_comments")
    post = relationship("Post", back_populates="comments")

