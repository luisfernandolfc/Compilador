#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import ply.lex as lex


class MyLexer(object):

	#def __init__(self):
		
	reservadas = {
		'se': 'SE',
		'então': 'ENTAO',
		'senão': 'SENAO', 
		'fim': 'FIM', 
		'repita': 'REPITA', 
		'até': 'ATE', 
		'leia': 'LEIA',
		'escreva': 'ESCREVA', 
		'inteiro': 'INTEIRO',
		'flutuante': 'FLUTUANTE',
		'vazio': 'VAZIO',
		'principal': 'PRINCIPAL',
		'retorna': 'RETORNA'
	}

	tokens = [
		'NUMERO',
		'SOMA',
		'SUBTRACAO',
		'MULTIPLICACAO',
		'DIVISAO',
		'IGUAL',
		'MAIOR',
		'VIRGULA',
		'ATRIBUICAO',
		'DOIS_PONTOS',
		'PARENTESES_E',
		'PARENTESES_D',
		'ID'
	] + list(reservadas.values())

	t_SOMA    = r'\+'
	t_SUBTRACAO   = r'-'
	t_MULTIPLICACAO   = r'\*'
	t_DIVISAO  = r'/'
	t_PARENTESES_E  = r'\('
	t_PARENTESES_D  = r'\)'
	t_IGUAL = r'='
	t_MAIOR = r'>'
	t_ATRIBUICAO = r':='
	t_DOIS_PONTOS = r':'
	t_VIRGULA = r','
	
	def t_NUMERO(self, t):
		r'[0-9]+(.[0-9]+)?(e-?[0-9]+)?'
		if ('e' in t.value) or ('.' in t.value):
			t.value = float(t.value)
		else:
			t.value = int(t.value)
		return t

	def t_COMENTARIO(self, t):
		r'({(.|\n)*?\})'
		t.lineno += t.value.count('\n')

	def t_NOVALINHA(self, t):
		r'\n+'
		t.lexer.lineno += len(t.value)

	def t_ID(self, t):
		r'[a-zA-ZÀ-ÿ_][a-zA-ZÀ-ÿ0-9_]*'
		t.type = self.reservadas.get(t.value, 'ID')
		return t

	t_ignore  = ' \t'

	def t_error(self, t):
		print("Illegal character %s" % t.value[0])
		t.lexer.skip(1)

	# Build the lexer
	def build(self,**kwargs):
		self.lexer = lex.lex(module=self, **kwargs)

	# Test it outputhn
	def test(self, data):
		self.lexer.input(data)
		while True:
			tok = self.lexer.token()
			if not tok: 
				break
			print (tok)

if (__name__ == "__main__"):
	if (len(sys.argv) == 2):
		f = open(sys.argv[1], 'r')
		MLex = MyLexer()
		MLex.build()
		MLex.test(f.read())
	else:
		print("Error. Ex: lex.py script.tpp")	
