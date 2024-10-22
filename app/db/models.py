from datetime import datetime

from decouple import config
from peewee import (BigIntegerField, DateTimeField, ForeignKeyField, Model,
                    PostgresqlDatabase)

DB_NAME = config('DB_NAME', '')
DB_USER = config('DB_USER', '')
DB_PASSWORD = config('DB_PASSWORD', '')
DB_HOST = config('DB_HOST', '')
DB_PORT = int(config('DB_PORT', ''))

db = PostgresqlDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)


class User(Model):
    discord = BigIntegerField(unique=True)
    guild = BigIntegerField()
    xp = BigIntegerField(default=0)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)


class Study(Model):
    user = ForeignKeyField(User, backref='users')
    start_time = DateTimeField(default=datetime.now)
    end_time = DateTimeField(null=True)
    total_time = BigIntegerField(default=0)
    xp = BigIntegerField(default=0)
    channel = BigIntegerField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
