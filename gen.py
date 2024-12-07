import random
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import User, Group, UserToGroup, Task, TaskToUser, Base


def generate_data(session, ratio=10):
    faker = Faker()
    users = []
    for _ in range(ratio):
        login = faker.unique.user_name()
        tag = faker.unique.word() + str(random.randint(1, 10_000))
        user = User(
            login=login,
            tag=tag,
            password=faker.password(),
            profile_image=faker.image_url()
        )
        users.append(user)
    session.add_all(users)
    session.commit()

    groups = []
    for user in users:
        group_name = faker.unique.company()
        group = Group(
            name=group_name,
            description=faker.text(max_nb_chars=50),
            image=faker.image_url(),
            owner_id=user.id
        )
        groups.append(group)
    session.add_all(groups)
    session.commit()

    for group in groups:
        utg = UserToGroup(group_id=group.id, user_id=group.owner_id)
        session.add(utg)

    user_for_multiple_groups = users[0]
    additional_groups = random.sample(groups, min(3, len(groups)))
    for g in additional_groups:
        if g.owner_id != user_for_multiple_groups.id:
            utg = UserToGroup(group_id=g.id, user_id=user_for_multiple_groups.id)
            session.add(utg)
    session.commit()

    tasks = []
    for group in groups:
        for _ in range(2):
            task_name = faker.unique.catch_phrase()
            task = Task(
                group_id=group.id,
                owner_id=group.owner_id,
                name=task_name,
                summary=faker.sentence(),
                description=faker.text(max_nb_chars=200),
                deadline=faker.future_datetime(),
                status=random.randint(0, 3)
            )
            tasks.append(task)
    session.add_all(tasks)
    session.commit()

    group_memberships = session.query(UserToGroup).all()
    group_to_users = {}
    for mem in group_memberships:
        group_to_users.setdefault(mem.group_id, []).append(mem.user_id)

    all_task_to_users = []
    for task in tasks:
        possible_users = group_to_users.get(task.group_id, [])
        if not possible_users:
            possible_users = [task.owner_id]
        num_assignees = random.randint(1, min(3, len(possible_users)))
        assignees = random.sample(possible_users, num_assignees)
        for user_id in assignees:
            ttu = TaskToUser(
                user_id=user_id,
                task_id=task.id
            )
            all_task_to_users.append(ttu)
    session.add_all(all_task_to_users)
    session.commit()


if __name__ == "__main__":
    engine = create_engine('sqlite:///database.db', echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    generate_data(session, ratio=20)
