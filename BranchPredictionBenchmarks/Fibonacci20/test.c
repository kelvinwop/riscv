// Fibonacci Program Benchmark

static int fib(int i) {
	return (i>1) ? fib(i-1) + fib(i-2) : i; 
}	
	
int main(){
	
	unsigned int START_FLAG = 9999;
	fib(20);
	unsigned int END_FLAG = 8888; 
	return 0;
}
