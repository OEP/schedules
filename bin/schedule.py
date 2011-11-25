#!/usr/bin/env python3
import re
import sys
from random import choice, randrange

class OpFormatError(Exception):
  """Exception raised for improper op formats.

  Attributes:
    expr -- the malformed op
    msg -- explanation of error
  """

  def __init__(self,expr,msg):
    self.expr = expr
    self.msg = msg

def base26(num):
  """Makes a base-26 number, using the alphabet as numerals.

  Arguments:
    num -- integer to turn into base 26
  """
  alphabet = list(map(chr, map(lambda x: 65 + x, range(0,26))))
  if num == 0: return alphabet[0];

  s = ""
  while num > 0:
    s = alphabet[num % 26] + s
    num = int(num / 26)
  return s

def randomOp(tset,resources):
  """Makes a random op-tuple.

  Arguments:
    tset -- the transaction set to choose from
    resources -- number of possible resources

  Returns:
    tuple -- (<op>, <transaction #>, <resource or None>)
  """
  op = choice([ "R", "W", "C" ])
  t = str(choice(tset))
  return (op, t, None if op == "C" else base26( randrange(0,resources) ))

def op2str(op):
  """Converts an op tuple into a string

  Arguments:
    op -- the op to convert
  """
  return ((op[0] + op[1]) if op[2] == None
    else  op[0] + op[1] + "(" + op[2] + ")")

def str2op(s):
  """Parses a string into an op tuple.

  Arguments:
    s -- the string to parse

  Raises:
    OpFormatError -- if there is a problem parsing the op
  """
  m = re.match("^([WRC])([0-9]+)(\(([A-Z]+)\))?$",s)
  if m == None:
    raise OpFormatError(s, "Could not parse this as an op.")
  tmp = m.group(1,2,4)
  if (tmp[0] == "R" or tmp[0] == "W") and tmp[2] == None:
    raise OpFormatError(s, "Read/write ops require an argument.")
  elif tmp[0] == "C" and tmp[2] != None:
    raise OpFormatError(s, "Commit operations do not take arguments.")
  return tmp

class schedule:
  """Represents a transaction schedule.

  Attributes:
    ops -- the transaction operations in the schedule
  """

  def __init__(self,strSchedule=None):
    self.transactions = [ ]
    if strSchedule != None:
      strSchedule = strSchedule.strip()
      chunks = re.split('[^A-Z()0-9]+', strSchedule)
      self.ops = list(map(str2op, chunks))
    else:
      self.ops = []
    self.syncTransactions()   

  def __str__(self):
    return ','.join(map(op2str,self.ops))

  def addTransaction(self,n):
    if not n in self.transactions:
      self.transactions.append(n)

  def syncTransactions(self):
    tmp = [ x[1] for x in self.ops ]
    for i in tmp:
      self.addTransaction(i)
  

def main():
  scheds = ["R2(A),C1,W3(A),C3,R2(A),C2",
            "R2(A),C1,W3,C3,R2(A),C2",
            "R2,C1,W3(A),C3,R2(A),C2",
            "R2(A),C1,W3(A),C3,RB(A),C2",
            "R2(A),C1(C),W3(A),C3,R2(A),C2"]

  ## Override with command line argument.
  if len(sys.argv) > 1:
    scheds = [ ",".join(sys.argv[1:]) ]

  ## Loop over schedules and make sure they're ok.
  for s in scheds:
    try:
      tmp = schedule(s)
      print(s + " -> " + str(tmp))
      print("Transaction list: " + str(tmp.transactions))
    except OpFormatError as e:
      print(s + ": '" + e.expr + "': " + e.msg)

if __name__ == "__main__":
  main()
