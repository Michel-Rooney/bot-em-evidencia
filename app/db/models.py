from datetime import datetime

from peewee import (BigIntegerField, DateTimeField, ForeignKeyField, Model,
                    PostgresqlDatabase)

db = PostgresqlDatabase(
    'defaultdb',
    user='avnadmin',
    password='AVNS_Re_cV99CETaj5e3U5S5',
    host='bot-em-evidencia-michelrooney16.f.aivencloud.com',
    port=24628,
)
# db = PostgresqlDatabase(
#     'postgresql_0ok4',
#     user='postgresql_0ok4_user',
#     password='zOvaNY3BpJ0YONAv0qZAcwtqnn8PtiDj',
#     host='dpg-csbeohaj1k6c73eehd80-a.oregon-postgres.render.com',
#     port=5432,
# )


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
