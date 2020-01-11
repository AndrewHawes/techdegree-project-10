from peewee import *

DATABASE = SqliteDatabase('todos.db')


class Todo(Model):
    name = CharField()
    completed = BooleanField(default=False)

    class Meta:
        database = DATABASE


def initialize():  # pragma: no cover
    DATABASE.connect(reuse_if_open=True)
    DATABASE.create_tables([Todo], safe=True)
    DATABASE.close()
