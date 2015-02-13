#!/usr/bin/python
from sys import argv
from sys import exit
from random import randrange as rand
from functools import reduce as foldl

''' 
	Class to work with portuguese fiscal identification number
	Python 2/3 compatible
'''
class Nif:
	''' Valid combinations to Nif '''
	_COMBINATIONS=[
		[1],[2],     # Pessoa singular
		#[3],        # Pessoa singular (ainda nao atribuido)
		[5],         # Pessoa coletiva
		[6],         # Organismo publico
		[7,0],       # Heranca indivisa colectiva
		[7,1],       # Nao residentes colectivos
		[7,7],       # Nif oficiso de sujeito passivo
		[7,9],       # Excepcional Expo '98
		[8],         # Emprestimo individual
		[9,0],[9,1], # Condominios, Sociedades ou herancas individuais
		[9,8],       # Nao residentes sem establecimento estavel
		[9,9],       # Sociedades civis sem personalidade juridica
	]

	''' Internal Nif representation'''
	_nif = []

	''' Length of the base numbers, 
	does not include the checksum number'''
	_BASE_LENGTH = 8

	''' Normalizes the probabilities of each Nif valid Combination '''
	@staticmethod
	def _fair_combinations():
		gen = lambda c: (([c[0]] for _ in range(10)) if len(c)==1 else [c])
		norm = lambda x: [w for y in x for w in y]
		return norm((gen(c) for c in Nif._COMBINATIONS))

	''' Nif: supports string, array<int>, Nif, None '''
	def __init__(self,num=None, fill=False):
		if not num:
			pass
		elif isinstance(num,Nif):
			self._nif = num
		elif isinstance(num,list):
			self._nif=num
		elif isinstance(num,str):
			self._nif=list(map(int,list(num)))
			if fill:
				length = len(self._nif)
				if length < 8:
					self._nif[length:]=[rand(9) for i in range(length,8)]
				if length < 9:
					self._nif[8:] = [ self.eval_sum() ]

	def __iter__(self):
		return (i for i in self._nif)

	def __getitem__(self,item):
		return self._nif[item]

	def __getslice__(self,slice,item):
		return Nif(self._nif.__getslice__(slice,item))

	def __setslice__(self,slice,item):
		return self._nif.__setslice__(slice,item)

	def __setitem__(self, index, item):
		if isinstance(index,slice):
			if -Nif._BASE_LENGTH < index.start < Nif._BASE_LENGTH:
				self._nif[index]=item
				self.fix_sum()
			else:
				raise IndexError(
						"Nif: only the first {0} numbers can be assigned"
						.format(Nif._BASE_LENGTH)
					)

		elif isinstance(index,int):
			self._nif[index] = item
			self.fix_sum()

	def __str__(self):
		return ''.join(map(str,self._nif))

	def __int__(self):
		return foldl(lambda x,y: x*10+int(y),self._nif,0)

	'''' Generates a valid Nif with random digits 
		3 steps algorithm:
			- create the list with the initial valid combinations
			- randomize the following digits
			- add the control digit
	'''
	def generate(self):
		if not hasattr(self,'_balanced'):
			self._balanced = Nif._fair_combinations()
		comb = self._balanced
		_nif = comb[rand(len(comb))]
		lnif = len(_nif)
		_nif[lnif:]=[rand(9) for n in range(Nif._BASE_LENGTH - lnif)]
		_nif[Nif._BASE_LENGTH:] = [Nif._eval_sum(_nif)]
		self._nif = list(_nif)
		return self

	''' Validates a Nif 
		it must validate 3 rules:
			- 9 digit length
			- start with one of valid combinations
			- the last digit must be a valid checkSum
	'''
	def is_valid(self):
		validator = lambda x,y: x or str(self).startswith(''.join(map(str,y)))
		return (len(self._nif) == Nif._BASE_LENGTH + 1			# Rule 1
			and foldl(validator, Nif._COMBINATIONS, False) 		# Rule 2
			and int(self.get_sum_digit()) == self.eval_sum())	# Rule 3
	
	valid = property(is_valid)

	''' Sum Digit getter/setter '''
	def get_sum_digit(self):
	    return self._nif[Nif._BASE_LENGTH]
	def set_sum_digit(self, value):
	    self._nif[Nif._BASE_LENGTH:] = [value]
	
	sum_digit = property(get_sum_digit,set_sum_digit)

	''' Corrects the Sum Digit '''
	def fix_sum(self):
		self.set_sum_digit(self.eval_sum())
		return self

	def eval_sum(self):
		return Nif._eval_sum(self._nif[:Nif._BASE_LENGTH])

	''' Evaluates the Sum digit value 
		x = digits( nif )
		a = mod( sum( (9-i) . x[i] ), 11), 0 <= i < 8
		result = 0,			a = 1 or a = 0 
				 11 - a,	a >= 2
	'''
	@staticmethod
	def _eval_sum(elements):
		_ruler = lambda x,y: x + ((9 - y[0]) * int(y[1]))
		sum = foldl(_ruler, enumerate(elements[:Nif._BASE_LENGTH]), 0) % 11
		return 0 if sum < 2 else 11 - sum

	''' Creates a Nif object and returns it with a valid Nif '''
	@staticmethod
	def generate_nif():
		return Nif().generate()

	''' Generates a Valid Nif or fixes a Nif passed by argument '''
	@staticmethod
	def main():
		if len(argv) <= 1:
			n=Nif()
			print(n.generate())
		else:
			n=Nif(argv[1],True)
			n.fix_sum()
			if n.is_valid():
				print(n)
			else:
				print("Invalid Nif: {0}".format(argv[1]))
				exit(1)

if __name__ == '__main__':
	Nif.main()
