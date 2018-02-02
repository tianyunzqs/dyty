# -*- coding: utf-8 -*-

import os
import sys
import queue
import time
import re


class Node:
	def __init__(self):
		self.value = None
		self.children = {}    # children is of type {char, Node}


class Trie:
	def __init__(self):
		self.root = Node()
	
	def insert(self, key):      # key is of type string
		# key should be a low-case string, this must be checked here!
		node = self.root
		for char in key:
			if char not in node.children:
				child = Node()
				node.children[char] = child
				node = child
			else:
				node = node.children[char]
		node.value = key

	def search(self, key):
		node = self.root
		for char in key:
			if char not in node.children:
				return None
			else:
				node = node.children[char]
		return node.value

	def seg(self, sentence):
		N = len(sentence)
		for i in range(N):
			for j in range(i+1, N):
				node = self.root
				flag = 0
				for char in sentence[i: j+1]:
					if char not in node.children:
						flag = 1
					else:
						node = node.children[char]
				if not flag and node.value:
					yield node.value
					
	def display_node(self, node):
		q = []
		front = 0
		rear = 0
		q.append(node)
		rear += 1
		while front != rear:
			p = q[front]
			front += 1
			if p.children is not None:
				for k, v in p.children.items():
					print(v.value)
					q.append(v)
					rear += 1
			
	def display(self):
		for key, child in self.root.children.items():
			self.display_node(child)
			
	def get_all_words(self):
		for _, child in self.root.children.items():
			q = []
			front = 0
			rear = 0
			q.append(child)
			rear += 1
			while front != rear:
				p = q[front]
				front += 1
				if p.children is not None:
					for k, v in p.children.items():
						yield v.value
						q.append(v)
						rear += 1


def gen_trie(f_name):
	"""
	构建trie树
	:param f_name: 用户词典路径
	:return: trie词典树
	"""
	trie = {}
	with open(f_name, "r", encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			parts = re.split(r"\s+", line.strip())
			if len(parts) == 2:
				word, freq = parts
				p = trie
				for w in word:
					if w not in p:
						p[w] = {}
					p = p[w]
				p[""] = ""
	return trie


# trie = Trie()
_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
# print("Building Trie...", file=sys.stderr)
trie2 = gen_trie(os.path.join(_curpath, "dict2.txt"))
# t1 = time.time()
# content = open(os.path.join(_curpath,"dict.txt"),'rb').read().decode('utf-8')
# for line in content.split("\n"):
# 	word,freq = line.split(" ")
# 	trie.insert(word)
# print("loading model cost " + str(time.time() - t1) + "seconds.", file=sys.stderr)
# print("Trie has been built succesfully.", file=sys.stderr)


def __cut_all(sentence):
	N = len(sentence)
	i,j=0,0
	p = trie2
	while i<N:
		c = sentence[j]
		if c in p:
			p = p[c]
			if '' in p:
				yield sentence[i:j+1]
			j+=1
			if j>=N:
				i+=1
				j=i
				p=trie2
		else:
			p = trie2
			i+=1
			j=i


def dyty_cut(sentence):
	start_loc, end_loc, end = 0, 0, 0
	p = trie2
	for loc, char in enumerate(sentence):
		if char in p:
			end_loc += 1
			p = p[char]
			if "" in p:
				end = end_loc
				print("word = ", sentence[start_loc: end_loc])
		else:
			end_loc += 1
			if p != trie2:
				start_loc = end
			print("word = ", sentence[start_loc: end_loc])
			start_loc = end_loc
			p = trie2
	

# text = "我是谁"
# text = "小明是谁"
# text = "小明是县长"
text = "小明县长"
dyty_cut(text)
exit(0)


t1 = time.time()
print(list(__cut_all(text)))
print(time.time() - t1)

# trie.insert('中国')
# trie.insert('中国人')
# trie.insert('国芯')
# trie.insert('国人')
# trie.insert('国家')
# trie.insert('家人')
# trie.insert('人民')
# trie.insert('银行')
# trie.insert('北京')
# print(list(trie.get_all_words()))

# print(list(trie.seg('中国人民银行在北京。')))

# trie.insert('国庆')
# trie.insert('国庆节')
# trie.insert('研究')
# trie.insert('结巴')
# trie.insert('分词')
text = '武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式武汉市长江大桥出席长江大桥的通车仪式'
# t1 = time.time()
# print(list(trie.seg(text)))
# print(time.time() - t1)

t1 = time.time()
print(list(__cut_all(text)))
print(time.time() - t1)