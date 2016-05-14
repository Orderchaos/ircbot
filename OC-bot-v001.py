#!/usr/bin/python

# Import some necessary libraries.
import socket, re, subprocess, os, time, threading, sys

# Some basic variables used to configure the bot        
server = "" # Server
channel = "" # Channel
botnick = "" # Your bots nick
lines = 0
regexes = [".*"]
combined = "(" + ")|(".join(regexes) + ")"
log = []
varstartup = 0
def ping(): # This is our first function! It will respond to server Pings.
  ircsock.send("PONG :pingis\n")  

def sendmsg(msg): # This is the send message function, it simply sends messages to the channel.
  ircsock.send("PRIVMSG "+ channel +" :"+ msg +"\n") 

def joinchan(chan): # This function is used to join channels.
  ircsock.send("JOIN "+ chan +"\n")

def whisper(msg, user): # This function sends a whisper to a user 
  ircsock.send("PRIVMSG " + user + ' :' + msg.strip('\n\r') + '\n')

def sed(msg):
  if msg.count('/') < 2:
    print("not enough arguments")
    return
  sedtest=msg.split('/',1)[1].rsplit('/',1)[0]
  if sedtest == '':
    print("Nothing to find")
    return
  sreplace=msg.split('/',1)[1].rsplit('/',1)[1]
  replaced = ".__not found__."
  with open("ircchat.log", "r") as ircchat:
    content = ircchat.readlines() 
  for i in content:
    try:
      if i.split(':',1)[1].find(sedtest) != -1:
        replaced = i
    except Exception:
      pass
  if replaced == ".__not found__.":
    print("not found")
    return
  else:
    name = replaced.split(':', 1)[0]
    replaced = replaced.split(':',1)[1].replace(sedtest, sreplace)
    replaced = replaced.strip('\n\r')
    checksend(name,sedtest, replaced)
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This bot is a result of a tutoral covered on http://shellium.org/wiki.\n") # user authentication
ircsock.send("NICK "+ botnick +"\n") # here we actually assign the nick to the bot
ircsock.send("nickserv identify" + password + " \r\n")
def regex(msg):
  if msg.count('|') < 2:
    print("Not enough arguments")
    return
  sedtest = msg.split('|',1)[1].rsplit('|',1)[0]
  sreplace = msg.split('|',1)[1].rsplit('|',1)[1]
  replaced = ".__not found__."
  if (sedtest.find("*") != -1):
    findme = sedtest.replace('*','\*')
  elif len(sedtest) == 1:
    findme = re.escape(sedtest)
  else:
    findme = sedtest
  try:
    pattern = re.compile("(%s)" % findme)
  except Exception:
    findme = re.escape(findme)
    pattern = re.compile("(%s)" % findme)
    pass
  with open("ircchat.log", "r") as ircchat:
    content = ircchat.readlines()
  repltext = ('',0)
  name = ''
  found = ''
  for i in content:
    try:
      text = i.split(":",1)[1]
      if pattern.search(text):
        text = text.strip('\n\r')
        found = text
        repltext = re.subn(pattern, sreplace, text)
        name = i.split(":",1)[0]
    except Exception:
      print('error in search')
      pass
  if repltext[1] > 10:
    sendmsg("Too many matches, refine your correction")
    return
  replaced = repltext[0]
  replaced = replaced.strip('\n\r')
  checksend(name,found, replaced, findme)

def logger(msg):
  irclog = open("ircchat.log", 'r')
  content = irclog.readlines()
  irclog.close()
  irclog = open("ircchat.log", "w")
  while len(content) > 100:
    content.remove(content[0])
  for i in content:
    if i[0] != ':':
      irclog.write(i.strip('\n\r') + '\n')
    if len(i.strip('\n\r')) == 0:
      irclog.write(":delete\n")
  irclog.write(msg.strip('\n\r') + '\n')
  irclog.close()

def checksend(name,orig,new,pattern=''):
  print(pattern)
  if orig == new:
    whisper("No text would be changed.", name)
    return 
  if pattern in {'\\s','\\S','\\D','\\W', '\\w'}:
    whisper("Wildcard(s) not allowed because they are too broad. If you meant to seach plaintext use 's/[find]/[replace]' or delimit the wildcard (like s|\\\\s|!s", name)
    return 
  if len(new) > 200:
    whisper("Resulting message is too long (200 char max)", name)
    return
  if len(new) == 0:
    whisper("Replace resulted in empty messge. Nothing to send", name)
    return
  message="Correction, <" + name + ">: " + new
  sendmsg(message.strip('\r\n'))
  logger(name + ':' +  new)

def help(name,topic=''):
  message = ''
  if topic == '':
    message = "Hi! I am an irc bot created by OrderChaos. Currentl function is find and replace. You can perform a plain text find/replace on recent chat by typing in \'s/[find]/[replace]\' (no quotes) or a regex based find/replace with \'s|[find]|[replace]\'. Note that some wildcards are disabled because they result in too many matches. Please report any bugs or suggestions here: https://github.com/Orderchaos/ircbot/issues" 
  else:
    message = "Feature not yet implemented, sorry. Please see the main help (message me with \'.help\')"
  print(topic)
  whisper(message, name)

def main():
  joinchan(channel) # Join the channel using the functions we previously defined
  with open("ircchat.log", "w") as temp:
    temp.write("")
  start_time = time.time()
  while 1: # Be careful with these! it might send you to an infinite loop
    ircmsg = ""
    ircmsg = ircsock.recv(2048) # receive data from the server
    ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
    print(ircmsg) # Here we print what's coming from the server
    strmsg = str(ircmsg)
    if strmsg.find("PING :") != -1: # if the server pings us then we've got to respond!
      ping()
    if strmsg.find("PRIVMSG") != -1:
      splitmsg=strmsg.split(':',2)
      name=strmsg.split('!',1)[0][1:]
      if splitmsg[2][:2] == 's|':
        regex(strmsg)
      elif splitmsg[2][:2] == 's/':
        sed(strmsg)
      elif splitmsg[2][:5] == '.help':
        help(name,splitmsg[2][5:])
      else:
        name=strmsg.split('!')
        finalname=name[0][1:]
        combo=""
        privmsgfound = "false"
        for combine in splitmsg[1:]:
          if privmsgfound != "false":
            combo=combo + ":" + combine
          if combine.find("PRIVMSG") != -1:
            privmsgfound = "true"
        if len(finalname) < 17:
          final=finalname+combo
          logger(final)
          if final.find("OrderChaos:gtfo %s" % botnick) != -1:
            sendmsg("Oh...okay... :'(")
            ircsock.send("PART " + channel + "\r\n")
            sys.exit()

main()

