#!/usr/bin/env python3

import schedule
from schedule import op2str
from mkSchedule import makeRandomSchedule

def mkGraphFromSchedule(sched):
  s = sched.ops
  opPairs = [(x,y) for x in s for y in s[s.index(x)+1:]]
  conflicts = list(filter(opsConflict, opPairs))

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
    return status


def main():
  s = makeRandomSchedule(3,1)
  print("Schedule: " + str(s))
  (conflicts, g) = mkGraphFromSchedule(s)
  print(g)
  if g.isTrees():
    print("It's trees!")
  else:
    print("It's not trees!")



if __name__ == "__main__":
  main()
