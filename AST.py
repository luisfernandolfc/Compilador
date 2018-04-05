import sys

class Node(object):
	def __init__(self,type,children,leaf=None):
		self.type = type
		self.children = children
		self.leaf = leaf
	
		
	def __str__(self, level=0):
		ret = "|"*level+repr(self.type)+"\n"
		for child in self.children:
			ret += child.__str__(level+1)
		return ret



		
