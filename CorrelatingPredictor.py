class CorrelatingPredictor: 
    
    def __init__(self,m,n):
        self.totalPredictions = 0
        self.totalPredictionsMiss = 0
        self.totalPredictionsHit = 0
        self.m = m # Looking at the last b branches
        self.n = n # how big should the n-bit counter be  

        self.branchPredictionBuffer = dict() # Stores pairs of 1 (TAKEN) or 0 (NOT TAKEN)
        self.globalBranchHistory = [0] * self.m # Global history, Initial State all 0s

    def newState(self,oldState,outcome):
        
        # 4 States 0 1 (Predict Not Taken) 2 3 Predict Taken
        if(oldState == 0 ):
            if(outcome == "NOT TAKEN"):
                return 0
            else: 
                return 1
        if(oldState == 1):
            if(outcome == "NOT TAKEN"):
                return 0
            else: 
                return 3
        if(oldState == 2):
            if(outcome == "NOT TAKEN"):
                return 0
            else: 
                return 3
        if(oldState == 3):
            if(outcome == "NOT TAKEN"):
                return 2
            else: 
                return 3

    def predict(self, BranchInstruction, BranchOutcome):
        
        prediction = "NOT TAKEN"
        branchInstructionAddress = BranchInstruction[22:32]

        branchInstructionAddress = branchInstructionAddress + ''.join(map(str, self.globalBranchHistory)) 
        # print(branchInstructionAddress, "Branch History", self.globalBranchHistory)

        # Determening Prediction
        if(branchInstructionAddress in self.branchPredictionBuffer ):
            if(self.branchPredictionBuffer[branchInstructionAddress] <= 1):
                prediction = "NOT TAKEN"
            else:
                prediction = "TAKEN"
        else:
            self.branchPredictionBuffer[branchInstructionAddress]  = 0 # Initial State of 2-bit Predictor 

        oldState = self.branchPredictionBuffer[branchInstructionAddress]

        # Calculating Prediction Accuracy                                                         
        self.totalPredictions += 1
        if(prediction==BranchOutcome):
            self.totalPredictionsHit += 1
        else:
            self.totalPredictionsMiss += 1
            # Update Prediction 
            newState = self.newState(oldState,BranchOutcome)
            self.branchPredictionBuffer[branchInstructionAddress] = newState
            # print(branchInstructionAddress,"Old State:",oldState,"OutCOme: ", BranchOutcome,"New State: ", newState )
        
        # Shifting the Global History Resgiter 
        self.globalBranchHistory.pop(0)
        intOutcome = 0
        if(BranchOutcome=='TAKEN'):
            intOutcome = 1
        self.globalBranchHistory.append(intOutcome)

    def printStatistics(self):
        print("Dynamic Correlating Predictor Summary: ")
        print("Total Predictions:", self.totalPredictions)
        print("Total Predictions Hit:", self.totalPredictionsHit)
        print("Total Predictions Miss:", self.totalPredictionsMiss)