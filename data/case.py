import mongoengine
import datetime

class Case(mongoengine.EmbeddedDocument):
    _id        = mongoengine.IntField(required=True, unique=True, primary_key=True)
    _type      = mongoengine.StringField()
    date       = mongoengine.DateField(default=datetime.now)
    until      = mongoengine.DateField(default=None)
    modID      = mongoengine.IntField()
    modTag     = mongoengine.StringField()
    reason     = mongoengine.StringField()
    punishment = mongoengine.StringField()