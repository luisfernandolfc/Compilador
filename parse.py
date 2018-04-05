#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import ply.yacc as yacc

import AST
import lex

lexer = lex.MyLexer()
lexer.build()
tokens = lexer.tokens
has_error = False

precedence = (
	('left', 'SOMA', 'SUBTRACAO'),
	('left', 'MULTIPLICACAO', 'DIVISAO')
)

def p_programa(p):
	'''programa : declaracao_global funcao_declaracao	
		            | funcao_declaracao
	'''	
	if(len(p) == 3):
		p[0] = AST.Node("programa_global",[p[1],p[2]])	
	else:
		p[0] = AST.Node("programa",[p[1]])	
	
	
def p_funcao_declaracao(p):
	'''funcao_declaracao : funcao funcao_declaracao
		            | funcao_principal
	'''
	if(len(p) == 3):
		p[0] = AST.Node("funcao_declaracao",[p[1], p[2]])
	else:
		p[0] = AST.Node("funcao_declaracao",[p[1]])

def p_funcao(p):
	'''funcao : tipo_funcao ID PARENTESES_E parametros PARENTESES_D expressoes FIM
		            | tipo_funcao ID PARENTESES_E PARENTESES_D expressoes FIM
	'''
	if(len(p) == 8):
		p[0] = AST.Node("FUNCAO",[p[4],p[6]],[p[1],p[2]])
	else:	            
		p[0] = AST.Node("FUNCAO",[p[5]],p[2])

def p_funcao_principal(p):
	'''funcao_principal : tipo_funcao PRINCIPAL PARENTESES_E parametros PARENTESES_D expressoes FIM
		            | tipo_funcao PRINCIPAL PARENTESES_E PARENTESES_D expressoes FIM
	'''
	if(len(p) == 8):
		p[0] = AST.Node("FUNC_PRINCIPAL",[p[4],p[6]],[p[1],p[2]])
	else:	            
		p[0] = AST.Node("FUNC_PRINCIPAL",[p[5]],[p[1],p[2]])	
		
def p_expressoes(p):
	'''expressoes : expressoes expressao
		       | expressao
	'''
	if(len(p) == 3):
		p[0] = AST.Node("expressoes",[p[1], p[2]])
	else:
		p[0] = AST.Node("expressoes",[p[1]])

def p_retorno(p):
	'''retorno : RETORNA factor'''		
	p[0] = AST.Node("retorno",[p[2]])	

def p_tipo_funcao(p):
	'''tipo_funcao : INTEIRO
			  | FLUTUANTE
			  | VAZIO
	'''
	if(p[1] == 'inteiro'):
		p[0] = AST.Node("INTEIRO_FUNC",[])
	elif(p[1] == 'flutuante'):
		p[0] = AST.Node("FLUTUANTE_FUNC",[])
	else:
		p[0] = AST.Node("VAZIO_FUNC",[])
	
		
def p_expressao(p):
	'''expressao : escreve_expre
	   	      | ler_expre
	   	      | atribuicao_expre
	   	      | repita_expre
	   	      | declaracao_tipo
	   	      | chama_func_expre	   	     
	   	      | se_expre
	   	      | retorno
	'''
	p[0] = AST.Node("expressao",[p[1]])

def p_declaracao_global(p):
	'''declaracao_global : declaracao_global declaracao_tipo
			  | declaracao_tipo			  
	'''
	if(len(p) == 3):
		p[0] = AST.Node("expressoes",[p[1], p[2]])
	else:
		p[0] = AST.Node("expressoes",[p[1]])
		
def p_declaracao_tipo(p):
	'''declaracao_tipo : INTEIRO DOIS_PONTOS ID
			  | FLUTUANTE DOIS_PONTOS ID			  
	'''
	if(p[1] == 'inteiro'):
		p[0] = AST.Node("INTEIRO",[],p[3])
	elif(p[1] == 'flutuante'):
		p[0] = AST.Node("FLUTUANTE",[],p[3])	
	
def p_atribuicao_expre(p):
	'''atribuicao_expre : declaracao_tipo ATRIBUICAO factor
			  | identificador ATRIBUICAO factor
	'''
	p[0] = AST.Node("ATRIBUICAO", [p[1],p[3]])	
	

def p_se_expre(p):
	'''se_expre : SE condicao ENTAO expressoes senao_expre FIM'''
	p[0] = AST.Node("SE",[p[2],p[4],p[5]])	


def p_senao_expre(p):
	'''senao_expre : SENAO expressoes	   
		    |
	'''
	if (len(p) == 3):
		p[0] = AST.Node("SENAO",[p[2]])
	else:
		p[0] = AST.Node("SENAO",[])

def p_escreve_expre(p):
	'''escreve_expre : ESCREVA PARENTESES_E chama_func_expre PARENTESES_D
	'''
	p[0] = AST.Node("ESCREVA", [p[3]])	

def p_ler_expre(p):
	'''ler_expre : LEIA PARENTESES_E identificador PARENTESES_D'''
	p[0] = AST.Node("LEIA", [p[3]])
	

def p_repita_expre(p):
	'''repita_expre : REPITA expressoes ATE condicao'''
	p[0] = AST.Node("REPITA", [p[2],p[4]])
		
def p_chama_func_expre(p):
	'''chama_func_expre : ID PARENTESES_E parametros_chamada PARENTESES_D
			    | ID PARENTESES_E PARENTESES_D
	'''
	if(len(p) == 5):
		p[0] = AST.Node("chama_funcao",[p[3]],p[1])
	else:
		p[0] = AST.Node("chama_funcao",[],p[1])
	
def p_exp_parametros_chamada(p):
	'''parametros_chamada : factor VIRGULA parametros_chamada
		              | factor
	'''
	if(len(p) == 4):
		p[0] = AST.Node("parametros_chamada",[p[1],p[3]])
	else:
		p[0] = AST.Node("parametros_chamada",[p[1]])

	
def p_parametros(p):
	'''parametros : declaracao_tipo VIRGULA parametros
		      | declaracao_tipo
	'''
	if(len(p) == 4):
		p[0] = AST.Node("parametros",[p[1],p[3]])
	else:
		p[0] = AST.Node("parametros",[p[1]])
		

def p_factor(p):
	'''factor : identificador
		  | constante
		  | PARENTESES_E factor PARENTESES_D
		  | operacao_aritmetica
	'''
	if (len(p) == 4):
		p[0] = AST.Node("factor",[p[2]])
	else:
		p[0] = AST.Node("factor",[p[1]])
		
def p_identificador(p):
	'''identificador : ID
	'''
	p[0] = AST.Node("ID",[],p[1])

def p_condicao(p):
	'''condicao : comparacao'''
	p[0] = AST.Node("condicao",[p[1]])

def p_constante(p):
	'''constante : NUMERO'''
	p[0] = AST.Node("constante",[],p[1])

def p_operador(p):
	'''operador : IGUAL
	            | MAIOR
	            | MAIOR IGUAL'''
	if (len(p) == 3):
		p[0] = AST.Node("operador",[],[p[1],p[2]])
	else:            
		p[0] = AST.Node("operador",[],p[1])

def p_operacao_aritmetica(p):
	'''operacao_aritmetica : factor SOMA factor
				| factor SUBTRACAO factor
				| factor MULTIPLICACAO factor
				| factor DIVISAO factor'''
	p[0] = AST.Node("operacao_aritmetica",[p[1],p[3]], p[2])

def p_comparacao(p):
	'''comparacao : factor operador factor
		      | PARENTESES_E comparacao PARENTESES_D '''
	if (p[1] == "("):
		p[0] = AST.Node("comparacao",[p[2]])
	else:
		p[0] = AST.Node("comparacao",[p[1], p[2], p[3]])

def p_error(p):
	print("Erro sintatico " + str(p))
	#print("Item ilegal: '%s', linha %d, coluna %d" % (p.value,p.lineno, p.lexpos))
	global has_error
	has_error = True

# def t_NEWLINE(p):
#         r'\n+'
#         p.lineno += len(p.value)

def ccparse(texto):
	return parser.parse(texto)

parser = yacc.yacc(debug=True)

if (__name__ == "__main__"):
	if (len(sys.argv) == 2):
		f = open(sys.argv[1], 'r')
		p = parser.parse(f.read(), debug=False)
		print(p)
	else:
		print("Passe apenas 1 argumento indicando o arquivo a ser analisado!")
