import mongoengine
import datetime

class Case(mongoengine.EmbeddedDocument):
    _id        = mongoengine.IntField(required=True, unique=True, primary_key=True)
    _type      = mongoengine.StringField()
    date       = mongoengine.DateField(default=datetime.datetime.now)
    until      = mongoengine.DateField(default=None)
    mod_id      = mongoengine.IntField()
    mod_tag    = mongoengine.StringField()
    reason     = mongoengine.StringField()
    punishment = mongoengine.IntField(default=0)