from river import feature_extraction
from river import stats
from river import compose
from river import linear_model
from river import metrics
from river import evaluate
from river import preprocessing
from river import optim
from pprint import pprint
from river import datasets

dataset = datasets.Bikes()

for x, y in dataset:
    pprint(x)
    print(f'Number of available bikes: {y}')
    break

model = compose.Select('clouds', 'humidity', 'pressure', 'temperature', 'wind')
model |= preprocessing.StandardScaler()
model |= linear_model.LinearRegression(optimizer=optim.SGD(0.00))

metric = metrics.MAE()

while True:
    evaluate.progressive_val_score(dataset, model, metric, print_every=5000)