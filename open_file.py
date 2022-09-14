import csv
import time
from main import *

file = "data.csv"

with open(file, encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",")
    ls = [row for row in reader]
    model = Model(int(ls[0][0]))
    max_trial = int(ls[1][0])
    tabu_length = int(ls[2][0])

    flag = 0

    for lll in ls:
        if not lll:
            flag = ls.index(lll)
            break

    ls = list(ls[flag + 1:])
    for lll in ls:
        if not lll:
            flag = ls.index(lll)
            break
        resource = Resource(lll[0])
        resource.setMax([int(i) for i in lll[1:]])
        model.addResource(resource)

    ls = list(ls[flag + 1:])
    for lll in ls:
        if not lll:
            flag = ls.index(lll)
            break
        job_name = lll[0]
        if job_name not in model.job_list:
            job = Job(job_name)
            model.addJob(job)
        mode = Mode(lll[1])
        mode.setDuration(int(lll[3]))
        for re in range(4, len(lll) - 2, 2):
            if lll[re]:
                mode.addResource(lll[re], int(lll[re + 1]))
        model.addMode(job_name, mode)
        if lll[2]:
            model.setSetupMode(job_name, lll[2], [mode.name])

    ls = list(ls[flag + 1:])
    for lll in ls:
        if int(lll[0]):
            model.addImmediatePrecedence(lll[1], lll[2], lll[3])
        else:
            model.addPrecedence(lll[1], lll[2])

model.optimize(max_trial, tabu_length, time.time())
