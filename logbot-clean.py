#!/usr/bin/python3

# Import some necessary libraries.

import socket, re, sys, sqlite3, collections
from datetime import datetime
#import subprocess, os, time, threading 
# Some basic variables used to configure the bot        
server = "" # Server
channel = "" # Channel
botnick = "" # Your bots nick
adminident = "" #Ident of user to give admin access of bot.
password = ""
dbname = channel.replace('#','') + '.db'
conn = sqlite3.connect(dbname)
c = conn.cursor()
def ping(): # respond to server Pings.
  ircsock.send(bytes("PONG :pingis\n", "UTF-8"))  

def sendmsg(msg): # sends messages to the channel.
  ircsock.send(bytes("PRIVMSG "+ channel +" :"+ msg +"\n", "UTF-8")) 

def joinchan(chan): # join channel(s).
  ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8"))
  while 1:
    # set ircmsg to new data received from server
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    # remove any line breaks
    ircmsg = ircmsg.strip('\n\r') 
    # print received message to stdout (mostly for debugging).
    if ircmsg.find("now identified") != -1:
      print("identified!")
      break

def whisper(msg, user): # whisper a user 
  ircsock.send(bytes("PRIVMSG " + user + ' :' + msg.strip('\n\r') + '\n', "UTF-8"))

def checkuser(user):
  ircsock.send(bytes("NICKSERV ACC " + user + "\n", "UTF-8"))
  nickowner = 'not registered'
  nickuser = 'not registered'
  rtn = ircsock.recv(2048).decode("UTF-8")
  acc = rtn.rsplit('ACC ', 1)[1].strip('\r\n')[0]
  if acc == '1':
    nickowner = nickinfo(user)
  ircsock.send(bytes("NICKSERV ACC " + user + ' *\n', "UTF-8"))
  rtn2 = ircsock.recv(2048).decode("UTF-8").strip('\r\n')
  if rtn2.split('ACC ', 1)[1].strip('\r\n')[0] == '3':
    nickuser = rtn2.split('> ', 1)[1].split(' ', 1)[0]
  if acc == '3':
    nickowner = nickuser  
  nickowner = ''.join(e for e in nickowner if 31 < ord(e) <127)
  nickuser = ''.join(e for e in nickuser if 31 < ord(e) <127)
  account = [nickowner, nickuser] 
  return account 
    
def nickinfo(name):
  ircsock.send(bytes("NICKSERV INFO " + name + "\n", "UTF-8"))
  account = 'not found'
  while 1:
    rtn = ircsock.recv(2048).decode("UTF-8")
    if rtn.find('End of Info') != -1:
      break
    if account == 'not found':
      account = rtn.strip('\r\n').split('account ', 1)[1].split('):', 1)[0]
  return account
# send help message to users
def help(name,topic=''):
  # set default help message to blank.
  message = ''
  # if no help topic is specified, send general help message about the bot.
  if topic == '':
    message = "Sorry, there is no help for you."
  # if a help message is specified, let the user know it's not coded yet.
  else:
    message = "Feature not yet implemented, sorry. Please see the main help (message me with \'.help\')"
  print(topic)
  # send help message in whisper to user.
  whisper(message, name)

def createdb(dbname):
  conn.execute('pragma foreign_keys=ON')
  conn.commit()
  newtable('log', 'id INTEGER PRIMARY KEY,nick text,ident text,user text,host text,message text,time datetime,command int')
  newtable('idents', 'ident text PRIMARY KEY,role int,kick_count int,ban_count int,quiet_count int,ignore int')
  newtable('nicks', 'nick text PRIMARY KEY,owner text,ignore int')
  newtable('hosts', 'host text PRIMARY KEY,ignore int')
  newtable('identhost', 'ident text,host text,seen datetime')
  newtable('identnick', 'ident text,nick text, seen datetime')
  newtable('nickhost', 'nick text,host text,seen datetime')
  newtable('action', 'time datetime,op_ident text,target text,action text,message text')
  main()

def newtable(name, column):
  if c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()[0] > 0:
    return 
  else:
    c.execute('CREATE TABLE {tn} ({col})' .format(tn=name, col=column))
  return

def log(name, message, time, cmd):
  filldb(name, time)
  idents = checkuser(name)
  hostname = userhost(name)
  c.execute("INSERT INTO log VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (name, idents[0], idents[1], hostname, message, time, cmd))
  conn.commit()

def userhost(name):
  ircsock.send(bytes('USERHOST ' + name + '\n', "UTF-8"))
  ircmsg = ircsock.recv(2048).decode("UTF-8")
  ircmsg = ircmsg.strip('\n\r')
  hostname = ircmsg.split('@', 1)[1][:-1]
  return hostname 

def joinlist(field, table, wfi, wit, item):
  exe = "SELECT {f} FROM {t} WHERE {wf}='{wi}'".format(f=field, t=table, wf=wfi, wi=wit)
  items = c.execute(exe).fetchone()[0].split(',')
  if (not item in items):
    items.append(item)
    itemlist = ",".join(items)
    c.execute("UPDATE {t} SET {f}='{il}' WHERE {wf}='{wi}'" .format(t=table, f=field, il=itemlist, wf=wfi, wi=wit))
    conn.commit()

def exists(table, field, value):
  return c.execute("SELECT count(*) from {ta} WHERE {fi}='{va}'" .format(ta=table, fi=field, va=value)).fetchone()[0]

def filldb(names, time):
  identinfo = checkuser(names)
  hostname = userhost(names)
  if identinfo[0] != 'not registered':
    if exists('idents', 'ident', identinfo[0]) == 0:
      c.execute("INSERT INTO idents VALUES (?, ?, ?, ?, ?, ?)", (identinfo[0], 'tbd', 0, 0, 0, 0))
  if identinfo[1] != 'not registered':
    if exists('idents', 'ident', identinfo[1]) == 0:
      c.execute("INSERT INTO idents VALUES (?, ?, ?, ?, ?, ?)", (identinfo[1], 'tbd', 0, 0, 0, 0))
    if c.execute("SELECT COUNT(*) FROM identnick WHERE ident=? AND nick=?", (identinfo[1], names)).fetchone()[0] == 0:
      c.execute("INSERT INTO identnick VALUES (?, ?, ?)", (identinfo[1], names, time))
    else:
      c.execute("UPDATE identnick SET seen=? WHERE ident=? AND nick=?", (time, identinfo[1], names))
    if c.execute("SELECT COUNT(*) FROM identhost WHERE ident=? AND host=?", (identinfo[1], hostname)).fetchone()[0] == 0:
      c.execute("INSERT INTO identhost VALUES (?, ?, ?)", (identinfo[1], hostname, time))
    else:
      c.execute("UPDATE identhost SET seen=? WHERE ident=? AND host=?", (time, identinfo[1], hostname))
  if exists('nicks', 'nick', names) == 0:
    c.execute("INSERT INTO nicks VALUES (?, ?, ?)", (names, identinfo[0], 0))
    c.execute("INSERT INTO nickhost VALUES (?, ?, ?)", (names, hostname, time))
  else:
    if c.execute("SELECT COUNT(*) FROM nickhost WHERE nick=? AND host=?", (names, hostname)).fetchone()[0] == 0:
      c.execute("INSERT INTO nickhost VALUES (?, ?, ?)", (names, hostname, time))
    else:
      c.execute("UPDATE nickhost SET seen=? WHERE nick=? AND host=?", (time, names, hostname))
  if exists('hosts', 'host', hostname) == 0:
    c.execute("INSERT INTO hosts VALUES (?, ?)", (hostname, 0))
  conn.commit()

def findtext(sfind):
  sfind = '%' + sfind + '%'
  sfound = []
  if (c.execute("SELECT count(*) FROM log WHERE message LIKE ? AND command = 0 ORDER BY id DESC", (sfind,)).fetchone()[0]) > 0:
    sfound = c.execute("SELECT * FROM log WHERE message LIKE ? AND command = 0 ORDER BY id DESC", (sfind,)).fetchone() 
  return sfound

def sed(name, msg, time):
  # detect if there are fewer than 2 '/' in the message. If so, not a valid find/replace pair, do nothing.
  if msg.count('/') < 2:
    print("not enough arguments")
    return
  # get the text between the first and last '/' as the 'find' portion
  sedtest=msg.split('/',1)[1].rsplit('/',1)[0]
  # if there is no text between the first and last '/' (as in 's//somethin') do nothing because there is nothing to find.
  if sedtest == '':
    print("Nothing to find")
    return
  # set the replace text to everything after the last '/'
  sreplace=msg.split('/',1)[1].rsplit('/',1)[1]
  replaced = findtext(sedtest)
  # if the default replaced text was not changed, no matches were found in the log, do nothing.
  if not replaced:
    print("not found")
    return
  else:
  # if the default replaced text was found, perform a replace on the text, strip any newlines, and send to checksend method for verification before sending to channel.
    newmsg = replaced[5].replace(sedtest, sreplace)
    hostname = userhost(botnick)
    c.execute("INSERT INTO log VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (replaced[1], replaced[2], botnick, hostname, newmsg, time, 0))
    conn.commit()
    newmsg = 'Correction, <' + replaced[1] + '>: ' + newmsg.strip('\n\r')
    sendmsg(newmsg)
    



# main functions of the bot
def main():
  # start by joining the channel. --TO DO: allow joining list of channels
  joinchan(channel)
  print('setup done')

  # start infinite loop to continually check for and receive new info from server
  while 1: 
    # clear ircmsg value every time
    ircmsg = ""
    time = '{0:%Y-%m-%d %H:%M}'.format(datetime.now())
    # set ircmsg to new data received from server
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    # remove any line breaks
    ircmsg = ircmsg.strip('\n\r') 
    # print received message to stdout (mostly for debugging).
    print(ircmsg) 
    # repsond to pings so server doesn't think we've disconnected
    # look for PRIVMSG lines as these are messages in the channel or sent to the bot
    if ircmsg.find("PRIVMSG") != -1:
      # save user name into name variable
      name = ircmsg.split('!',1)[0][1:]
      # get the message to look for commands
      message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
      cmd = 0
      if len(name) < 17:
        ident = checkuser(name)[1] 
        # if the final message is from me and says 'gtfo [bot]' stop the bot and exit. Needs adjustment so it works for main user account and not hardcoded username.
        if ident.lower() == adminident and message[:5+len(botnick)] == "gtfo %s" % botnick:
          sendmsg("oh...okay. :'(")
          ircsock.send(bytes("QUIT \r\n", "UTF-8"))
          sys.exit()

        if message[:2] == 'w/':
          sendmsg("Your ident is " + checkuser(name)[1])
          cmd = 1
        if message[:2] == 's/':
          cmd = 1
          sed(name, message, time) 
        # if no command found, get 
        if name != botnick:
          log(name, message, time, cmd)
    else:
      if ircmsg.find("PING :") != -1: 
        ping()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n", "UTF-8")) # user authentication
ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # assign the nick to the bot
ircsock.send(bytes("nickserv identify " + password + "\r\n", "UTF-8"))
#start main functioin
#main()
createdb(dbname)
conn.close()
