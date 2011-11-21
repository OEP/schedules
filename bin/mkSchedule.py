#!/usr/bin/env python3

from optparse import OptionParser
from schedule import str2op,op2str,randomOp,schedule
import sys

def makeRandomSchedule(numTransactions,numResources):
  """Makes a truly random schedule. Only guarantees that after a commit
     operation is done, that transaction is finished. Returns a list of
     op-tuples.
  """
  tset = list(map(str,map(lambda x: x+1, range(numTransactions))))
  s = schedule()
  while True:
    op = randomOp(tset,numResources)
    s.ops.append(op)

    if op[0] == "C":
      tset.remove(op[1])

    if len(tset) == 0:
      break
  s.syncTransactions()
  return s

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
