# ircbot
Python 2 based irc bot project
Created by OrderChaos for use on Freenode and to learn python.
Feel free to do whatever you like with this, I just ask that you don't try to sell it.

Current implementation connects via socket and reads in messages from the server. 
It saves the latest 100 messages to a flat file which is used for find/replace functions.
This is very much an alpha build with just basic functionality enabled and little or no optimization.
Recommended to run with screen or tmux as bot currently runs in foreground.

How to setup:
Download the bot.py file.
Edit the file and fill out the variables at the top per the comments.
Example:
  server = "chat.freenode.net" # Server
  channel = "##MyTestChan" # Channel
  botnick = "BotTestNick" # Your bots nick
  password = "Hunter2"

Usage (loosely) follows sed conventions:
  Messages in the format of 's/[find]/[replace]' are processed for basic find and replace with ''.
  For example, if I said "taht is funny" and wanted to correct it, I would type "s/ah/ha" and the bot would reply with "Correction <OrderChaos>: that is funny"
  Messages in the format of 's|[find]|[replace]' are processed for regex find and replace.
  For example, if I said "That's awesome!1!1!" and wanted to replace the 1s, I would type "s|\d|!" and the bot would reply with "Correction <OrderChaos>: That's awesome!!!!!"

A few things to note:
  1) All replaces are global.
  2) Only the first and last delimiters are processed, the rest are treated as part of the find/replace text.
  3) There are some limitations to the find/replace messages that are allowed (see code for details), still needs a lot of work and will likely change in future versions.
  4) There is a '.help' function, but it is not fully implemented yet and is currently a bit of a misnomer.
