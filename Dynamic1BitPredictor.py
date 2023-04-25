class OneBitPredictor: 
    
    def __init__(self):
        self.totalPredictions = 0
        self.totalPredictionsMiss = 0
        self.totalPredictionsHit = 0
        self.branchPredictionBuffer = dict() # Stores pairs of 1 (TAKEN) or 0 (NOT TAKEN)

    def predict(self, BranchInstruction, BranchOutcome):
        
        prediction = "NOT TAKEN"
        branchInstructionAddress = BranchInstruction[22:32]

        # Determening Prediction
        if(branchInstructionAddress in self.branchPredictionBuffer ):
            if(self.branchPredictionBuffer[branchInstructionAddress] == 1):
                prediction = "TAKEN"
            else:
                prediction = "NOT TAKEN"
        else:
            self.branchPredictionBuffer[branchInstructionAddress]  = (BranchOutcome == "TAKEN") 

        # Calculating Prediction Accuracy                                                         
        self.totalPredictions += 1
        if(prediction==BranchOutcome):
            self.totalPredictionsHit += 1
        else:
            self.totalPredictionsMiss += 1
            self.branchPredictionBuffer[branchInstructionAddress] = (BranchOutcome == "TAKEN") 

    def printStatistics(self):
        print("Dynamic 1-Bit Branch Predictor Summary: ")
        print("Total Predictions:", self.totalPredictions)
        print("Total Predictions Hit:", self.totalPredictionsHit)
        print("Total Predictions Miss:", self.totalPredictionsMiss)