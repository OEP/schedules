#!/usr/bin/env python3

import schedule
from schedule import op2str
from mkSchedule import makeRandomSchedule

def mkGraphFromSchedule(sched):
  s = sched.ops
  opPairs = [(x,y) for x in s for y in s if s.index(x) < s.index(y)]
  conflicts = list(filter(opsConflict, opPairs))

#  for i in conflicts:
#    print(op2str(i[0]) + " conflicts with " + op2str(i[1]))
    

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
      self.edges = []

    def __str__(self):
      return "{" + self.label + ", " + str(self.edges) + "}"

    def add(self,j):
      if not j in self.edges:
        self.edges.append(j)

	

  def __init__(self, labels):
    """Makes an edgeless graph with given labels"""
    self.initialize(labels)

  def __str__(self):
    s = str()
    for x in self.vertices.keys():
      s = s + x + " --> " + str(self.vertices[x].edges) + "\n"
    return str(s)

  def initialize(self, labels):
    """Iterates over list of labels and adds vertices to our graph"""
    self.vertices = dict()
    for label in labels:
      self.vertices[label] = self.Vertex(label)

  def addEdge(self,i,j):
    self.vertices[i].add(j)
    return None



def main():
  s = makeRandomSchedule(3,1)
  print("Schedule: " + str(s))
  (conflicts, g) = mkGraphFromSchedule(s)



if __name__ == "__main__":
  main()
