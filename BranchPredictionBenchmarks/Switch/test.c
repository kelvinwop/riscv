// Switch Program Benchmark
int main(){
	unsigned int START_FLAG = 9999;
	
	unsigned int totalCount = 0;
	for(unsigned int x=0; x < 100;x++){
		
		for(unsigned int i = 0; i < 5; i++){
			switch(i){
				case 0:
					totalCount++;
					break;
				case 1:
					totalCount++;
					break;
				case 2:
					totalCount++;
					break;
				case 3:
					totalCount++;
					break;
				case 4:
					totalCount++;
					break;	
			}
		}
	}
	
	unsigned int END_FLAG = 8888; 
	return 0;
}
