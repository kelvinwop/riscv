import json
import seaborn as sns
import matplotlib.pyplot as plt
print("starting")

with open("output.txt", "r") as f:
    data = f.read()

class AlwaysPredictor:
    def __init__(self, state=1) -> None:
        self.state = state
        self.total = 0
        self.correct = 0
        self.accuracy = 0.5
        self.last_result = 0
    def feedline(self, line):
        self.total += 1
        if line[1] == "TAKEN":
            if self.state == 1:
                self.correct += 1
                self.last_result = 1
            else:
                self.last_result = 0
        if line[1] == "NOT TAKEN":
            if self.state == 0:
                self.correct += 1
                self.last_result = 1
            else:
                self.last_result = 0
        self.accuracy = float(self.correct) / float(self.total)
    def results(self):
        percentage = float(self.correct) / float(self.total) * 100.0
        return f"[ALWAYS {self.state} predictor] {self.correct=} out of {self.total=} ({percentage:02f}%)"

class NBitPredictor:
    def __init__(self, bits=1) -> None:
        self.state = 2**(bits-1)-1  # predict not taken
        self.total = 0
        self.correct = 0
        self.nottaken = 2**(bits-1)-1
        self.max = 2**bits - 1
        self.bits = bits
        self.accuracy = 0.5
        self.last_result = 0
    def feedline(self, line):
        self.total += 1
        if line[1] == "TAKEN":
            if self.state > self.nottaken:
                self.correct += 1
                self.last_result = 1
            else:
                self.last_result = 0
            self.state = min(self.state + 1, self.max)
        if line[1] == "NOT TAKEN":
            if self.state <= self.nottaken:
                self.correct += 1
                self.last_result = 1
            else:
                self.last_result = 0
            self.state = max(self.state - 1, 0)
        self.accuracy = float(self.correct) / float(self.total)
    def results(self):
        percentage = float(self.correct) / float(self.total) * 100.0
        return f"[{self.bits} predictor] {self.correct=} out of {self.total=} ({percentage:02f}%)"

class LocalAdapter:
    def __init__(self, pred_constr, a_constr, kw_constr) -> None:
        self.a_constr = a_constr
        self.kw_constr = kw_constr
        self.pred_constr = pred_constr
        self.branches = dict()
    def feedline(self, line):
        if line[2] not in self.branches:
            self.branches[line[2]] = self.pred_constr(*self.a_constr, **self.kw_constr)
        self.branches[line[2]].feedline(line)
    def results(self):
        total = 0
        correct = 0
        branches = 0
        for k,v in self.branches.items():
            branches += 1
            total += v.total
            correct += v.correct
        percentage = float(correct) / float(total) * 100.0
        return f"[local predictor ({branches} tracked)] {correct=} out of {total=} ({percentage:02f}%)"
    
class HybridAdapter:
    def __init__(self) -> None:
        self.global_correct = 0
        self.global_total = 0
        self.global_predictors = self.__setup_predictors()
        self.branches = dict()
    def __setup_predictors(self):
        preds = list()
        for i in range(1,10):
            preds.append(NBitPredictor(bits=i))
        preds.append(AlwaysPredictor(state=0))
        preds.append(AlwaysPredictor(state=1))
        return preds
    def __select_predictor(self, localpreds):
        maxacc = 0
        bestpred = None
        for pred in self.global_predictors:
            if pred.accuracy > maxacc:
                maxacc = pred.accuracy
                bestpred = pred
        for pred in localpreds:
            if pred.accuracy > maxacc:
                maxacc = pred.accuracy
                bestpred = pred
        return bestpred
    def __feed_predictors_line(self, preds, line):
        bestpred = self.__select_predictor(preds)
        for pred in preds:
            pred.feedline(line)
        for pred in self.global_predictors:
            pred.feedline(line)
        self.global_correct += bestpred.last_result
        self.global_total += 1
    def feedline(self, line):
        if line[2] not in self.branches:
            self.branches[line[2]] = self.__setup_predictors()
        self.__feed_predictors_line(self.branches[line[2]], line)
    def results(self):
        branches = 0
        for k,v in self.branches.items():
            branches += 1
        percentage = float(self.global_correct) / float(self.global_total) * 100.0
        return f"[HYBRID ({branches} tracked)] {self.global_correct=} out of {self.global_total=} ({percentage:02f}%)"

lines = data.split("\n")
preds = list()
for i in range(1,10):
    preds.append(LocalAdapter(NBitPredictor, [], {"bits":i}))
preds.append(LocalAdapter(AlwaysPredictor, [], {"state":0}))
preds.append(LocalAdapter(AlwaysPredictor, [], {"state":1}))
for i in range(1,10):
    preds.append(NBitPredictor(bits=i))
preds.append(AlwaysPredictor(state=0))
preds.append(AlwaysPredictor(state=1))
preds.append(HybridAdapter())

for line in lines:
    if line == "":
        continue
    obj = json.loads(line)
    for pred in preds:
        pred.feedline(obj)

for pred in preds:
    results = pred.results()
    print(results)