from lazysql import Base, update_all, viewtable, db


class User(Base):
    __tablename__ = 'users'
    user_id = ('SERIAL', 'PRIMARY KEY')
    username = ('varchar(256)', 'NOT NULL')


class Post(Base):
    __tablename__ = 'posts'
    post_id = ('SERIAL', 'PRIMARY KEY')
    text = ('varchar', 'NOT NULL')

update_all()

a = User()
print(a.username)
a.create(user_id=29, username='john')
print(a.username)
b = a.selectone(user_id=29)
print(b.username)
print(viewtable(User))

db.close()

