import AST
import string


class table:
	def __init__(self, type, scope, value, numberParam=[],initialized=False, use = False):
		self.type = type
		self.scope = scope
		self.value = value
		self.initialized = initialized
		self.numberParam = []
		self.used = use
	def __repr__(self):
		value = len(self.numberParam)	
		if (self.type == "FUNCAO" or self.type == "FUNC_PRINCIPAL"):				
			return '(%s, %i)\n' % (self.type, value)
		else:
			return '(%s, %s,)\n' % (self.type, self.scope)

class Analyse():

	def __init__(self):
		self.symbolTable = {}
		self.count =0

	def AnalyseInit(self,p,scope):
		#print(p.type)
		# print(p.children[0])
		# print(scope)
		# print(p.children[1])
		if(p.type == "programa_global"):	
			self.dec_varglobal(p.children[0],scope)	
			self.dec_funcao(p.children[1],str(p.children[1].leaf))
		else:
			self.dec_funcao(p.children[0],str(p.children[0].leaf))

		#Checar variaveis não inicializadas
		for item in self.symbolTable:
			if ((self.symbolTable[item].type == "INTEIRO" or self.symbolTable[item].type == "FLUTUANTE") and self.symbolTable[item].initialized != True):
				print('Erro Semântico - Variável:"'+item+'" não foi inicializada')	

		#Checar variaveis não utilizadas
		for item in self.symbolTable:
			if ((self.symbolTable[item].type == "INTEIRO" or self.symbolTable[item].type == "FLUTUANTE") and self.symbolTable[item].used!= True):
				print('Erro Semântico - Variável:"'+item+'" não foi utilizada')			
		
	
	#Varáveis globais
	def dec_varglobal(self,p,scope):
		# print(p.type)
		# print(p.leaf)
		# print(scope)
		if(p.type == "INTEIRO"  and p.leaf not in self.symbolTable and scope == "global"):
			self.symbolTable[p.leaf] = table(p.type,scope,0, 0)
		elif(p.type == "INTEIRO"  and p.leaf in self.symbolTable and scope == "global"):
			print(self.symbolTable)
			print('Erro Semântico - Variável:"'+p.leaf+'" já foi declarada')
			exit(1)
		if(p.type == "FLUTUANTE" and p.leaf not in self.symbolTable and scope == "global"):
			self.symbolTable[p.leaf] = table(p.type,scope,0, 0)
		elif(p.type == "FLUTUANTE"  and p.leaf in self.symbolTable and scope == "global"):
			print('Erro Semântico - Variável:"'+p.leaf+'" já foi declarada')
			exit(1)
		
		
		if(p.leaf != None):
			if isinstance(p.leaf, AST.Node):
				self.dec_varglobal(p.leaf,scope)
		for child in p.children:
			if isinstance(child, AST.Node):
				self.dec_varglobal(child,scope)
	
	def procura_factor(self, p, nomeFuncao, tipo):
		
		if (p.type == "factor"):
			self.procura_factor(p.children[0], nomeFuncao, tipo)
		elif (p.type == "identificador" or p.type == "constante"):
			if (str(tipo) == "'INTEIRO_FUNC'\n"):
				tipo = "INTEIRO"
			else:
				tipo = "FLUTUANTE"
			self.checa_coercao(p, tipo, nomeFuncao)

	def checa_retorno(self, p, nomeFuncao, tipo):
		
		# print(p.type)
		# print(p.leaf)
		if(p.type == "retorno" and str(tipo) == "'VAZIO_FUNC'\n"):
			print('Erro Semântico - Função:"'+nomeFuncao+'" é do tipo VAZIO e não deve possuir retorno')	
			exit(1)

		elif(p.type == "retorno" and (str(tipo) == "'INTEIRO_FUNC'\n" or str(tipo) == "'FLUTUANTE_FUNC'\n")):
			self.procura_factor(p.children[0], nomeFuncao, tipo)
		for child in p.children:
			self.checa_retorno(child, nomeFuncao, tipo)

	def checa_atribuicao(self, p, scope):
		
		#Checando as variaveis		
		if (str(p.children[0].leaf)+"."+scope in self.symbolTable and scope != "None"):
			self.symbolTable[p.children[0].leaf+"."+scope].initialized = True		
			self.checa_coercao(p.children[1], self.symbolTable[p.children[0].leaf+"."+scope].type, scope)				
		elif (str(p.children[0].leaf) in self.symbolTable and scope != "None"):
			self.symbolTable[p.children[0].leaf].initialized = True		
			self.checa_coercao(p.children[1], self.symbolTable[p.children[0].leaf].type, scope)	

	def checa_coercao(self, p, tipo, scope):
		
		if (str(p.leaf)+"."+scope in self.symbolTable and (tipo == "INTEIRO" or tipo == "FLUTUANTE")):
			if (self.symbolTable[p.leaf+"."+scope].type != tipo and tipo == "INTEIRO"):
				print('Erro Semântico - Tipo "'+tipo+'" não é compativel com o tipo "'+self.symbolTable[p.leaf+"."+scope].type+'".')	
				exit(1)
			else:
				self.symbolTable[p.leaf+"."+scope].used = True
		#Checa Variavel Global
		elif (str(p.leaf) in self.symbolTable and (tipo == "INTEIRO" or tipo == "FLUTUANTE")):
			if (self.symbolTable[p.leaf].type != tipo and tipo == "INTEIRO"):
				print('Erro Semântico - Tipo "'+tipo+'" não é compativel com o tipo "'+self.symbolTable[p.leaf].type+'".')	
				exit(1)
			else:
				self.symbolTable[p.leaf].used = True		
		elif(p.type == "constante" and tipo == "INTEIRO" and isinstance(p.leaf, float)):
			print('Erro Semântico - Tipo "'+tipo+'" não é compativel com o tipo "FLUTUANTE"')	
			exit(1)	
		
		else:
			for child in p.children:
				self.checa_coercao(child, tipo, scope)

	def checa_usada(self, p, scope):
		
		if (p.type == "ID"):
			if (p.leaf+"."+scope in self.symbolTable):			
				self.symbolTable[p.leaf+"."+scope].used = True
			elif (p.leaf in self.symbolTable):
				self.symbolTable[p.leaf].used = True
		for child in p.children:
				self.checa_usada(child, scope)

	def checa_comparacao(self, p, scope):
		
		if (len(p.children) == 1):
			self.checa_comparacao(p.children[0], scope)
		elif (len(p.children) == 3):			
			self.checa_factor(p.children[0], scope)
			self.checa_factor(p.children[2], scope)

	def checa_factor(self, p, scope):		
		if (str(p.children[0].leaf)+"."+scope in self.symbolTable):
			self.symbolTable[str(p.children[0].leaf)+"."+scope].used = True
		elif (str(p.children[0].leaf) in self.symbolTable):
			self.symbolTable[str(p.children[0].leaf)].used = True

	def dec_funcao(self,p,scope):
		#Checando se é uma função e se já foi ou não declarada
		# print(p.type)
		# print(p.leaf)		

		if(p.type == "FUNCAO" and p.leaf[1] == "PRINCIPAL"):
			print('Erro Semantico - Função "' +p.leaf[1]+ '" é a função principal')
			exit(1)		
		if(p.type == "FUNCAO" and p.leaf[1] not in self.symbolTable):
			
			#Procura o nó com as expressões e então checa se existe retorno
			if isinstance(p.children[1], AST.Node):
				self.checa_retorno(p.children[1], p.leaf[1], p.leaf[0])		
			elif isinstance(p.children[0], AST.Node):
				self.checa_retorno(p.children[0], p.leaf[1], p.leaf[0])		
			#Adiciona na tabela de simbolos.
			self.symbolTable[str(p.leaf[1])] = table(p.type,scope,0, 0)	
			if isinstance(p.children[0], AST.Node):
				self.dec_funcao(p.children[0],str(p.leaf[1]))
			if isinstance(p.children[1], AST.Node):
				self.dec_funcao(p.children[1],str(p.leaf[1]))
		elif(p.type == "FUNCAO" and p.leaf[1] in self.symbolTable):
			print('Erro Semantico - Função "' +p.leaf[1]+ '" já foi declarada')
			exit(1)
		

		#Checando a função principal, sintática garante que só terá uma função principal
		if(p.type == "FUNC_PRINCIPAL" and p.leaf[1] not in self.symbolTable):
		#Checa se é uma função VOID			
			if (str(p.leaf[0]) == "'VAZIO_FUNC'\n"):
				self.checa_retorno(p.children[0], p.leaf[1], p.leaf[0])

			self.symbolTable[str(p.leaf[1])] = table(p.type,scope,0, 0)
			if isinstance(p.children[0], AST.Node):
				self.dec_funcao(p.children[0],str(p.leaf[1]))
			if isinstance(p.children[1], AST.Node):
				self.dec_funcao(p.children[1],str(p.leaf[1]))		

		#Checando variáveis.
		if((p.type == "INTEIRO" or p.type == "FLUTUANTE") and p.leaf == scope):
			print('Erro Semântico - "'+p.leaf+'" é uma função')
			exit(1)
		elif(p.type == "INTEIRO" and p.leaf+"."+scope not in self.symbolTable and p.leaf not in self.symbolTable and scope!= "None"):
			self.symbolTable[p.leaf+"."+scope] = table(p.type,scope,0, 0)			
		elif(p.type == "INTEIRO" and (p.leaf+"."+scope in self.symbolTable or p.leaf in self.symbolTable) and scope!= "None"):
			if (p.leaf in self.symbolTable):
				print('Erro Semântico - Variável:"'+p.leaf+'" já foi declarada como global')				
			else:
				print('Erro Semântico - Variável:"'+p.leaf+'" já foi declarada')
			exit(1)

		if(p.type == "FLUTUANTE" and p.leaf+"."+scope not in self.symbolTable and p.leaf not in self.symbolTable and scope!= "None"):
			self.symbolTable[p.leaf+"."+scope] = table(p.type,scope,0, 0)
		elif(p.type == "FLUTUANTE" and (p.leaf+"."+scope in self.symbolTable or p.leaf in self.symbolTable) and scope!= "None"):
			if (p.leaf in self.symbolTable):
				print('Erro Semântico - Variável:"'+p.leaf+'" já foi declarada como global')				
			else:
				print('Erro Semântico - Variável:"'+p.leaf+'" já foi declarada')
			exit(1)
		
		# Checando coerção Inteiro<->Float
		if (p.type == "ATRIBUICAO" and scope != "None"):			
			self.checa_atribuicao(p, scope)

		if (p.type =="LEIA"):
			self.symbolTable[p.children[0].leaf+"."+scope].initialized = True

		if (p.type =="chama_funcao"):
			# print(p.leaf)
			if isinstance(p.children[0], AST.Node):
				self.checa_usada(p.children[0], scope)
				#print(p.children[0].children[0].children[0].leaf)
				#print("ENTROU")
			#print(p.children[0].p.children[0].type)
		
		if (p.type == "comparacao" and scope != "None"):
			self.checa_comparacao(p, scope)	

		#Checando a chamada de função, caso a função ainda não foi criada, erro semântico.
		if(p.type == "chama_funcao" and p.leaf not in self.symbolTable):
			print('Erro Semântico - Função:"'+p.leaf+'" não foi declarada')
			exit(1)
		elif(p.type == "chama_funcao" and p.leaf in self.symbolTable):
			#Caso a função tenha o mesmo nome que seu escopo
			if(p.leaf == scope):
				print('Erro Semântico - Não é possível chamar a função:"'+p.leaf+'" dentro de seu escopo')
				exit(1)
			self.count = 0
			self.ArgsChamadaFunc(p)
			#Caso os argumentos da chamada sejam maiores ou menores.
			if(self.count > len(self.symbolTable[p.leaf].numberParam)):
				print('Erro Semântico - Função:"'+p.leaf+'" possui muitos argumentos')
				exit(1)
			elif(self.count < len(self.symbolTable[p.leaf].numberParam)):
				print('Erro Semântico - Função:"'+p.leaf+'" possui poucos argumentos')	
				exit(1)

		#Checar os parametros para declaração de variáveis
		if(p.type == "parametros"):
			self.symbolTable[scope].numberParam.append(p.children[0].type)
		if(p.type == "ID" and (p.leaf+"."+scope not in self.symbolTable and p.leaf not in self.symbolTable) and scope!= "None"):
			print('Erro Semântico - Variável:"'+p.leaf+'" não foi declarada')
			exit(1)
		if(p.leaf != None):
			if isinstance(p.leaf, AST.Node):
				self.dec_funcao(p.leaf,scope)
		for child in p.children:
			try:
				if isinstance(child, AST.Node):
					self.dec_funcao(child,scope)
			except:
				pass			

	def ArgsChamadaFunc(self,p):
		if(p.type == "parametros_chamada"):
			self.count+=1	
		for child in p.children:
			self.ArgsChamadaFunc(child)	