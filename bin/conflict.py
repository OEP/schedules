#!/usr/bin/env python3

from optparse import OptionParser
from schedule import schedule
from schedule import OpFormatError
from Graph import mkGraphFromSchedule
import sys
import Graph


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

  line = thing.readline()
  while line:
    try:
      line = line.strip()
      sched = schedule(line)
      (conflicts, g) = mkGraphFromSchedule(sched)
  
      if g.isTrees():
        print(str(sched) + ": Conflict serializable")
      else:
        print(str(sched) + ": Not conflict serializable")
    except OpFormatError as e:
      print(line + ": '" + e.expr + "': " + e.msg)

    line = thing.readline()

if __name__ == "__main__":
  main()
