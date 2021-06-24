import mongoengine

class FilterCategory(mongoengine.Document):
    name                    = mongoengine.StringField(required=True)
    description             = mongoengine.StringField(required=True)
    color                   = mongoengine.StringField(required=True)
    post_in_public          = mongoengine.BooleanField(required=True)
    delete_original_message = mongoengine.BooleanField(required=True)
