import urllib3
import certifi
import json
import time
import datetime
import dateutil.parser as dp

def twitchAPIReq(URL):
    http = urllib3.PoolManager(
            cert_reqs="CERT_REQUIRED",
            ca_certs=certifi.where())

    r = http.request("GET", URL,
            headers={
                "Client-ID": ''
                })
    output = json.loads(r.data.decode("utf-8"))
    return output

def get_user_ID(username):
    username_json = twitchAPIReq("https://api.twitch.tv/helix/users?login=" + username)
    try:
        user_id = username_json["data"][0]["id"]
    except IndexError:
        user_id = False
    return user_id

def followage(sender, channel):
    senderid = get_user_ID(sender)
    channelid = get_user_ID(channel)
    if not senderid or not channelid:
        return False
    else:
        follow_json = twitchAPIReq("https://api.twitch.tv/helix/users/follows?from_id=" + senderid + "&to_id=" + channelid)
        if follow_json["data"]:
            follow_time = follow_json["data"][0]["followed_at"]
            return(deltatime_nodebot(follow_time))
        else:
            return False

def uptime(username):
    user_id = get_user_ID(username)
    if not user_id:
        return False
    else:
        stream_json = twitchAPIReq("https://api.twitch.tv/helix/streams?user_id=" + user_id)
        if stream_json["data"]:
            start_time = stream_json["data"][0]["started_at"]
            return deltatime_nodebot(start_time)
        else:
            return False

def title(username):
    user_id = get_user_ID(username)
    if not user_id:
        return False
    else:
        stream_json = twitchAPIReq("https://api.twitch.tv/helix/streams?user_id=" + user_id)
        if stream_json["data"]:
            return stream_json["data"][0]["title"]
        else:
            return False


def deltatime_nodebot(in_time):    
    parsed_time = dp.parse(in_time)
    delta = datetime.datetime.utcnow().replace(tzinfo=None) - parsed_time.replace(tzinfo=None)
    class output:
        years = str(delta.days // 365)
        months = str(((delta.days // 12) % 31) % 12)
        days = str(delta.days % 31)
        hours = str(delta.seconds // 3600)
        minutes = str((delta.seconds // 60) % 60)
        seconds = str(delta.seconds % 60)
    return output

