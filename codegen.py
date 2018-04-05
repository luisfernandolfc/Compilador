# -*- coding: utf-8 -*-
#!/usr/bin/env python

from llvmlite import *
from llvmlite import ir
from llvmlite import binding
import AST
import string

class codegen():
	def __init__(self):
		self.symbols = {}
		self.module = ir.Module('programa')
		self.scope = 'global'
		self.builder = None
		self.func = None
		self.lastState = None
		self.printf_f = ir.Function(self.module, ir.FunctionType(ir.VoidType(), [ir.FloatType()]), "my_printf_f")
		self.scanf_f = ir.Function(self.module, ir.FunctionType(ir.FloatType(), []), "my_scanf_f")

	def codegenInit(self,p):
		
		if (p.type == "programa_global"):
			self.programa_init(p.children[1])
			#self.codegenFunc(p.children[1])			
		else:
			self.programa_init(p.children[0])

	def programa_init(self, p):
		# print(p.type)
		# print(p.children[1].type)
		#print(p.children[0].type)
		if (p.children[0].type == "FUNCAO"):
			#print(p.children[1].type)
			self.programa_init(p.children[1])
			self.funcao(p.children[0])
		# 	# self.principal(self.tree.child[1])			

		elif (p.children[0].type == "FUNC_PRINCIPAL"):			
			self.principal(p.children[0])


	def funcao(self,p):
		
		nome = p.leaf[1]
		self.scope = p.leaf[1]
		self.symbols[self.scope] = {}
		tipo = self.getTypeFunc(p)
		
		parametros = self.parametro_decl(p.children[0])

		self.func = ir.Function(self.module, ir.FunctionType(tipo, [parametros[i][0] for i in range(0, len(parametros))]), name = nome)
		bb = self.func.append_basic_block('entry')
		self.builder = ir.IRBuilder(bb)

		# for j, var in enumerate(parametros):
		# 	self.func.args[j].name = var[1]
		# 	print(var[1])
		# 	print(var[0])
		# 	self.symbols[self.scope][var[1]] = self.builder.alloca(var[0], name = var[1])
		# 	self.builder.store(self.func.args[j], self.symbols[self.scope][var[1]])
		
		self.expressoes_loop(p.children[1])
	

		self.scope = "global"

	def parametro_decl(self, p):
		args = []
		if (len(p.children) == 2):
			args.append((self.getTypeVar(p.children[0]), p.leaf))
			args = args + self.parametro_decl(p.children[1])

		elif (len(p.children) == 1):
			args.append((self.getTypeVar(p.children[0]), p.leaf))

		return args

	def principal(self, p):
		# print("Principal")
		# print(p.type)
		self.func = ir.Function(self.module, ir.FunctionType(ir.VoidType(), ()), name='main')
		bb = self.func.append_basic_block('entry')
		self.builder = ir.IRBuilder(bb)

		self.scope = "principal"
		self.symbols[self.scope] = {}		
		self.expressoes_loop(p.children[0])

		self.builder.ret_void()

		self.scope = "global"

	def expressoes_loop(self, p):
		# print(p.type)
		# print("\n"+p.type)
		
		if (len(p.children) == 2):			
			self.expressoes_loop(p.children[0])
			self.expressao(p.children[1])
		elif(len(p.children) == 1):
			# print(len(p.children))
			self.expressao(p.children[0])
		
		# 	self.sequencia_decl(node.child[0])
		# 	return self.declaracao(node.child[1])
		# else:
		# 	return self.declaracao(node.child[0])

	def expressao(self, p):
		# print(p.children[0].type)
		
		#print(p.children[0].leaf)
		if(p.children[0].type == "INTEIRO" or p.children[0].type == "FLUTUANTE"):
			self.gen_declaracao(p.children[0])
	
		# elif(p.children[0].type == "ATRIBUICAO"):
		# 	return self.codegenAtribuicao(p.children[0])

		# elif(p.children[0].type == "LEIA"):
		# 	return self.codegenLeia(p.children[0])

		# elif(p.children[0].type == "ESCREVA"):
		# 	return self.codegenEscreve(p.children[0])

		# elif(p.children[0].type == "SE"):
		# 	return self.codegenSe(p.children[0])
		
	

	def getTypeVar(self,p):
		if(p.type == "INTEIRO"):
			return ir.IntType(32)
		else:
			return ir.FloatType()

	def getTypeFunc(self,p):
		
		if(str(p.leaf[0]) == "'INTEIRO_FUNC'\n"):
			return ir.IntType(32)
		elif(str(p.leaf[0]) == "'FLUTUANTE_FUNC'\n"):
			return ir.FloatType()
		else:
			return ir.VoidType()
 
	def gen_declaracao(self,p):
		alloca = None
		tipo = self.getTypeVar(p)
		alloca = self.builder.alloca(tipo, name = p.leaf)
		self.symbols[self.scope][p.leaf] = [alloca,tipo]

	def c_f2i(self, v):
		return self.builder.fptosi(v, ir.IntType(32))

	def c_i2f(self, v):
		return self.builder.sitofp(v, ir.FloatType())   

	# def codegenLeia(self, p):
	# 	print(p.children[0].leaf[1])
		# var = self.builder.call(self.scanf_f, [])
		# if(self.symbols[self.scope][p.children[0].leaf][1] == IntType(32)):
		# 	var = self.c_f2i(var)
		# self.builder.store(var,self.symbols[self.scope][p.children[0].leaf][0])

	
		
	def codegenAtribuicao(self,p):
		value = None
		# print(p.children[0].type)
		value = self.codegenExpression(p.children[1],p.children[0])
		try:
			self.builder.store(value,self.symbols[p.children[0].leaf][0])
		except:
			self.builder.store(value,self.symbols[self.scope][p.children[0].leaf][0])

	def codegenExpression(self,p,p2):
		if(len(p.children[0].children) == 0):
			return self.codegenUniqueValue(p,p2)
		else:
			p1 = p.children[0]
			left = self.codegenExpression(p1.children[0],p2)
			right = self.codegenExpression(p1.children[1],p2)
			op = p.children[0].leaf
			if(op == "+"):
				if (self.symbols[self.scope][p2.leaf][1] == ir.IntType(32)):
					return self.builder.add(left, right, 'addtmp')
				else:
					return self.builder.fadd(left, right, 'addtmp')
			elif(op == "-"):
				if (self.symbols[self.scope][p2.leaf][1] == ir.IntType(32)):
					return self.builder.sub(left, right, 'subtmp')
				else:
					return self.builder.fsub(left, right, 'subtmp')         
			elif(op == "*"):
				if (self.symbols[self.scope][p2.leaf][1] == ir.IntType(32)):
					return self.builder.mul(left, right, 'mulmp')
				else:
					return self.builder.fmul(left, right, 'multmp') 
			elif(op == "/"):
				if (self.symbols[self.scope][p2.leaf][1] == ir.IntType(32)):
					return self.builder.fdiv(left, right, 'divtmp')
				else:
					return self.builder.fdiv(left, right, 'divtmp') 


	def codegenUniqueValue(self,p,p2):
		var = p2
		value = p
		if(var != None):
			if(self.symbols[self.scope][var.leaf][1] == ir.IntType(32) and isinstance(value.children[0].leaf,(int,float))):
				return ir.Constant(ir.IntType(32),value.children[0].leaf)
			elif(self.symbols[self.scope][var.leaf][1] == ir.FloatType() and isinstance(value.children[0].leaf,(int,float))):
				return ir.Constant(ir.FloatType(32),value.children[0].leaf)
			else:				
				return self.builder.load(self.symbols[self.scope][value.children[0].leaf][0])                           
				
		else:
			if(isinstance(value.children[0].leaf,(int,float))):
				return ir.Constant(ir.FloatType(),value.children[0].leaf)
			else:
				result = self.builder.load(self.symbols[self.scope][value.children[0].leaf][0])
				if(self.symbols[self.scope][value.children[0].leaf][1] == ir.IntType(32)):
					result = self.c_i2f(result)
				return result

	
	
	def genNewBlock(self):
		block = self.func.append_basic_block('entry')
		self.builder = ir.IRBuilder(block)

	def codegenArgsFuncao(self,p):
		tipos = []
		if(p.type == "parametros"):
			tipo = self.getType(p.children[0])
			tipos.append([tipo,p.children[0].leaf])
			if(len(p.children) > 1):
				tipos = tipos + self.codegenArgsFuncao(p.children[1])
		return tipos
		
	def codegenExpressions(self,p): 
		try:
			self.codegenInstrucao(p.children[0])
			if len(p.children)>1:
				self.codegenExpressions(p.children[1])
		except:
			pass    

	def codegenChamadaFuncao(self,p):
		args = self.codegenArgsChamadaFuncao(p.children[0])
		func = self.module.get_function_named(p.leaf)
		return self.builder.call(func, args, 'calltmp')


	def codegenArgsChamadaFuncao(self,p):
		args = []
		args.append(self.codegenExpression(p.children[0],None))
		if(len(p.children) > 1):
			args = args + self.codegenArgsChamadaFuncao(p.children[1])        
		return args