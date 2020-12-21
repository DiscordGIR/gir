import mongoengine
from datetime import datetime

class Tag(mongoengine.EmbeddedDocument):
    name         = mongoengine.StringField(required=True)
    content      = mongoengine.StringField(required=True)
    added_by_tag = mongoengine.StringField()
    added_by_id  = mongoengine.IntField()
    added_date   = mongoengine.DateTimeField(default=datetime.now)
 