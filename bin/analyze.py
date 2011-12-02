#!/usr/bin/env python3

from optparse import OptionParser
from schedule import schedule
from schedule import OpFormatError
import sys
import re

def prompt(flag):
  if flag:
    print(">", end=" ")
    sys.stdout.flush()

def main():
  # Options declaration.
  parser = OptionParser()
  (options,args) = parser.parse_args(sys.argv);

  if len(args) == 2:
    thing = open(args[1])
  elif len(args) == 1:
    thing = sys.stdin
  else:
    parser.print_help()
    sys.exit(2)

  # Print happy things if there's a user on the other side!
  tty = thing.isatty()

  if tty:
    print("* CS 609 Project")
    print("* Fall 2011")
    print("* Jason Bowman, Paul Kilgo, Houston Searcy")
    print("------------------------------------------")
    print("Type a schedule at the prompt. If it is\n",
          "well-formed, the analysis will be\n",
          "printed below. This script accepts a\n",
          "syntax similar to the one used in class.\n",
          "EXAMPLE: R1(X) W2(X) W1(X) C1 C2\n\n",
          "CTRL-D to Exit.")
    print("------------------------------------------")

  prompt(tty)

  for line in thing:
    try:
      ## Chomp off any comments.
      orig = line.strip()
      line = re.split('#+',line)[0];


      if line.strip() == "":
        if not tty: print(orig)
        prompt(tty)
        continue

      line = line.strip()
      sched = schedule(line)

      if not tty:
        print(orig)
  
      sched.printAnalysis()

    except OpFormatError as e:
      print(line + ": '" + e.expr + "': " + e.msg)

    prompt(tty)

if __name__ == "__main__":
  main()
