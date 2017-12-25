# -*- coding: utf-8 -*-

import re
import datetime
import codecs
import pickle

from utils.string_utils import cut_sentence


class Tables2(object):
	def __init__(self, words, token="&&", feature_num=2):
		self.v = []
		self.HEAD = "_B"
		if feature_num == 1:
			self.v = words
		else:
			for i in range(len(words)):
				tmp = [0] * feature_num
				self.v.append(tmp)
			
			for i in range(len(words)):
				word = words[i]
				seg = word.split(token)
				for ind, s in enumerate(seg):
					self.v[i][ind] = seg[ind]
	
	def get_tag(self, x, y):
		if x < 0:
			return self.HEAD + str(x)
		if x >= len(self.v):
			return self.HEAD + '+' + str((x - len(self.v) + 1))
		return self.v[x]
	

class Template(object):
	def __init__(self):
		self.featureTemplate = {}
	
	def add_template(self, text):
		seg = text.split(':')
		loc_str = seg[0].strip()
		loc_dic = seg[1].strip()[2:].split('/%x')
		self.featureTemplate.setdefault(loc_str, loc_dic)


class ExpandTemplate(object):
	def __init__(self):
		self.bigram_id = 0
		self.template_feature_id = {}
	
	def add_bigram_tag(self, text):
		seg = text.split(" ", 1)
		self.bigram_id = int(seg[0].strip())
	
	def add_unigram_tag(self, text):
		expand_template_id = text.split(' ', 1)
		tmp_id = int(expand_template_id[0].strip())
		expand_template = expand_template_id[1].strip().split(':', 1)
		template = expand_template[0]
		feature = expand_template[1]
		
		feature_id = {}
		if self.template_feature_id.get(template, "None") != "None":
			feature_id = self.template_feature_id[template]
		feature_id[feature] = tmp_id
		self.template_feature_id[template] = feature_id


class CRFmodel(object):
	def __init__(self, model_path):
		# 模板
		self.template = Template()
		# 扩展模板
		self.expand_template = ExpandTemplate()
		# 权重矩阵
		self.weight_matrix = []
		# 权重矩阵大小
		self.weight_matrix_num = 0
		# 概率转移矩阵
		self.transform_matrix = []
		# 标签集合
		self.labels = []
		# 标签数量
		self.labels_num = 0
		# 扩展模板数量
		self.extend_template_num = 0
		# crf模型解析
		self.crf_model_parse(model_path)
		# 模板特征id
		self.temp_feature_id = self.expand_template.template_feature_id
		self.featureTemplatesplit = self.template.featureTemplate
	
	def crf_model_parse(self, model_path):
		crf_model_file = codecs.open(model_path, 'r', encoding='utf-8')
		# ==============================================
		version = crf_model_file.readline().split(':')[1].strip()
		costfactor = crf_model_file.readline().split(':')[1].strip()
		maxid = crf_model_file.readline().split(':')[1].strip()
		xsize = crf_model_file.readline().split(':')[1].strip()
		# ==============================================
		crf_model_file.readline()
		
		line = crf_model_file.readline()
		while line != '\r\n':
			self.labels.append(line.strip())
			line = crf_model_file.readline()
		
		# ==============================================
		self.weight_matrix_num = int(maxid)
		self.labels_num = len(self.labels)
		self.extend_template_num = (self.weight_matrix_num - self.labels_num * self.labels_num) / self.labels_num + 1
		
		self.weight_matrix = [0] * self.weight_matrix_num
	
		# ==============================================
		line = crf_model_file.readline()
		cnt = 0
		weight_index = 0
		while line:
			cnt += 1
			line = line.strip()
			if len(line.split(' ')) > 1 and line.split(' ')[1].lower() == 'b' and len(line) > 1:
				self.expand_template.add_bigram_tag(line)
				line = crf_model_file.readline()
				continue
			if line.lower().find('u') != -1:
				if line.lower().find('%x[') != -1:
					self.template.add_template(line)
				else:
					self.expand_template.add_unigram_tag(line)
			elif cnt > self.extend_template_num and line != '':
				self.weight_matrix[weight_index] = float(line.strip())
				weight_index += 1
			line = crf_model_file.readline()
		crf_model_file.close()
		
		for i in range(self.labels_num):
			tmp = [0] * self.labels_num
			self.transform_matrix.append(tmp)
		bigram_id = self.expand_template.bigram_id
		for i in range(self.labels_num):
			for j in range(self.labels_num):
				self.transform_matrix[i][j] = self.weight_matrix[bigram_id + (i * self.labels_num) + j]
	
	def get_crf_label(self, words):
		label_list = []
		if len(words) < 1:
			return label_list
		
		table = Tables2(words, feature_num=1)
		
		# Viterbi weigth and path
		Viscoreag = [0] * self.labels_num
		Vipath = {}
		
		# transform
		for i in range(len(words)):
			weightBEMtmp = {}
			for j in range(self.labels_num):
				weightBEMtmp[self.labels[j]] = []
			
			for key, value in self.featureTemplatesplit.items():
				sb = ''
				for j in range(len(value)):
					template = value[j]
					xy = template.replace("[", "").replace("]", "")
					x = int(xy.split(",")[0])
					y = int(xy.split(",")[1])
					if sb != '':
						sb += '/'
					sb += table.get_tag(i + x, y)
				
				feature_ids = self.temp_feature_id.get(key, 'None')
				
				if len(feature_ids) > 0:
					tagFeature = sb
					_id = feature_ids.get(tagFeature, 'None')
					if _id != 'None':
						for j, label in enumerate(self.labels):
							score = weightBEMtmp.get(label, [])
							score.append(self.weight_matrix[_id + j])
							weightBEMtmp[label] = score
			
			sunBEM = [0] * self.labels_num
			for j, label in enumerate(self.labels):
				score = weightBEMtmp.get(label, [])
				sunBEM[j] += sum(score)
			
			# ---------------------  Viterbi  ---------------------------
			if i < 1:
				for j, label in enumerate(self.labels):
					Viscoreag[j] = sunBEM[j]
					Vipath[j + 1] = label
			else:
				presBEM = Viscoreag
				
				# transform
				Vipathsaved = {}
				for j in range(self.labels_num):
					Vipathsaved[j + 1] = Vipath.get(j + 1)
				
				for j in range(self.labels_num):
					skj = [0] * self.labels_num
					for k in range(self.labels_num):
						skj[k] = presBEM[k] + self.transform_matrix[k][j] + sunBEM[j]
					
					maxScore = max(skj)
					maxIdex = skj.index(maxScore)
					
					pathPre = Vipathsaved.get(maxIdex + 1)
					Vipath[j + 1] = pathPre + '\t' + self.labels[j]
					Viscoreag[j] = maxScore
		
		maxScore = max(Viscoreag)
		maxIndex = Viscoreag.index(maxScore)
		
		tags = Vipath.get(maxIndex + 1, '')
		tag = tags.split('\t')
		for s in tag:
			label_list.append(s)
		
		return label_list

	def get_seg_result(self, text):
		words_result = []
		if len(text) == 0:
			return words_result
		char_list = list(text)
		labels = self.get_crf_label(char_list)
		tmp_word = ""
		flag_b = 0
		for ind, label in enumerate(labels):
			if label == "B":
				if tmp_word != "":
					words_result.append(tmp_word)
					tmp_word = ""
				tmp_word += char_list[ind]
				flag_b = 1
			elif label == "I" and flag_b == 1:
				tmp_word += char_list[ind]
			else:
				if tmp_word != "":
					words_result.append(tmp_word)
					tmp_word = ""
				words_result.append(char_list[ind])
				flag_b = 0
		return words_result
	
	# def crf_cut(self, text):
	# 	seg_list = []
	# 	parts = re.split(r"。|；|;|,|，|、|”|“|！|!|:|：|？|\?|\t|\n", text)
	# 	sentences = filter(None, parts)
	# 	punctuation_loc = 0
	# 	for sentence in sentences:
	# 		punctuation_loc += len(sentence)
	# 		seg_list += self.get_seg_result(sentence)
	# 		if punctuation_loc < len(text) - 1:
	# 			seg_list.append(text[punctuation_loc])
	# 	return seg_list
	

if __name__ == '__main__':
	# model_path = r'E:/dyty_set_data/seg_model.txt'
	# crf = CRFmodel(model_path)
	# pickle.dump(crf, open("E:/dyty_set_data/seg_model.pickle", "wb"))
	crf = pickle.load(open("E:/dyty_set_data/seg_model.pickle", "rb"))
	text = u'由于这部五十分钟的电视纪录片真实而生动地记录了中国农村一个村子的民主选举过程，因而在本次电影节上成了各国观众和众记者关注的热门话题。'
	# text = "正当朱镕基当选政府总理后第一次在中外记者招待会上，回答外国记者的提问：中国农村是否实行民主选举制度的时候，一位中国电视编导正携带着她的反映中国农村民主选举村委会领导的电视纪录片《村民的选择》（北京电视台摄制，仝丽编导），出现在法国的真实电影节上。"
	text = "回答外国记者的提问"
	starttime = datetime.datetime.now()
	seg = crf.get_seg_result(text)
	endtime = datetime.datetime.now()
	print('\nCRF took : ' + str((endtime - starttime).microseconds / 1000) + 'ms')
	print(seg)
	
	a = sum([])
	print(a)

