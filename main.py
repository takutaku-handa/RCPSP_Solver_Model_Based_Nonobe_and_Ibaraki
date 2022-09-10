import numpy as np


class Resource:
    def __init__(self, name="unknown resource"):
        self.name = name
        self.max = None

    def setMax(self, res_max: np.array):
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
        self.job_by_res = {}
        self.res_by_job = {}
        self.precedence = []
        self.immediate = []

    def addResource(self, res: Resource):
        if res.name not in self.resource.keys():
            self.resource[res.name] = res
            self.job_by_res[res.name] = []
        else:
            print(f"同じ名前の資源({res.name})が存在します")
            return

    def addJob(self, job: Job):
        if job.name not in self.job.keys():
            self.job[job.name] = job
            self.res_by_job[job.name] = []
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
            for res in mode.resource.keys():
                jbr = self.job_by_res[res]
                jbr.append(job_name)
                rbj = self.res_by_job[job_name]
                rbj.append(res)


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

    # 必要なもの
    # ペナルティ値の計算 (m, s) → 数値
    # 近傍の計算 (m, π) → [(m, π), ...]
    # CONSTRUCT処理 (m, π) → (m, s)

    def CONSTRUCT(self, job_list: list[str], mode_list: list[str], max_t: int):
        completion_time = {}
        start_time = {}
        i = 0
        remain_resource = {}
        immediate_consts = {}
        for rs_key, rs_value in self.resource.items():
            remain_resource[rs_key] = rs_value.max
            immediate_consts[rs_key] = [imm[0: 2] for imm in self.immediate if imm[2] == rs_key]

        while i >= len(job_list):
            job = job_list[i]
            mode = mode_list[i]
            precedence = [pre for pre in self.precedence if pre[1] == job and pre[1] in completion_time.keys()]
            immediate = [imm for imm in self.immediate if imm[1] == job and imm[1] in completion_time.keys()]
            t_bar = max([0] + [value for key, value in completion_time.items()
                               if key in precedence or key in immediate])
            T = 0
            solved = False
            pmj = 0

            for res_name in self.res_by_job[job]:
                limit_immediate_upper = 0
                limit_immediate_lower = "inf"

                usage = self.job[job].modes[mode].resource[res_name]
                length = len(usage)
                pmj = max(pmj, length)

                for imm in immediate_consts[res_name]:
                    if limit_immediate_lower == "inf":
                        limit_immediate_lower = completion_time[imm[0]] - 1
                    else:
                        limit_immediate_lower = min(limit_immediate_lower, completion_time[imm[0]] - 1)
                    limit_immediate_upper = max(limit_immediate_upper, start_time[imm[1]])

                if t_bar <= limit_immediate_lower:
                    t_list = list(range(t_bar, limit_immediate_lower + 1)) + list(range(limit_immediate_upper, max_t))
                else:
                    t_list = list(range(limit_immediate_upper, max_t))
                for t in t_list:
                    after = remain_resource[res_name][t: t + length] - usage
                    if np.all(after >= 0):
                        T = t
                        solved = True
                        break
                if not solved:
                    return "failure"

            for imm in immediate:
                for j_dash in self.job_by_res[imm[2]]:
                    if completion_time[imm[0]] <= start_time[j_dash] < T:
                        if [imm, j_dash] in precedence:
                            i = job_list.index(j_dash)
                            t_bar = T
                        else:
                            i = job_list.index(imm)
                            t_bar = start_time[j_dash] + 1 - pmj
                        return
                    else:
                        start_time[job] = T
                        completion_time[job] = T + pmj
                        i += 1

        return start_time
