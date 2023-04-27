// Nested Program Benchmark
int main(){
	unsigned int START_FLAG = 9999;
	unsigned int y = 0;
	unsigned int z = 0;
	for(unsigned int i = 0; i < 100; i++){
		
		if(i<50){
		  	y++;
		  	if(y<20){
		  		
		  		z++;
		  	}else{
		  		if (z%2==0){
		 	 		z++;
		 	 	}
		  	}
		}else{
		 	y++;	
		 	if(y<50){
		 	 z++;	
		 	}else{
		 	 	if (z%2==0){
		 	 		z++;
		 	 	}
		 	}
			
		}
	}
	unsigned int END_FLAG = 8888; 
	return 0;
}
