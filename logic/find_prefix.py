#!/usr/bin/python

import os
import subprocess

def get_similarity_percentage(a, b):
	'''
	params: two filenames to compare
	return value: ratio of common prefix to longest string
	'''

	# get length
	len_a, len_b = len(a), len(b)

	# compare strings and return the bucket
	prefix = os.path.commonprefix([a, b])

	# return ratio
	sim = float(len(prefix)) / max(len_a, len_b) 

	#print a + " ~ " + b + " == " + str(sim)

	return sim

def get_similarity_prefix(a, b):
	'''
	params: two filenames to compare
	return value: length of common prefix
	'''
	return len(os.path.commonprefix([a, b]))

def get_similarity_suffix(a, b):
	'''
	params: two filenames to compare
	return value: max length of differing suffix (signed)
	'''
	len_common_prefix = len(os.path.commonprefix([a, b]))
	return len_common_prefix - max(len(a), len(b))	


def find_buckets(words, similarity_func = get_similarity_percentage, threshold = 0.5):

	similarities = []
	for i in range(len(words)-1):
		index_a = words[i].rfind("/") + 1
		index_b = words[i+1].rfind("/") + 1
		path_a = words[i][:index_a]
		name_a = words[i][index_a:]
		path_b = words[i+1][:index_b]
		name_b = words[i+1][index_b:]
		if path_a == path_b:
			similarities.append( similarity_func( name_a, name_b ) )
		else:
			similarities.append( 0 )
		
	buckets = [] 
	act_buckets = []
	
	for i in range(len(similarities)):
		# first fits 
		act_buckets.append(words[i])
		if similarities[i] < threshold:
			buckets.append(act_buckets)
			# new act_buckets
			act_buckets = []

	# last act_buckets should be in buckets too
	act_buckets.append(words[-1])
	buckets.append(act_buckets)

	prefix_dict = {} # example: {'prefix':['','']}
	for bucket in buckets:
		common_prefix = os.path.commonprefix(bucket)
		prefix_dict[common_prefix] = bucket

	return prefix_dict

def want_file( w ):
	if not w:
		return False
	if w.find(".git") > 0:
		return False
	return True

def find_prefixes(path = "/var/ssl"):
	find_list = sorted( subprocess.\
		Popen(['find', path ,"-type","f"], stdout=subprocess.PIPE).\
		communicate()[0].\
		split('\n')\
	)
	#find_list = subprocess.check_output(["find", path, "-type", "f"]).split('\n')
	word_list = [ w.replace(path,"") for w in find_list if want_file( w )]
	return find_buckets(word_list)

