import re
import math
import os,sys
import pprint
import jieba.finalseg
import time
import tempfile
import marshal

FREQ = {}
total =0.0

def gen_trie(f_name):
	lfreq = {}
	trie = {}
	ltotal = 0.0
	content = open(f_name,'rb').read().decode('utf-8')
	for line in content.split("\n"):
		word,freq = line.split(" ")
		freq = float(freq)
		lfreq[word] = freq
		ltotal+=freq
		p = trie
		for c in word:
			if not c in p:
				p[c] ={}
			p = p[c]
		p['']='' #ending flag
	return trie, lfreq,ltotal


_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
# print("Building Trie...", file=sys.stderr)
trie,FREQ,total = gen_trie(os.path.join(_curpath,"dict2.txt"))
FREQ = dict([(k,float(v)/total) for k,v in FREQ.items()])
min_freq = min(FREQ.values())
# _curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
#
# print >> sys.stderr, "Building Trie..."
# t1 = time.time()
# cache_file = os.path.join(tempfile.gettempdir(),"jieba.cache")
# load_from_cache_fail = True
# if os.path.exists(cache_file) and os.path.getmtime(cache_file)>os.path.getmtime(os.path.join(_curpath,"dict.txt")):
# 	print >> sys.stderr, "loading model from cache"
# 	try:
# 		trie,FREQ,total,min_freq = marshal.load(open(cache_file,'rb'))
# 		load_from_cache_fail = False
# 	except:
# 		load_from_cache_fail = True
#
# if load_from_cache_fail:
# 	trie,FREQ,total = gen_trie(os.path.join(_curpath,"dict.txt"))
# 	FREQ = dict([(k,float(v)/total) for k,v in FREQ.iteritems()]) #normalize
# 	min_freq = min(FREQ.itervalues())
# 	print >> sys.stderr, "dumping model to file cache"
# 	marshal.dump((trie,FREQ,total,min_freq),open(cache_file,'wb'))
#
# print >> sys.stderr, "loading model cost ", time.time() - t1, "seconds."
# print >> sys.stderr, "Trie has been built succesfully."


def __cut_all(sentence):
	N = len(sentence)
	i,j=0,0
	p = trie
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
				p=trie
		else:
			p = trie
			i+=1
			j=i




def calc(sentence,DAG,idx,route):
	N = len(sentence)
	route[N] = (1.0,'')
	for idx in range(N-1,-1,-1):
		candidates = [ ( FREQ.get(sentence[idx:x+1],min_freq) * route[x+1][0],x ) for x in DAG[idx] ]
		route[idx] = max(candidates)

def __cut_DAG(sentence):
	N = len(sentence)
	i,j=0,0
	p = trie
	DAG = {}
	while i<N:
		c = sentence[j]
		if c in p:
			p = p[c]
			if '' in p:
				if not i in DAG:
					DAG[i]=[]
				DAG[i].append(j)
			j+=1
			if j>=N:
				i+=1
				j=i
				p=trie
		else:
			p = trie
			i+=1
			j=i
	for i in range(len(sentence)):
		if not i in DAG:
			DAG[i] =[i]
	#pprint.pprint(DAG)
	route ={}
	calc(sentence,DAG,0,route=route)
	x = 0
	buf =u''
	while x<N:
		y = route[x][1]+1
		l_word = sentence[x:y]
		if y-x==1:
			buf+= l_word
		else:
			if len(buf)>0:
				if len(buf)==1:
					yield buf
					buf=u''
				else:
					regognized = jieba.finalseg.__cut(buf)
					for t in regognized:
						yield t
					buf=u''
			yield l_word		
		x =y

	if len(buf)>0:
		if len(buf)==1:
			yield buf
		else:
			regognized = jieba.finalseg.__cut(buf)
			for t in regognized:
				yield t


def cut(sentence,cut_all=False):
	# if not ( type(sentence) is unicode):
	# 	try:
	# 		sentence = sentence.decode('utf-8')
	# 	except:
	# 		sentence = sentence.decode('gbk','ignore')
	re_han, re_skip = re.compile(r"([\u4E00-\u9FA5]+)"), re.compile(r"[^a-zA-Z0-9+#\n]")
	blocks = re_han.split(sentence)
	cut_block = __cut_DAG
	if cut_all:
		cut_block = __cut_all
	for blk in blocks:
		if re_han.match(blk):
				#pprint.pprint(__cut_DAG(blk))
				for word in cut_block(blk):
					yield word
		else:
			tmp = re_skip.split(blk)
			for x in tmp:
				if x!="":
					yield x

text = "小明是小程序员"
print(list(cut(text, cut_all=True)))
exit(0)


def load_userdict(f_name):
	global trie,total,FREQ
	content = open(f_name,'rb').read().decode('utf-8')
	for line in content.split("\n"):
		if line.rstrip()=='': continue
		word,freq = line.split(" ")
		freq = float(freq)
		FREQ[word] = freq / total
		p = trie
		for c in word:
			if not c in p:
				p[c] ={}
			p = p[c]
		p['']='' #ending flag
