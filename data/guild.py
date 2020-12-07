import mongoengine
from data.filterword import FilterWord

class Guild(mongoengine.Document):
    _id                       = mongoengine.IntField(required=True)
    case_id                   = mongoengine.IntField(min_value=1, required=True)
    role_mute                 = mongoengine.IntField()
    role_genius               = mongoengine.IntField()
    role_moderator            = mongoengine.IntField()
    role_memberplus           = mongoengine.IntField()
    role_memberpro            = mongoengine.IntField()
    role_memberedition        = mongoengine.IntField()
    role_member               = mongoengine.IntField()
    role_dev                  = mongoengine.IntField()
    
    channel_public            = mongoengine.IntField()
    channel_private           = mongoengine.IntField()
    channel_reports           = mongoengine.IntField()
    channel_botspam           = mongoengine.IntField()
    
    nsa_guild_id              = mongoengine.IntField()
    nsa_mapping               = mongoengine.DictField(default={})
    logging_excluded_channels = mongoengine.ListField(default=[])
    filter_words              = mongoengine.EmbeddedDocumentListField(FilterWord, default=[])
    filter_excluded_channels  = mongoengine.ListField(default=[])
    filter_excluded_guilds    = mongoengine.ListField(default=[349243932447604736])

    meta = {
        'db_alias': 'core',
        'collection': 'guilds'
    }

