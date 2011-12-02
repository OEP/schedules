#!/usr/bin/env python3
import re
import sys
from random import choice, randrange

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

def makeRandomSchedule(numTransactions,numResources):
  """Makes a truly random schedule. Only guarantees that after a commit
     operation is done, that transaction is finished. Returns a list of
     op-tuples.
  """
  tset = list(map(str,map(lambda x: x+1, range(numTransactions))))
  s = schedule()
  while True:
    op = randomOp(tset,numResources)
    s.addOp(op)

    if op[0] == "C":
      tset.remove(op[1])

    if len(tset) == 0:
      break
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

def mkGraphFromSchedule(sched):
  conflicts = sched.getConflicts()

  g = Graph(sched.transactions)
  for ops in conflicts:
    g.addEdge(ops[0][1], ops[1][1])
  return (conflicts, g)

def opsConflict(a):
  op1 = a[0][0]
  op2 = a[1][0]
  t1 = a[0][1]
  t2 = a[1][1]
  r1 = a[0][2]
  r2 = a[1][2]
  return (op1 == "W" or op2 == "W") and (t1 != t2) and (r1 == r2) \
    and (op1 != "C" and op2 != "C")

class OpFormatError(Exception):
  """Exception raised for improper op formats.

  Attributes:
    expr -- the malformed op
    msg -- explanation of error
  """

  def __init__(self,expr,msg):
    self.expr = expr
    self.msg = msg
  
class Graph:

  class Vertex:
    def __init__(self, label):
      self.label = label
      self.edges = dict()
      self.visited = False

    def __str__(self):
      return "{" + self.label + " --> " + str(list(self.edges.keys())) + "}"

    def add(self,j,node):
      self.edges[j] = node

    def isTree(self):
      if self.visited: return False
      self.visited = True
      status = True
      for k,v in self.edges.items():
        status = status and v.isTree()
      self.visited = False
      return status


  def __init__(self, labels):
    """Makes an edgeless graph with given labels"""
    self.initialize(labels)

  def __str__(self):
    return str(list(map(str,self.vertices.values())))

  def initialize(self, labels):
    """Iterates over list of labels and adds vertices to our graph"""
    self.vertices = dict()
    for label in labels:
      self.vertices[label] = self.Vertex(label)

  def addEdge(self,i,j):
    self.vertices[i].add(j, self.vertices[j])
    return None

  def isTrees(self):
    status = True
    for k,v in self.vertices.items():
      status = status and v.isTree()
      if status == False: break
    return status


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

  def addOp(self, op):
    self.ops.append(op)
    self.syncTransactions()

  def getConflicts(self):
    return list(filter(
          opsConflict,
          [(x,y) for x in self.ops for y in self.ops[self.ops.index(x)+1:]]
    ))

  def syncTransactions(self):
    tmp = [ x[1] for x in self.ops ]
    for i in tmp:
      self.addTransaction(i)

  def printAnalysis(self, csz=None, rec=None, aca=None, stc=None):
    if csz==None: csz = self.isConflictSerializable()
    if rec==None: rec = self.isRecoverable()
    if aca==None: aca = self.isCascadeless()
    if stc==None: stc = self.isStrict()

    if csz: print("\t* Conflict serializable")
    else: print("\t* Not conflict serializable")
    if rec: print("\t* Recoverable")
    else: print("\t* Not recoverable")
    if aca: print("\t* ACA")
    else: print("\t* Not ACA")
    if stc: print("\t* Strict")
    else: print("\t* Not strict")
    return (csz,rec,aca,stc)
  
  def isConflictSerializable(self):
    (conflicts, g) = mkGraphFromSchedule(self)
    return g.isTrees()

  def isRecoverable(self):
    """Returns true if all transactions commit after all
       the transactions whose changes they read have committed."""
    # Keeps track of which transactions wrote to a resource.
    dirtyMap = dict()

    # Keeps track of which transaction's uncommitted reads we read.
    uncommittedReads = dict()

    for op in self.ops:
      # A set of cardinality 1 is the loneliest set that you ever knew...
      lonelySet = set(op[1])
      
      # Make empty set for not encountered resources
      if op[2] not in dirtyMap: dirtyMap[op[2]] = set()

      # Same thing for transactions
      # Set 0 contains transaction ID's whose dirty reads
      # Set 1 contains resources who were dirty when we read them.
      if op[1] not in uncommittedReads: uncommittedReads[op[1]] = [set(),set()]

      # Dirty the resource!
      if op[0] == "W": dirtyMap[op[2]] |= lonelySet
      # Tally up uncommitted reads.
      elif op[0] == "R":
        uncommittedReads[op[1]][0] |= dirtyMap[op[2]]
        uncommittedReads[op[1]][1] |= set([op[2]])


      # Remove self from dirty sets and make sure this commit is recoverable
      elif op[0] == "C":
        for key in dirtyMap.keys():
          dirtyMap[key] -= lonelySet


        # Now check on our uncommitted reads.
        reads = uncommittedReads[op[1]]
        for res in reads[1]:
          for tr in reads[0]:
            if tr in dirtyMap[res]:
              return False
    return True

  def isCascadeless(self):
    """Returns true if no transactions read uncommitted resources.
       Also known as ACA."""
    # Keeps track of which transactions wrote to a resource.
    dirtyMap = dict()

    for op in self.ops:
      # A set of cardinality 1 is the loneliest set that you ever knew...
      lonelySet = set(op[1])
      
      # Make empty set for not encountered resources
      if op[2] not in dirtyMap: dirtyMap[op[2]] = set()

      # Dirty the resource!
      if op[0] == "W": dirtyMap[op[2]] |= lonelySet
      # Tally up uncommitted reads.
      elif op[0] == "R":
        ignore = 1 if op[1] in dirtyMap[op[2]] else 0
        if len(dirtyMap[op[2]]) - ignore > 0:
          return False

      # Remove self from dirty sets and make sure this commit is recoverable
      elif op[0] == "C":
        for key in dirtyMap.keys():
          dirtyMap[key] -= lonelySet
    return True

  def isStrict(self):
    conflicts = self.getConflicts()
    commitSet = set()
    for op in self.ops:
      if op[0] == "C":
        for conflict in conflicts:
          # Make sure that, for each conflict where the current transaction
          # is in the RHS that the transaction on the LHS has committed.
          if conflict[1][1] == op[1] and conflict[0][1] not in commitSet:
            return False
        commitSet |= set([ op[1] ])
    return True
    

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
      if tmp.isConflictSerializable(): print("Conflict serializable!")
      else: print("Not conflict serializable!")
    except OpFormatError as e:
      print(s + ": '" + e.expr + "': " + e.msg)

if __name__ == "__main__":
  main()
