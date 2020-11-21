import mongoengine

class Guild(mongoengine.Document):
    _id                       = mongoengine.IntField(required=True, unique=True, primary_key=True)
    
    role_mute                 = mongoengine.IntField()
    role_genius               = mongoengine.IntField()
    role_moderator            = mongoengine.IntField()
    role_memberplus           = mongoengine.IntField()
    role_memberpro            = mongoengine.IntField()
    role_memberedition        = mongoengine.IntField()
    role_member               = mongoengine.IntField()
    
    channel_public            = mongoengine.IntField()
    channel_private           = mongoengine.IntField()
    channel_reports           = mongoengine.IntField()
    channel_botspam           = mongoengine.IntField()
    
    logging_excluded_channels = mongoengine.ListField(default=[])

