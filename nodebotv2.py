import codecs
import sys
import re
import socket
import time
import random
import json
import datetime
import nodebot_api


non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

# --------------------------------------------- Start Settings -----------------------------------------------------
HOST = "irc.twitch.tv"                          # Hostname of the IRC-Server in this case twitch's
PORT = 6667                                     # Default IRC-Port
CHAN = "#node1729"                              # Channelname = #{Nickname}
NICK = "nodebot1729"                            # Nickname = Twitch username
PASS = "oauth:"   # www.twitchapps.com/tmi/ will help to retrieve the required authkey
# --------------------------------------------- End Settings -------------------------------------------------------

try:
    open(CHAN[1:] + ".log")
except FileNotFoundError:
    f = open(CHAN[1:] + ".log", "w", encoding="utf-8")
    f.write("BEGIN OF LOG GENERATED ON " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "\n")
    f.write("ALL TIMES ARE REPRESENTED IN UTC\n")
    f.flush()
    f.close()

logfile = open(CHAN[1:] + ".log", "a", encoding="utf-8")

# --------------------------------------------- Start Functions ----------------------------------------------------
def send_pong(msg):
    con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))


def send_message(chan, msg):
    con.send(bytes('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))


def send_nick(nick):
    con.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))


def send_pass(password):
    con.send(bytes('PASS %s\r\n' % password, 'UTF-8'))


def join_channel(chan):
    con.send(bytes('JOIN %s\r\n' % chan, 'UTF-8'))


def part_channel(chan):
    con.send(bytes('PART %s\r\n' % chan, 'UTF-8'))

# --------------------------------------------- Start Commands -----------------------------------------------------
def command_pikmin():
    pikmin_list = open("!pikmin.txt", "r")
    pikmin = pikmin_list.readlines()
    pikmin_total_list = []
    for item in pikmin:
        item = re.split(":", item, 1)
        x = 0
        while x < int(item[0]):
            x += 1
            pikmin_total_list.append(item[1])

    #print(pikmin_total_list)
    pikmin = random.choice(pikmin_total_list)
    send_message(CHAN, sender + " lost " + str(random.randrange(1,100)) + " Pikmin to " + pikmin)

def command_fullbutton():
    buttons = open("E:/RetroSpy/gcn_buttons.txt")
    buttons_list = buttons.readlines()
    outstr = ""
    for item in buttons_list:
        item = item[:-1]
        outstr += item + ", "
        print(item)
    outstr = outstr[:-2]
    send_message(CHAN, outstr)
    buttons.close()

def command_commands():
    commands = options
    commands_list = []
    for key in commands:
        commands_list.append(key)
    commands_list.sort()
    outstr = "List of commands are as follows: "
    for item in commands_list:
        outstr += item + ", "
    outstr = outstr[:-2]
    send_message(CHAN, outstr)

def command_quote():
    qnumber = message[7:]
    print(qnumber)
    quotelist = open('!quote.txt', 'r')
    quotes = quotelist.readlines()
    if getInteger(qnumber):
        if int(qnumber) > len(quotes):
            send_message(CHAN, 'out of range, quote count: ' + str(len(quotes)))
        else:
            quote = quotes[int(qnumber) - 1]
            send_message(CHAN, quote)
    else:
        quote = random.choice(quotes)
        send_message(CHAN, quote)

def command_good_luck():
    good_luck_list = open("good_luck_list.txt", "r")
    good_luck = good_luck_list.readlines()
    good_luck = random.choice(good_luck)
    send_message(CHAN, "Thanks for the " + good_luck)

def command_pb():
    send_message(CHAN, "PB is a 1:52:36, expect nothing productive today")

def command_wr():
    send_message(CHAN, "KAP CAN'T READ")

def command_isprime():
    primenum = message[9:]
    if getInteger(primenum):
        primenum = int(primenum)
        if primenum > 1000000000:
            send_message(CHAN, "Number exceeding 1 billion, too large")
        elif primenum <= 1:
            send_message(CHAN, "Number too small")
        else:
            x = 2
            isdone = False
            while x <= primenum ** (0.5) and not isdone:
                if primenum % x == 0:
                    send_message(CHAN, str(primenum) + " is not prime")
                    isdone = True
                x += 1
            if not isdone:
                send_message(CHAN, str(primenum) + " is prime")
    else:
        send_message(CHAN, "null")


def command_fact():
    factnumber = message[6:]
    factlist = open("!fact.txt", "r")
    facts = factlist.readlines()
    if getInteger(factnumber):
        if int(factnumber) > (len(facts) - 1):
            send_message(CHAN, "out of range, fact count: " + str(len(facts)- 1))
        else:
            fact = facts[int(factnumber)]
    else:
        fact = random.choice(facts)
    send_message(CHAN, fact)


def test():
    if user_command_level >= 25:
        send_message(CHAN, 'you are a mod')
    else:
        send_message(CHAN, 'you are not a mod')

def command_faq():
    send_message(CHAN, "https://pastebin.com/TgidyeNa")

def command_get_user_id():
    user = message[len("!getuserid "):]
    if not user:
        user = sender

    output = nodebot_api.get_user_ID(username=user)
    if not output:
        send_message(CHAN, "Invalid username supplied")
    else:
        send_message(CHAN, output)

def command_followage():
    chans = re.split(" ", message[len("!followage "):])
    chans.remove('')
    if len(chans) == 2:
        sender = chans[0]
        channel = chans[1]
    elif len(chans) == 1:
        sender = chans[0]
        channel = CHAN[1:]
    else:
        channel = CHAN[1:]
    print(sender, channel)
    followage = nodebot_api.followage(sender, channel)
    if not followage:
        outstr = "User either doesn't follow channel or doesn't exist"
    else:
        outstr = sender + " has been following " + channel + " for "
        if int(followage.years):
            outstr += followage.years + "Y, "
        if int(followage.months):
            outstr += followage.months + "M, "
        if int(followage.days):
            outstr += followage.days + "D, "
        if int(followage.hours):
            outstr += followage.hours + "H, "
        if int(followage.minutes):
            outstr += followage.minutes + "m, "
        if int(followage.seconds):
            outstr += followage.seconds + "s"

    send_message(CHAN, outstr)

def command_uptime():
    channel = message[len("!uptime "):-1]
    print(channel)
    if not channel:
        channel = CHAN[1:]
    stream_uptime = nodebot_api.uptime(channel)
    if not stream_uptime:
        outstr = "User either is not live or doesn't exist"
    else:
        outstr = channel + " has been live for " 
        if int(stream_uptime.years):
            outstr += stream_uptime.years + "Y, "
        if int(stream_uptime.months):
            outstr += stream_uptime.months + "M, "
        if int(stream_uptime.days):  
            outstr += stream_uptime.days + "D, "  
        if int(stream_uptime.hours):
            outstr += stream_uptime.hours + "H, "
        if int(stream_uptime.minutes):
            outstr += stream_uptime.minutes + "m, "
        if int(stream_uptime.seconds): 
            outstr += stream_uptime.seconds + "s"
    send_message(CHAN, outstr)

def command_title():
    channel = message[len("!title "):-1]
    if not channel:
        channel = CHAN[1:]
    stream_title = nodebot_api.title(channel)
    if not stream_title:
        outstr = "Channel either not live or doesn't exist"
    else:
        outstr = stream_title
    send_message(CHAN, outstr)

# --------------------------------------------- End Commands -------------------------------------------------------

# --------------------------------------------- Start Helper Functions ---------------------------------------------
def get_sender(msg):
    result = ""
    for char in msg:
        if char == "!":
            break
        if char != ":":
            result += char
    return result

def get_message(msg):
    result = ""
    i = 3
    length = len(msg)
    while i < length:
        result += msg[i] + " "
        i += 1
    print(user_command_level)
    result = result[1:]
    return result

options = {}

def parse_message(msg):
    global options
    if len(msg) >= 1:
        msg = msg.split(' ')
        options = {"!pikmin": command_pikmin,
                   "!quote": command_quote,
                   "!wr": command_wr,
                   "!test": test,
                   "!fact": command_fact,
                   "!pb": command_pb,
                   "!faq": command_faq,
                   "!isprime": command_isprime,
                   "!commands": command_commands,
                   "!getuserid": command_get_user_id,
                   "!followage": command_followage,
                   "!uptime":command_uptime,
                   "!title": command_title
                   }
        if msg[0] in options:
            options[msg[0]]()
    
def getInteger(s):
    try:
        int(s)
        return int(s)
    except ValueError:
        return False

def add_bits(user, bits):
    opened = False
    while not opened:
        try:
            bitfile = open(CHAN[1:] + "_bitfile.json", "r")
            opened = True
        #if file does not exist create it
        except FileNotFoundError:
            bitfile = open(CHAN[1:] + "_bitfile.json", "w")
            bitfile.write("{}")
            bitfile.close()
    bits_dict = json.load(bitfile)
    bitfile.close()
    bitout = open(CHAN[1:] + "_bitfile.json", "w")
    if user not in bits_dict:
        bits_dict[user] = bits
    else:
        bits_dict[user] = int(bits_dict[user]) + int(bits)
    json.dump(bits_dict, bitout, indent=4, sort_keys=True)
    bitout.close()

# -------------------------------------------------------------------------------
con = socket.socket()
con.connect((HOST, PORT))

def connect():
    send_pass(PASS)
    send_nick(NICK)
    join_channel(CHAN)
    con.send(bytes('CAP REQ :twitch.tv/tags\r\n', 'UTF-8'))
    con.send(bytes('CAP REQ :twitch.tv/commands\r\n', 'UTF-8'))
    con.send(bytes('CAP REQ :twitch.tv/membership\r\n', 'UTF-8'))

connect()

data = ""

while True:
    try:
        data = data+con.recv(1024).decode("UTF-8", errors="ignore")
        if len(data) == 0:
            connect()

        data_split = re.split(r"[~\r\n]+", data)
        print(data_split)
        data = data_split.pop()

        if data_split[0][:4] != "PING":
            data_split = re.split(":", data_split[0], 1)
        data_split_dict = {}
        data_split_list = re.split(";", data_split[0])
        
        #create tags, filling blank ones with empty strings
        for item in data_split_list:
            item = re.split("=", item, 1)
            
            #set message, workaround.
            if item[0] == "user-type":
                data_split_dict["user-type"] = data_split[-1]
            else:
                try:
                    data_split_dict[item[0]] = item[1]
                except IndexError:
                    data_split_dict[item[0]] = ""

        print(data_split_dict)
        #default user level
        user_command_level = 10
        if "user-type" in data_split_dict:
            if data_split_dict["mod"] == "1":
                user_command_level = 25
                #if a mod is detected, remove the mod from user-type, this ensures that get_message will still work
                if data_split_dict["user-type"][3:] == "mod":
                    data_split_dict["user-type"] = data_split_dict["user-type"][3:]
            
            for line in [data_split_dict["user-type"]]:
                line = str.rstrip(line)
                line = str.split(line)

                if line[1] == "PRIVMSG":
                    sender = get_sender(line[0])
                    if "bits" in data_split_dict:
                        add_bits(sender, data_split_dict["bits"])
                    #broadcaster will always be the channel name, has complete authority over bot
                    if sender == CHAN[1:]:
                        user_command_level = 50
                    message = get_message(line)
                    parse_message(message)
                    if " gl " in message.lower() or message.lower() == "gl" or message[-3:].lower() == " gl":
                        command_good_luck()
                    print("[" + str(user_command_level) + "] " + sender + ": " + message.translate(non_bmp_map))
                    logfile.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " [" + str(user_command_level) + "] " + sender + ": " + message + "\n")
                    logfile.flush()

        else:
            for line in data_split:
                line = str.rstrip(line)
                line = str.split(line)
                if len(line) >= 1:
                    if line[0] == "PING":
                        send_pong(line[1])
                        print("sending pong")


    except socket.error:
        print("Socket died")

    except socket.timeout:
        print("Socket timeout")
