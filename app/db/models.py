from datetime import datetime

from peewee import (DateTimeField, ForeignKeyField, IntegerField, Model,
                    PostgresqlDatabase, TimeField)

# db = PostgresqlDatabase()
# db = PostgresqlDatabase(
# )
db = ''


class User(Model):
    discord = IntegerField(unique=True)
    guild = IntegerField()
    xp = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)


class Study(Model):
    user = ForeignKeyField(User, backref='users')
    start_time = TimeField(null=True)
    end_time = TimeField(null=True)
    total_time = IntegerField(default=0)
    xp = IntegerField(default=0)
    channel = IntegerField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
