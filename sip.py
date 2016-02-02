#!/usr/bin/python
#sip (Shell In Python), for Operating Systems (CS444)
import os, sys, signal, errno
from socket import gethostname
from getpass import getuser
import parser
import builtins
from shellstate import ShellState
from cmdinfo import CmdInfo

#########################################
# MAIN SHELL
########################################

def sip():
  print("\n           Welcome to sip (Shell In Python)!\n")
   #initiialize hostname, username, and home variables
  hostname = gethostname()
  username = getuser()
  homedir = os.environ['HOME']

  while True:
    #Prepare prompt
    cwd = os.getcwd()
    cwd = cwd.replace(homedir, '~', 1) #Collapse home directory to ~
    prompt = "%s@%s:%s$ " %(username, hostname, cwd)

    #Get command line and print prompt
    line = raw_input(prompt)
  
    state.updatehistory(line)

    #Parse command line into commands
    cmd = parser.parse(line)

    #Check if the command is a builtin
    if parser.commandtype(cmd.name) == 'builtin':
      (getattr(builtins, cmd.name)(state, cmd))

    #Check if command is a history call.
    elif parser.commandtype(cmd.name) == 'historyrepeat':
      builtins.repeat(state, cmd)

    #If command is external,
    else:
      try:
        childPid = os.fork() #Create new process.

        if childPid == 0: 
          os.execvp(cmd.name, ([cmd.name]+cmd.args)) #If child, execute

        else:
          if cmd.background: #If the process is background, don't wait, and append to the list.
            signal.signal(signal.SIGCHLD, reaper)
            joblist.append((childPid, cmd.name))

          else: #If the process is no background, wait for it.
            state.updateprocess(childPid)
            ecode = os.waitpid(childPid, 0)

      except OSError as e:
        print e.strerror
#Reaps child processes which have been put in the background.
def reaper(sig, stack):
  os.waitpid(-1, os.WNOHANG)

#########################################
#Hook for executing shell.
#########################################
if __name__ == "__main__": 
  #initialize state
  state = ShellState()
  sip()
