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
	return float(len(prefix)) / max(len_a, len_b) 

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


def find_buckets(words, similarity_func = get_similarity_percentage, threshold = 0.8):

	similarities = []
	for i in range(len(words)-1):
		similarities.append(similarity_func(words[i], words[i+1]))
		
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

def find_prefixes(path = "joerg/"):
	find_list = subprocess.check_output(["find", path, "-type", "f"]).split('\n')
	word_list = [w for w in find_list if w]
	print find_buckets(word_list)

if __name__ == "__main__":
	find_prefixes()
