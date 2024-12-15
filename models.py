from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy import create_engine

Base = declarative_base()
DB_URL = "sqlite:///database.db"
engine = create_engine(
    DB_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autoflush=True, bind=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, nullable=False, unique=True)
    tag = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    profile_image = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())

    owned_groups = relationship('Group', back_populates='owner', cascade='all, delete-orphan')
    tasks_owned = relationship('Task', back_populates='owner', cascade='all, delete-orphan')
    tasks_assigned = relationship('TaskToUser', back_populates='user', cascade='all, delete-orphan')
    groups_membership = relationship('UserToGroup', back_populates='user', cascade='all, delete-orphan')


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    image = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())

    owner = relationship('User', back_populates='owned_groups')
    members = relationship('UserToGroup', back_populates='group', cascade='all, delete-orphan')
    tasks = relationship('Task', back_populates='group', cascade='all, delete-orphan')


class UserToGroup(Base):
    __tablename__ = 'user_to_group'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    group = relationship('Group', back_populates='members')
    user = relationship('User', back_populates='groups_membership')


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'))
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    name = Column(String, nullable=False, unique=True)
    summary = Column(String, nullable=False)
    description = Column(String, nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=False)
    status = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())

    group = relationship('Group', back_populates='tasks')
    owner = relationship('User', back_populates='tasks_owned')
    assigned_users = relationship('TaskToUser', back_populates='task', cascade='all, delete-orphan')


class TaskToUser(Base):
    __tablename__ = 'task_to_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'))

    user = relationship('User', back_populates='tasks_assigned')
    task = relationship('Task', back_populates='assigned_users')
