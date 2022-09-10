import numpy as np


class Resource:
    def __init__(self, name="unknown resource"):
        self.name = name
        self.max = None

    def setMax(self, res_max):
        self.max = res_max


class Mode:
    def __init__(self, name="unknown mode"):
        self.name = name
        self.resource = None

    def setResource(self, res_array):
        self.resource = res_array


class Job:
    def __init__(self, name="unknown job"):
        self.name = name
        self.modes = []
        self.setup = None

    def addMode(self, mode):
        self.modes.append(mode)

    def setSetup(self, job):
        self.setup = job


class Precedence:
    def __init__(self, name="unknown constraint"):
        self.name = name
        self.jobs = None
        self.resource = None

    def setPrecedence(self, jobs):
        self.jobs = jobs

    def setImmediate(self, jobs, res):
        self.jobs = jobs
        self.resource = res


class Model:
    def __init__(self):
        self.resource = []
        self.job = []
        self.precedence = []

    def addResource(self, res):
        self.resource.append(res)

    def addJob(self, job):
        self.job.append(job)

    def addPrecedence(self, pre):
        self.job.append(pre)

    def optimize(self):
        print("optimized")
