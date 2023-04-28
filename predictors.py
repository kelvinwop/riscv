import json
import seaborn as sns
import matplotlib.pyplot as plt
from river import compose
from river import linear_model
from river import metrics
from river import preprocessing
print("starting")

with open("output.txt", "r") as f:
    data = f.read()

class RollingBuffer:
    def __init__(self, n=100):
        self.data = list()
        self.n = n
        self.i = 0
    def append(self, item):
        if len(self.data) < self.n:
            self.data.append(item)
        else:
            self.data[self.i] = item
        self.i = (self.i + 1) % self.n
    def get_ordered_list(self):
        ti = (self.i-1) % self.n
        output = list()
        for j in range(self.n):
            output.append(self.data[(ti-j)%self.n])
        return output

class RiverPredictor0:
    def __init__(self, model) -> None:
        self.mname = type(model)
        self.model = compose.Pipeline(
            preprocessing.StandardScaler(),
            model
        )
        self.total = 0
        self.correct = 0
        self.accuracy = 0.5
        self.last_result = 0
        self.acc_hist = RollingBuffer()
        self.state1 = NBitPredictor(bits=1)
        self.state2 = NBitPredictor(bits=2)
    def feedline(self, line):
        self.total += 1
        reg_values = json.loads(line[3])
        reg_values["state1"] = self.state1.state
        reg_values["state2"] = self.state2.state
        y_pred = self.model.predict_one(reg_values)
        if line[1] == "TAKEN":
            if y_pred >= 0.5:
                self.last_result = 1
            else:
                self.last_result = 0
        if line[1] == "NOT TAKEN":
            if y_pred < 0.5:
                self.last_result = 1
            else:
                self.last_result = 0
        self.correct += self.last_result
        self.acc_hist.append(self.last_result)
        # self.accuracy = float(self.correct) / float(self.total)
        self.accuracy = float(sum(self.acc_hist.data)) / 100.0
        self.model = self.model.learn_one(reg_values, int(line[1]=="TAKEN"))

        self.state1.feedline(line)
        self.state2.feedline(line)
    def results(self):
        if self.total == 0:
            percentage = 100.0
        else:
            percentage = float(self.correct) / float(self.total) * 100.0
        return f"[River predictor {self.mname}] {self.correct=} out of {self.total=} ({percentage:02f}%)"

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
        if self.total == 0:
            percentage = 100.0
        else:
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
        if self.total == 0:
            percentage = 100.0
        else:
            percentage = float(self.correct) / float(self.total) * 100.0
        return f"[{self.bits} predictor] {self.correct=} out of {self.total=} ({percentage:02f}%)"

class GShareAdapter:
    def __init__(self, pred_constr, a_constr=list(), kw_constr=dict(), bits=10, name="") -> None:
        self.name = name
        self.bits = bits
        self.a_constr = a_constr
        self.kw_constr = kw_constr
        self.pred_constr = pred_constr
        self.branches = dict()
        self.global_history = RollingBuffer(n=bits)
        for i in range(bits):
            self.global_history.append(0)

    def list_to_int10(self, listthing):
        output = 0
        j = 1
        for i in range(self.bits):
            output += listthing[i] * j
            j *= 2
        return output
    def feedline(self, line):
        pred_id = self.list_to_int10(self.global_history.get_ordered_list()) ^ (int(line[2], 16) & 2**self.bits-1)
        if pred_id not in self.branches:
            self.branches[pred_id] = self.pred_constr(*self.a_constr, **self.kw_constr)
        self.branches[pred_id].feedline(line)
        self.global_history.append(int(line[1]=="TAKEN"))
    def results(self):
        total = 0
        correct = 0
        branches = 0
        for k,v in self.branches.items():
            branches += 1
            total += v.total
            correct += v.correct
        if total == 0:
            percentage = 100.0
        else:
            percentage = float(correct) / float(total) * 100.0
        return f"[GShare {self.bits}-bit {self.name} ({branches} tracked)] {correct=} out of {total=} ({percentage:02f}%)"
    
class GlobalNotCorrelatingAdapter:
    def __init__(self, pred_constr, a_constr=list(), kw_constr=dict(), bits=10, name="") -> None:
        self.name = name
        self.bits = bits
        self.a_constr = a_constr
        self.kw_constr = kw_constr
        self.pred_constr = pred_constr
        self.branches = dict()
        self.global_history = RollingBuffer(n=bits)
        for i in range(bits):
            self.global_history.append(0)

    def list_to_int10(self, listthing):
        output = 0
        j = 1
        for i in range(self.bits):
            output += listthing[i] * j
            j *= 2
        return output
    def feedline(self, line):
        pred_id = self.list_to_int10(self.global_history.get_ordered_list())
        if pred_id not in self.branches:
            self.branches[pred_id] = self.pred_constr(*self.a_constr, **self.kw_constr)
        self.branches[pred_id].feedline(line)
        self.global_history.append(int(line[1]=="TAKEN"))
    def results(self):
        total = 0
        correct = 0
        branches = 0
        for k,v in self.branches.items():
            branches += 1
            total += v.total
            correct += v.correct
        if total == 0:
            percentage = 100.0
        else:
            percentage = float(correct) / float(total) * 100.0
        return f"[GlobalNotCorrelatingAdapter {self.bits}-bit {self.name} ({branches} tracked)] {correct=} out of {total=} ({percentage:02f}%)"
    
class CorrelatingAdapter:
    def __init__(self, pred_constr, a_constr=list(), kw_constr=dict(), bits=10, name="") -> None:
        self.name = name
        self.bits = bits
        self.a_constr = a_constr
        self.kw_constr = kw_constr
        self.pred_constr = pred_constr
        self.branches = dict()
        self.global_history = RollingBuffer(n=bits)
        for i in range(bits):
            self.global_history.append(0)

    def list_to_int10(self, listthing):
        output = 0
        j = 1
        for i in range(self.bits):
            output += listthing[i] * j
            j *= 2
        return output
    def feedline(self, line):
        pred_id = self.list_to_int10(self.global_history.get_ordered_list()) << self.bits + (int(line[2], 16) & 2**self.bits-1)
        if pred_id not in self.branches:
            self.branches[pred_id] = self.pred_constr(*self.a_constr, **self.kw_constr)
        self.branches[pred_id].feedline(line)
        self.global_history.append(int(line[1]=="TAKEN"))
    def results(self):
        total = 0
        correct = 0
        branches = 0
        for k,v in self.branches.items():
            branches += 1
            total += v.total
            correct += v.correct
        if total == 0:
            percentage = 100.0
        else:
            percentage = float(correct) / float(total) * 100.0
        return f"[CorrelatingAdapter {self.bits}-bit {self.name} ({branches} tracked)] {correct=} out of {total=} ({percentage:02f}%)"

class LocalAdapter:
    def __init__(self, pred_constr, a_constr=list(), kw_constr=dict(), name="") -> None:
        self.name = name
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
        if total == 0:
            percentage = 100.0
        else:
            percentage = float(correct) / float(total) * 100.0
        return f"[local predictor {self.name} ({branches} tracked)] {correct=} out of {total=} ({percentage:02f}%)"
    
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
        if self.global_total == 0:
            percentage = 100.0
        else:
            percentage = float(self.global_correct) / float(self.global_total) * 100.0
        return f"[HYBRID ({branches} tracked)] {self.global_correct=} out of {self.global_total=} ({percentage:02f}%)"

lines = data.split("\n")
preds = list()
for i in range(1,10):
    preds.append(LocalAdapter(NBitPredictor, [], {"bits":i}))
preds.append(LocalAdapter(AlwaysPredictor, [], {"state":0}, "AlwaysBranch"))
preds.append(LocalAdapter(AlwaysPredictor, [], {"state":1}, "NeverBranch"))
preds.append(LocalAdapter(RiverPredictor0, [], {"model":linear_model.LogisticRegression()}, "LogisticRegression"))
preds.append(LocalAdapter(RiverPredictor0, [], {"model":linear_model.PAClassifier(C=0.01, mode=1)}, "PassiveAggressive"))
preds.append(LocalAdapter(RiverPredictor0, [], {"model":linear_model.Perceptron()}, "Perceptron"))
preds.append(LocalAdapter(RiverPredictor0, [], {"model":linear_model.ALMAClassifier()}, "ALMA"))
preds.append(LocalAdapter(RiverPredictor0, [], {"model":linear_model.LinearRegression(intercept_lr=.1)}, "LinearRegression"))
for i in range(1,10):
    preds.append(NBitPredictor(bits=i))
preds.append(AlwaysPredictor(state=0))
preds.append(AlwaysPredictor(state=1))
preds.append(HybridAdapter())
preds.append(RiverPredictor0(model=linear_model.LogisticRegression()))
preds.append(RiverPredictor0(model=linear_model.PAClassifier(C=0.01, mode=1)))
preds.append(RiverPredictor0(model=linear_model.Perceptron()))
preds.append(RiverPredictor0(model=linear_model.ALMAClassifier()))
preds.append(RiverPredictor0(model=linear_model.LinearRegression(intercept_lr=.1)))
preds.append(GShareAdapter(NBitPredictor, [], {"bits":2}, name="2bp"))
preds.append(GShareAdapter(NBitPredictor, [], {"bits":2}, bits=16, name="2bp"))
preds.append(GShareAdapter(NBitPredictor, [], {"bits":1}, name="1bp"))
preds.append(GShareAdapter(NBitPredictor, [], {"bits":1}, bits=16, name="1bp"))
preds.append(GlobalNotCorrelatingAdapter(NBitPredictor, [], {"bits":1}, bits=10, name="1bp"))
preds.append(GlobalNotCorrelatingAdapter(NBitPredictor, [], {"bits":2}, bits=10, name="2bp"))
preds.append(CorrelatingAdapter(NBitPredictor, [], {"bits":1}, bits=10, name="1bp"))
preds.append(CorrelatingAdapter(NBitPredictor, [], {"bits":2}, bits=10, name="2bp"))
preds.append(CorrelatingAdapter(NBitPredictor, [], {"bits":1}, bits=5, name="1bp"))
preds.append(CorrelatingAdapter(NBitPredictor, [], {"bits":2}, bits=5, name="2bp"))

for line in lines:
    if line == "":
        continue
    obj = json.loads(line)
    for pred in preds:
        pred.feedline(obj)

for pred in preds:
    results = pred.results()
    print(results)