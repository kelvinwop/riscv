class NotTakenPredictor: 
    # Used by SiFive E20,E21,E24 Core 
    def __init__(self):
        self.totalPredictions = 0
        self.totalPredictionsMiss = 0
        self.totalPredictionsHit = 0
       
    def predict(self,BranchOutcome):
        
        prediction = "NOT TAKEN"

        self.totalPredictions += 1
        if(prediction==BranchOutcome):
            self.totalPredictionsHit += 1
        else:
            self.totalPredictionsMiss += 1

    def printStatistics(self):
        print("Satic Not Taken Branch Predictor Summary: ")
        print("Total Predictions:", self.totalPredictions)
        print("Total Predictions Hit:", self.totalPredictionsHit)
        print("Total Predictions Miss:", self.totalPredictionsMiss)