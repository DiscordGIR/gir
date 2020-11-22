import mongoengine
from data.guild import Guild

def global_init():
    mongoengine.register_connection(alias="core", name="botty")

def first_time():
    guild = Guild()
    guild._id = 777155838849843200
    guild.role_mute = 777270186604101652
    guild.role_genius = 777270163589693482
    guild.role_moderator = 777270257772789770
    guild.role_memberplus = 777270242874359828
    guild.role_memberpro = 777270222868185158
    guild.role_memberedition = 777270206841880586
    guild.role_member = 777270914365784075
    guild.channel_public = 777270542033092638
    guild.channel_private = 777270554800422943
    guild.channel_reports = 777270579719569410
    guild.channel_botspam = 778233669881561088
    guild.logging_excluded_channels = []


    guild.save()
    
    
    
    
    