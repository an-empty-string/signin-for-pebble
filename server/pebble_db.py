from peewee import *
database = SqliteDatabase('peewee.db')

class BaseModel(Model):
    class Meta:
        db = database

class User(BaseModel):
    username = TextField()
    password = TextField()

class Device(BaseModel):
    auth_key = TextField()
    enroll_key = TextField()
    owner = ForeignKeyField(User, related_name='devices', null=True)

class AuthRequest(BaseModel):
    user = ForeignKeyField(User, related_name='auth_requests')
    service = TextField()
    complete = BooleanField(default=False)
    completed_at = DateTimeField(null=True)
    approved = BooleanField(default=False)

try:
    User.create_table()
    Device.create_table()
    AuthRequest.create_table()
except:
    pass
