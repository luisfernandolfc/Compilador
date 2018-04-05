import lex
import sys
import parse
import semAnalyse
import codegen
from llvmlite import *
from subprocess import call

if(__name__ == "__main__"):
	if (len(sys.argv) == 3):
		f = open(sys.argv[1], 'r')
		p = parse.parser.parse(f.read(), debug=False)
		if(parse.has_error == True):
			exit(1)
		aly = semAnalyse.Analyse()
		aly.AnalyseInit(p,"global")
		print(aly.symbolTable)
		# gen = codegen.codegen()
		# gen.codegenInit(p)
		# print(gen.module)


		# print("Gravando build/program.ll...")
		# arq_saida = open('build/program.ll', 'w')
		# arq_saida.write(str(gen.module))
		# arq_saida.close()
		
		# call(["llc-3.3",  "build/program.ll"])
		# call(["gcc","-c","MyLib.c","-o","build/MyLib.o"])
		# call(["gcc","build/program.s","build/MyLib.o","-o", sys.argv[2]])
		

	else:
		print("Erro, parametros incorretos.\nUtilização: " + sys.argv[0] + " 'entrada' 'saida'")

	
