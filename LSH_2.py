from __future__ import division
from random import randint
from time import time
from sys import argv
import numpy as np  
import pandas as pd
import sys
import random
import gc

# Generate pairs of random numbers that act as seeds for the minhash functions
def generateMinHashSeeds(noOfSeeds):
	seeds=[]
	unique_seeds=set()
	i=0
	while i<noOfSeeds:
		i=i+1
		a=random.randint(0,100000)
		b=random.randint(0,100000)
		seed_hash=hash((a,b))
		if seed_hash not in unique_seeds:
			unique_seeds.add((a,b))
			seeds.append((a,b))
		else:
			i=i-1

	return seeds

# Generate the hash value of a given data item based on the two seed values of a minhash function
def getHash(data,seedone,seedtwo):
	hash_val=17
	hash_val=hash_val*37^hash(seedone)
	hash_val=hash_val*37^hash(seedtwo)
	hash_val=hash_val*37^hash(data)
	return hash_val


# fracs=[0,0.25,0.50,0.75,1]
fracs=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
sizes=[5000,10000,15000,20000]
no_seeds=100
seeds=generateMinHashSeeds(no_seeds)
results=pd.DataFrame(data=None,columns=fracs,index=sizes)

# Running minhash for each pair of combinations between fracs and sizes!
for s in sizes:
	for f in fracs:
		print "Working on size",s,"fraction",f
		# Generate f fraction of total size numbers as common in two array,rest all numbers should be different!
		# Since Jaccard similarity has union in denominator in order to have f as the JS,need to have 2*f/(1+f) similar values between two sets
		same_frac=2*f/(1+f)
		# sample1=range(0,int(s*same_frac))
		# sample2=range(0,int(s*same_frac))
		# sample1=sample1+range(int(s*same_frac),int((2-same_frac)*s),2)
		# sample2=sample2+range(int(s*same_frac)+1,int((2-same_frac)*s)+1,2)
		same_values=random.sample(range(0,2*s),int(same_frac*s))
		sample1=same_values
		sample2=same_values
		additonal_sample1=random.sample(list(set(range(0,2*s))-set(same_values)),int(s*(1-same_frac)))
		sample1=sample1+additonal_sample1
		additonal_sample2=random.sample(list(set(range(0,2*s))-set(sample1)),int(s*(1-same_frac)))
		sample2=sample2+additonal_sample2

		# print "Int:",len(set(sample1)&set(sample2)),"Uni:",len(set(sample1)|set(sample2))
		# print "S:",s,"F:",f,"S1:",len(sample1),"S2:",len(sample2),"JS:",len(set(sample1)&set(sample2))/len(set(sample1)|set(sample2))

		# Getting signature matrix for sample1
		print "Getting signature matrix for sample1"
		s1_signature_matrix=np.full((1,no_seeds),sys.maxsize,dtype="int64")
		for token in set(sample1):
			for hash_function in xrange(no_seeds):
				currentHash=getHash(token,seeds[hash_function][0],seeds[hash_function][1])
				if currentHash<s1_signature_matrix[0][hash_function]:
					s1_signature_matrix[0][hash_function]=currentHash

		# Getting signature matrix for sample2
		print "Getting signature matrix for sample2"
		s2_signature_matrix=np.full((1,no_seeds),sys.maxsize,dtype="int64")
		for token in set(sample2):
			for hash_function in xrange(no_seeds):
				currentHash=getHash(token,seeds[hash_function][0],seeds[hash_function][1])
				if currentHash<s2_signature_matrix[0][hash_function]:
					s2_signature_matrix[0][hash_function]=currentHash

		print "Calculating minhash Jaccard values!"
		total=0
		for i in xrange(no_seeds):
			if s1_signature_matrix[0][i]==s2_signature_matrix[0][i]:
				total=total+1

		results.iloc[sizes.index(s),fracs.index(f)]=[total/(1.0*no_seeds)]

		# Checking if the two are candidates or not
		per_band=20
		no_bands=int(no_seeds/per_band)

		# print no_bands
		c=1000000007
		a=random.randint(1,c-1)
		b=random.randint(1,c-1)
		for b in range(no_bands):
			dictionary={}
			hashvalue1=long(0)
			hashvalue2=long(0)
			for j in xrange(b*per_band,(b+1)*per_band):
				# Another way to calculate hash is to xor with c
				# hashvalue1=hashvalue1+(((s1_signature_matrix[0][j]*a)+b)%c)
				# hashvalue2=hashvalue2+(((s2_signature_matrix[0][j]*a)+b)%c)
				hashvalue1=hashvalue1+(s1_signature_matrix[0][j]^c)
				hashvalue2=hashvalue2+(s2_signature_matrix[0][j]^c)
			if hashvalue1 not in dictionary:
					dictionary[hashvalue1]=[]
			if hashvalue2 not in dictionary:
					dictionary[hashvalue2]=[]
			dictionary[hashvalue1].append(0)
			dictionary[hashvalue2].append(1)
			# print "Band:",(b+1),"dictionary:",dictionary
			flag=False
			for hsh in dictionary:
				for y in dictionary[hsh]:
					for z in dictionary[hsh]:
						if y<z:
							flag=True
							if "Yes" not in results.iloc[sizes.index(s),fracs.index(f)]:
								results.iloc[sizes.index(s),fracs.index(f)].append("Yes")

		if (flag==False)&(len(results.iloc[sizes.index(s),fracs.index(f)])==1):
			results.iloc[sizes.index(s),fracs.index(f)].append("No")


print results
writer = pd.ExcelWriter('Results_XOR.xlsx')
# df1.to_excel(writer,'Sheet1')
results.to_excel(writer)
writer.save()

