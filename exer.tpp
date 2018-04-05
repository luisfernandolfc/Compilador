inteiro fatorial(inteiro: n)
    se n > 0 então {não calcula se n > 0}       
        inteiro: fat  
        fat := 1
        repita
            fat := fat * n
            n := n - 1
        até n = 0
        retorna(fat) {retorna o valor do fatorial de n}
    senão
    	retorna(0)
    fim
fim

vazio fatorial2(inteiro: s)
   inteiro: c  
   c := s
   s := c
   
fim

vazio principal()
    inteiro: n 
    leia(n)
    escreva(fatorial(n))

fim