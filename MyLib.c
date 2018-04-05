#include <stdio.h>
#include <stdlib.h>

void my_printf_f(float i) 
{
	printf("%f\n", i);
}

float my_scanf_f(void) 
{
	float x;
	scanf("%f",&x);
	return x;
}
