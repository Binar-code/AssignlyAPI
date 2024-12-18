import datetime
import json

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends, Query, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from codes import *
from models import *

tokens = []
Base.metadata.create_all(bind=engine)
app = FastAPI()

STATIC_DIR = './static'
PROFILE_PIC_DIR = f'{STATIC_DIR}/profiles'
GROUP_PIC_DIR = f'{STATIC_DIR}/groups'


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def auth(token):
    is_auth = False
    id = 0
    for item in tokens:
        if item['token'] == token:
            is_auth = True
            id = item['id']
            break

    return is_auth, id


@app.get("/get_image")
def get_image(path: str = Form(...)):
    return FileResponse(path=path)


@app.get("/login")
def login(login, password, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == login).first()
    if user == None:
        return JSONResponse({'message': 'user not found'}, status_code=NOT_FOUND)

    if user.password != password:
        return JSONResponse({'message': 'incorrect password'}, status_code=BAD_REQUEST)

    data = {
        'id': user.id,
        'token': '1'  # secrets.token_hex()
    }

    json = jsonable_encoder(data)
    tokens.append(data)
    return JSONResponse(content=json, status_code=OK)


@app.get('/groups')
def groups_list(token, db: Session = Depends(get_db)):
    is_auth, id = auth(token)
    if is_auth:
        groups_id = db.query(UserToGroup).filter(UserToGroup.user_id == id)
        groups = []
        for item in groups_id:
            groups.append(db.get(Group, item.group_id))
        data = []
        for item in groups:
            users = db.query(UserToGroup).filter(UserToGroup.group_id == item.id)
            members = []
            for i in users:
                user = db.get(User, i.user_id)
                members.append({
                    'id': user.id,
                    'login': user.login,
                    'tag': user.tag,
                    'profile_image': user.profile_image
                })
            data.append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'image': item.image,
                'owner_id': item.owner_id,
                'members': members
            })

        json = jsonable_encoder(data)
        return JSONResponse(content=json, status_code=OK)
    else:
        return JSONResponse({'message': 'unauthorized'}, status_code=UNAUTHORIZED)


@app.get('/tasks')
def tasks(token, group_id, limit, offset, db: Session = Depends(get_db)):
    is_auth, id = auth(token)
    if is_auth:
        tasks = db.query(Task).filter(Task.group_id == group_id)
        data = []
        cur = int(offset)
        while cur < (int(offset) + int(limit)) and cur < tasks.count():
            task = tasks[cur]
            users = db.query(TaskToUser).filter(TaskToUser.task_id == task.id)
            members = []
            for i in users:
                member = db.get(User, i.user_id)
                members.append({
                    'id': member.id,
                    'login': member.login,
                    'tag': member.tag,
                    'profile_image': member.profile_image
                })
            data.append({
                'id': task.id,
                'group_id': task.group_id,
                'owner_id': task.owner_id,
                'name': task.name,
                'summary': task.summary,
                'description': task.description,
                'deadline': task.deadline,
                'status': task.status,
                'members': members
            })
            cur += 1

        json = jsonable_encoder(data)
        return JSONResponse(content=json, status_code=OK)
    else:
        return JSONResponse({'message': 'unauthorized'}, status_code=UNAUTHORIZED)


@app.post('/signup', response_model=None)
def add_user(login: str = Form(...),
             tag: str = Form(...),
             password: str = Form(...),
             img: UploadFile = File(None),
             db: Session = Depends(get_db)):
    if (db.query(User).filter(User.login == login).first() is not None
            or db.query(User).filter(User.tag == tag).first() is not None):
        return JSONResponse({'message': 'User already exist'}, status_code=CONFLICT)

    user = User(
        login=login,
        tag=tag,
        password=password,
    )

    if img:
        file_path = f"{PROFILE_PIC_DIR}/{img.filename}"
        with open(file_path, "wb") as f:
            f.write(img.file.read())
        user.profile_image = file_path

    db.add(user)
    db.commit()
    return JSONResponse({'id': user.id}, status_code=OK)


@app.post('/add_task')
def add_task(token, group_id, name, summary, description, deadline,
             status, members: list = Query(), db: Session = Depends(get_db)):
    try:
        valid_date = datetime.datetime.strptime(deadline, '%d.%m.%Y %H:%M')
    except ValueError:
        return JSONResponse({'message': 'Invalid date'}, status_code=BAD_REQUEST)

    is_auth, id = auth(token)

    if is_auth:
        if db.query(Task).filter(Task.name == name, Task.owner_id == id).first() is not None:
            return JSONResponse({'message': 'task with same name already exist'}, status_code=BAD_REQUEST)

        task = Task(
            group_id=group_id,
            owner_id=id,
            name=name,
            summary=summary,
            description=description,
            deadline=valid_date,
            status=status
        )

        db.add(task)
        db.commit()
        task_id = task.id

        data = json.loads(members[0])
        for i in data:
            if not i:
                break
            db.add(TaskToUser(
                user_id=int(i['id']),
                task_id=task_id
            ))
        db.add(TaskToUser(
            user_id=id,
            task_id=task_id
        ))
        db.commit()

        return JSONResponse({'id': task.id}, status_code=OK)
    else:
        return JSONResponse({'message': 'unauthorized'}, status_code=UNAUTHORIZED)


@app.get('/users')
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    data = []
    for item in users:
        data.append({
            'id': item.id,
            'login': item.login,
            'tag': item.tag,
            'profile_image': item.profile_image
        })

    json = jsonable_encoder(data)

    return JSONResponse(content=json, status_code=OK)


@app.get('/user_by_id')
def user_by_id(id, db: Session = Depends(get_db)):
    user = db.get(User, id)
    if user is None:
        return JSONResponse({'message': 'user not found'}, status_code=NOT_FOUND)

    return JSONResponse(
        {
            'id': user.id,
            'login': user.login,
            'tag': user.tag,
            'profile_image': user.profile_image
        },
        status_code=OK
    )


@app.post('/logout')
def logout(token):
    is_auth, id = auth(token)
    if not is_auth:
        return JSONResponse({'message': 'token not found'}, status_code=BAD_REQUEST)

    index = 0
    for i, item in enumerate(tokens):
        if item['id'] == int(id):
            index = i
            break

    tokens.pop(index)
    return JSONResponse({'message': 'logout successfully'}, status_code=OK)


@app.post('/add_group')
def add_group(
        token: str = Form(...),
        name: str = Form(...),
        description: str = Form(...),
        image: UploadFile = File(None),
        members: list = Form, db: Session = Depends(get_db)):
    is_auth, id = auth(token)
    if is_auth:
        check = db.query(Group).filter(Group.name == name, Group.owner_id == id).first()
        if check is not None:
            return JSONResponse({'message': 'group already exist'}, status_code=BAD_REQUEST)

        group = Group(
            name=name,
            description=description,
            owner_id=id
        )

        if image:
            file_path = f'{GROUP_PIC_DIR}/{image.filename}'
            with open(file_path, 'wb') as f:
                f.write(image.file.read())
            group.image = file_path

        db.add(group)
        db.commit()
        data = json.loads(members[0])
        for i in data:
            if not i:
                break
            db.add(UserToGroup(
                group_id=group.id,
                user_id=int(i['id'])
            ))

        db.add(UserToGroup(
            group_id=group.id,
            user_id=id
        ))
        db.commit()

        return JSONResponse({'id': group.id}, status_code=OK)
    return JSONResponse({'message': 'unauthorized'}, status_code=UNAUTHORIZED)


@app.get('/group_by_id')
def group_by_id(token, group_id, db: Session = Depends(get_db)):
    is_auth, id = auth(token)
    if is_auth:
        group = db.get(Group, group_id)
        if group is None:
            return JSONResponse({'message:': 'group not found'}, status_code=NOT_FOUND)

        members = db.query(UserToGroup).filter(UserToGroup.group_id == group_id)
        members_id = [i.user_id for i in members]
        print(members_id)

        if id not in members_id:
            return JSONResponse({'message': 'can not access group'}, status_code=UNAUTHORIZED)

        data = []

        for i in members_id:
            member = db.get(User, i)
            print(member)
            data.append({
                'id': member.id,
                'login': member.login,
                'tag': member.tag
            })

        return JSONResponse({
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'image': group.image,
            'owner_id': group.owner_id,
            'members': data
        }, status_code=OK)
    else:
        return JSONResponse({'message': 'unauthorized'}, status_code=UNAUTHORIZED)


@app.get('/task_by_id')
def task_by_id(token, task_id, db: Session = Depends(get_db)):
    is_auth, id = auth(token)

    if is_auth:
        task = db.get(Task, task_id)

        if (task.owner_id != id):
            return JSONResponse({'message': 'can not access task'}, status_code=UNAUTHORIZED)

        members = db.query(TaskToUser).filter(TaskToUser.task_id == task_id)
        data = []

        for item in members:
            member = db.get(User, item.user_id)
            data.append({
                'id': member.id,
                'login': member.login,
                'tag': member.tag
            })

        return JSONResponse({
            'id': task_id,
            'group_id': task.group_id,
            'owner_id': task.owner_id,
            'name': task.name,
            'summary': task.summary,
            'description': task.description,
            'status': task.status,
            'members': data
        })
    else:
        return JSONResponse({'message': 'unauthorized'}, status_code=UNAUTHORIZED)


@app.post("/status_change")
def status_change(token, task_id, status, db: Session = Depends(get_db)):
    is_auth, id = auth(token)

    if is_auth:
        task = db.get(Task, task_id)
        if task.owner_id != id:
            return JSONResponse({'message': 'can not access task'}, status_code=UNAUTHORIZED)
        db.query(Task).filter(Task.id == task_id).update({Task.status: status})
        db.commit()
        return JSONResponse({'message': 'status updated'}, status_code=OK)

    else:
        return JSONResponse({'message': 'unauthorized'}, status_code=UNAUTHORIZED)
