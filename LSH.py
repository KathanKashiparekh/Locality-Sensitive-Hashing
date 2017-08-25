from __future__ import division
from random import randint
from time import time
from sys import argv
import numpy as np  
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

n=2
dataset=np.random.randint(low=0,high=2000,size=(n,5000),dtype="int64")
jaccard_actual=np.full((n,n),0.0)
np.savetxt('dataset.txt',dataset,fmt='%.0f')

# Calculate brute-force Jaccard values.
t=time()
for i in xrange(n):
	for j in xrange(i+1,n):
		jaccard_actual[i][j]=len(set(dataset[i])&set(dataset[j]))/(len(set(dataset[i])|set(dataset[j])))

print "Actual Jaccard value calculation took: \t\t %.2f"%(time()-t)

no_seeds=100
seeds=generateMinHashSeeds(no_seeds)
signature_matrix=np.full((n,no_seeds),sys.maxsize,dtype="int64")
jaccard_minhash=np.full((n,n),0.0)
# Calculating the minhash values of the dataset
t=time()
for i in xrange(n):
	# print dataset[i]
	for token in set(dataset[i]):
		for hash_function in xrange(no_seeds):
			currentHash=getHash(token,seeds[hash_function][0],seeds[hash_function][1])
			# currentHash=hash(token)^1000000007
			# print "Token:",token," Hash:",currentHash
			if currentHash<signature_matrix[i][hash_function]:
				signature_matrix[i][hash_function]=currentHash

print "MinHashing completed in: \t\t %.2f"%(time()-t)

# Calculating jaccard values of the minhash signature matrix.
t=time()
for i in xrange(n):
	for j in xrange(i+1,n):
		for hash_val in xrange(no_seeds):
			if signature_matrix[i][hash_val]==signature_matrix[j][hash_val]:
				jaccard_minhash[i][j]+=1
		jaccard_minhash[i][j] /= (1.0 * no_seeds)

print "Time taken to compute minhash jaccard values:\t\t %.2f" % (time() - t)

# Prints first two data-points and results of two methods cam be compared from the other two results printed
# print dataset[:2][:]
print jaccard_actual
print jaccard_minhash

# Calculating average error between both prediction.
avgerr = 0.0
for i in xrange(n):
	for j in xrange(i + 1, n):
		if jaccard_actual[i][j] != 0:
			err = abs(jaccard_minhash[i][j] - jaccard_actual[i][j])/jaccard_actual[i][j]
			avgerr += err

print "Average Relative Error between actual and minhash jaccard: %.2f" % ((avgerr/((n * (n - 1))/2)))

# LSH. Candidate pairs are stored in the candidates set. 
t=time()
candidates=set()
per_band=20
no_bands=int(no_seeds/per_band)
lsh_seeds=generateMinHashSeeds(no_bands)

# print no_bands
c=1000000007
a=random.randint(1,c-1)
b=random.randint(0,c-1)
for b in range(no_bands):
	dictionary={}
	for i in xrange(n):
		hashvalue=long(0)
		for j in xrange(b*per_band,(b+1)*per_band):
			hashvalue=hashvalue+(((signature_matrix[i][j]*a)+b)%c)
			# hashvalue=hashvalue+(signature_matrix[i][j]^1000000007)
		if hashvalue not in dictionary:
			dictionary[hashvalue]=[]
		dictionary[hashvalue].append(i)
	print "Band:",(b+1),"dictionary:",dictionary
	for hsh in dictionary:
		for y in dictionary[hsh]:
			for z in dictionary[hsh]:
				if y<z:
					candidates.add((y,z))

print "Candidates: " + str(len(candidates)) + ", time taken: %.2f" % (time() - t)