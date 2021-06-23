import mongoengine
from data.filtercategory import FilterCategory

class FilterWord(mongoengine.EmbeddedDocument):
    # _id    = mongoengine.ObjectIdField(required=True, default=mongoengine.ObjectId., unique=True, primary_key=True)
    notify               = mongoengine.BooleanField(required=True)
    bypass               = mongoengine.IntField(required=True)
    word                 = mongoengine.StringField(required=True)
    false_positive       = mongoengine.BooleanField(default=False)
    category             = mongoengine.EmbeddedDocumentField(FilterCategory, default=None)
