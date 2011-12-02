#!/usr/bin/env python3

import sys
from optparse import OptionParser
from schedule import makeRandomSchedule

def appendIf(flag, lst, msg):
  if flag: lst.append(msg)

def check(sched):
  csz = sched.isConflictSerializable()
  rec = sched.isRecoverable()
  aca = sched.isCascadeless()
  stc = sched.isStrict()

  msgs = []
  appendIf(aca and not rec, msgs, "All ACA schedules are recoverable")
  appendIf(stc and not aca, msgs, "All strict schedules are ACA")
  appendIf(stc and not rec, msgs,
      "All strict schedules are ACA and therefore recoverable")
  return (sched, csz, rec, aca, stc, msgs)

def main():
  # Options declaration.
  parser = OptionParser()
  parser.add_option("-n", type="int", dest="number", default=1,
    help="Number of schedules to generate [default: %default]") 
  parser.add_option("-t", type="int", dest="transactions", default=3,
    help="Number of transactions in a schedule [default: %default]") 
  parser.add_option("-r", type="int", dest="resources", default=1,
    help="Number of resources in a schedule [default: %default]")
  parser.add_option("-a", action="store_true", dest="analyze",
    help="Analyze each generated schedule")
  parser.add_option("-l", action="store_true", dest="logical",
    help="Check each schedule for logical fallacies in the analysis")
  parser.add_option("-q", action="store_true", dest="quiet",
    help="Don't print the schedule unless -l was used and a fallacy exists")

  (options,args) = parser.parse_args(sys.argv);

  if len(args) > 1:
    parser.print_help()
    sys.exit(2)

  count = options.number
  tees = options.transactions 
  resources = options.resources 


  scheds = [makeRandomSchedule(tees,resources) for i in range(count)]

  if options.analyze or options.logical:
    results = map(check, scheds)
    if options.quiet:
      results = filter(lambda x: len(x[5]) > 0, results)
    for result in results:
      (sched,csz,rec,aca,stc,msgs) = result
      print(sched)
      sched.printAnalysis(csz,rec,aca,stc)
      if options.logical:
        for m in msgs: print("\tLogical error: " + m)
  else:
    for s in scheds: print(s)

if __name__ == "__main__":
  main()
