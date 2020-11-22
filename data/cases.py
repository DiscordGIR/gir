import mongoengine
from data.case import Case

class Cases(mongoengine.Document):
    _id   = mongoengine.IntField(required=True, unique=True, primary_key=True)
    cases = mongoengine.EmbeddedDocumentListField(Case)
    meta = {
        'db_alias': 'core',
        'collection': 'cases'
    }