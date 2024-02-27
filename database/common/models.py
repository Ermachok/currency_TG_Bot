from datetime import datetime

import peewee as pw

db = pw.SqliteDatabase('NEV_tgBot.db')


class ModelBase(pw.Model):
    created_date = pw.DateField(default=datetime.now())

    class Meta():
        database = db


class History(ModelBase):
    name = pw.TextField()
    request = pw.TextField()
    from_currency = pw.TextField()
    to_currency = pw.TextField()
    answer = pw.TextField()
