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
        self.resource = {}

    def addResource(self, name: str, amount: np.array):
        if name not in self.resource.keys():
            self.resource[name] = amount


class Job:
    def __init__(self, name="unknown job"):
        self.name = name
        self.modes = {}
        self.setups = {}


class Model:
    def __init__(self):
        self.resource = {}
        self.job = {}
        self.precedence = []
        self.immediate = []

    def addResource(self, res: Resource):
        if res.name not in self.resource.keys():
            self.resource[res.name] = res
        else:
            print(f"同じ名前の資源({res.name})が存在します")
            return

    def addJob(self, job: Job):
        if job.name not in self.job.keys():
            self.job[job.name] = job
        else:
            print(f"同じ名前のジョブ({job.name})が存在します")
            return

    def addMode(self, job_name: str, mode: Mode):
        job = self.job[job_name]
        if mode.name not in job.modes.keys():
            for res in mode.resource:
                if res not in self.resource.keys():
                    print(f"モード({mode.name}に含まれる({res})という資源は、このモデルに存在しません")
                    return
            job.modes[mode.name] = mode
        else:
            print(f"同じ名前のモード({mode.name})が存在します")
            return

    def setSetupMode(self, job_name: str, predecessor_name, mode_list: list[str]):
        job = self.job[job_name]
        for md in mode_list:
            if md not in job.modes.keys():
                print(f"ジョブ({job_name})に{md}というモードは存在しません")
                return
        job.setups[predecessor_name] = mode_list

    def addPrecedence(self, job1, job2):
        if job1 in self.job.keys() and job2 in self.job.keys():
            self.precedence.append([job1, job2])
        else:
            print(f"{[job1, job2]}に一致するジョブは、このモデルに存在しません")
            return

    def addImmediatePrecedence(self, job1, job2, res: str):
        if job1 in self.job.keys() and job2 in self.job.keys():
            if res in self.resource:
                self.immediate.append([job1, job2, res])
            else:
                print(f"{res}という資源は、このモデルに存在しません")
                return
        else:
            print(f"{[job1, job2]}に一致するジョブは、このモデルに存在しません")
            return
