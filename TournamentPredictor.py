class TournamentPredictor: 
    # Uses 2 bit predictors 
    def __init__(self,m,n):
        self.totalPredictions = 0
        self.totalPredictionsMiss = 0
        self.totalPredictionsHit = 0

        self.totalGlobalPredictorUsed = 0
        self.totalLocalPredictorUsed = 0

        self.totalGlobalPredictorHit = 0
        self.totalGlobalPredictorMiss = 0
        self.totalLocalPredictorHit = 0
        self.totalLocalPredictorMiss = 0

        self.m = m # Looking at the last b branches
        self.n = n # how big should the n-bit counter be  

        self.branchPredictorSelectorBuffer = dict () # Assuming each entry can be 0 1 (Use Global History) 2 3 (User Local Predictor)

        self.branchLocalPredictionBuffer = dict() # Stores pairs of 1 (TAKEN) or 0 (NOT TAKEN)
        
        self.globalBranchHistory = [0] * self.m # Global history, Initial State all 0s
        self.globalBranchBuffer = dict () 

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
        
        
        branchInstructionAddress = BranchInstruction[22:32]

        # Determening which predictor to use (global or local predictor)
        currentPredictorSelector = self.selectPredictor(branchInstructionAddress)
        
        predictorUsed = "Global"
        predictor = 0 # Needs to be declared outside 
        if(currentPredictorSelector <= 1 ):
            predictorUsed = "Global"
            # Use Global Predictor
            # Global Branch History is used as the index to predictor table 
            predictor = self.globalPrediction(self.globalBranchHistory)
            self.totalGlobalPredictorUsed += 1
        else:
            predictorUsed = "Local"
            # Use Local Predictor
            predictor = self.localPrediction(branchInstructionAddress)
            self.totalLocalPredictorUsed += 1
        prediction = "NOT TAKEN"
        if(predictor <= 1):
            prediction = "NOT TAKEN"
        else:
            prediction = "TAKEN" 


        # Update Predictor Selector If Miss 
        # Update Branch History Register 

        # Calculating Prediction Accuracy                                                         
        self.totalPredictions += 1
        if(prediction==BranchOutcome):
            self.totalPredictionsHit += 1
        else:
            # Prediction was not correct 
            self.totalPredictionsMiss += 1

            if(predictorUsed == "Global"):
                globalHistoryString = ''.join(map(str, self.globalBranchHistory))

                oldState = self.globalBranchBuffer[globalHistoryString]
                newState = self.newState(oldState,BranchOutcome)
                
                self.globalBranchBuffer[globalHistoryString] = newState
                self.totalGlobalPredictorMiss += 1
            else:
                # Local Predictor was Used 
                oldState = self.branchLocalPredictionBuffer[branchInstructionAddress]
                newState = self.newState(oldState,BranchOutcome)
                self.branchLocalPredictionBuffer[branchInstructionAddress] = newState
                self.totalLocalPredictorMiss += 1
            # Update Prediction Selector 
            oldState = self.branchPredictorSelectorBuffer[branchInstructionAddress]
            
            # Since I want to use the same function 
            # Predictor was wrong therefore we need to use the other predictor (Through the 2 bit counter)
            fakeBranchOutcome = "NOT TAKEN" # Global Predictor Should have been used
            if (predictorUsed == "Global"): 
                fakeBranchOutcome = "TAKEN" # Local PredictorShould have been used Used
            newState = self.newState(oldState,fakeBranchOutcome)
            self.branchPredictorSelectorBuffer[branchInstructionAddress] = newState
            print("Predictor Old State",oldState, "NewState",newState)

        # Shifting the Global History Register 
        self.globalBranchHistory.pop(0)
        intOutcome = 0
        if(BranchOutcome=='TAKEN'):
            intOutcome = 1
        self.globalBranchHistory.append(intOutcome)

    def selectPredictor(self, BranchAddress):
        # We may need to edit which bits we use for indexing PredictorSelectionBuffer (Currently Using whole address)
        if(BranchAddress in self.branchPredictorSelectorBuffer):
            return self.branchPredictorSelectorBuffer[BranchAddress]
        else:
            self.branchPredictorSelectorBuffer[BranchAddress] = 0
            return 0
        
    def globalPrediction(self,globalHistory):

        globalHistoryString = ''.join(map(str, globalHistory))
        if( globalHistoryString in self.globalBranchBuffer):
            return self.globalBranchBuffer[globalHistoryString]
        else:
            self.globalBranchBuffer[globalHistoryString] = 0
            return 0 # Initial Prediction of NOT TAKEN 
        
    def localPrediction (self,BranchAddress):
        if(BranchAddress in self.branchLocalPredictionBuffer):
            return self.branchLocalPredictionBuffer[BranchAddress]
        else:
            self.branchLocalPredictionBuffer[BranchAddress] = 0
            return 0 # Initial Prediction of NOT TAKEN 
        
    def printStatistics(self):
        print("Dynamic Tournament Predictor Summary: ")
        print("Total Predictions:", self.totalPredictions)
        print("Total Predictions Hit:", self.totalPredictionsHit)
        print("Total Predictions Miss:", self.totalPredictionsMiss)
        print("Total Global Predictor Used: ", self.totalGlobalPredictorUsed)
        print("Total Global Predictor Miss: ", self.totalGlobalPredictorMiss)
        print("Total Local Predictor Used: ", self.totalLocalPredictorUsed)
        print("Total Local Predictor Miss: ", self.totalLocalPredictorMiss)
        print("Number of entries in Predictor Buffer", len(self.branchPredictorSelectorBuffer))
        print("Number of entries in GlobalPredictionBuffer", len(self.globalBranchBuffer))
        print("Number of entries in LocalPredictionBuffer", len(self.branchLocalPredictionBuffer))