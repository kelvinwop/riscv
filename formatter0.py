with open("input.txt", "r") as f:
    data = f.read()

datalines = data.split("\n")

output = ""
for line in datalines:
    line = line.replace("self.", "")
    line = line.replace("out of ", "")
    name, ex = line.split("correct=")
    correct, ex = ex.split("total=")
    total, ex = ex.split(" (")
    pct = ex[:-1]

    name = name.strip()
    correct = correct.strip()
    total = total.strip()
    pct = pct.strip()
    output += f"{name},{correct},{total},{pct}\n"

with open("output.csv", "w+") as f:
    f.write(output)