#!/usr/bin/env python3

import sys
from optparse import OptionParser
from schedule import makeRandomSchedule


def main():
  # Options declaration.
  parser = OptionParser()
  parser.add_option("-n", type="int", dest="number", default=1,
    help="Number of schedules to generate [default: %default]") 
  parser.add_option("-t", type="int", dest="transactions", default=3,
    help="Number of transactions in a schedule [default: %default]") 
  parser.add_option("-r", type="int", dest="resources", default=1,
    help="Number of resources in a schedule [default: %default]")

  (options,args) = parser.parse_args(sys.argv);

  if len(args) > 1:
    parser.print_help()
    sys.exit(2)

  COUNT = options.number
  TRANSACTIONS = options.transactions 
  COUNT_RESOURCES = options.resources 

  for i in range(COUNT):
    sched = makeRandomSchedule(TRANSACTIONS,COUNT_RESOURCES)
    print(sched)

if __name__ == "__main__":
  main()
