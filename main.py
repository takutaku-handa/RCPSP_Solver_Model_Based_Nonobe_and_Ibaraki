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
        self.duration = None

    def addResource(self, name: str, amount: np.array):
        if name not in self.resource.keys():
            self.resource[name] = amount

    def setDuration(self, duration: int):
        self.duration = duration


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
        t_bar = 0
        remain_resource = {}
        immediate_consts = {}
        for rs_key, rs_value in self.resource.items():
            remain_resource[rs_key] = rs_value.max
            immediate_consts[rs_key] = [imm[0: 2] for imm in self.immediate if imm[2] == rs_key]

        step4_flag = False

        while i < len(job_list):
            now_job = job_list[i]
            now_mode = mode_list[i]
            precedence = [pre[0] for pre in self.precedence if pre[1] == now_job and pre[0] in completion_time.keys()]
            immediate = [imm[0] for imm in self.immediate if imm[1] == now_job and imm[0] in completion_time.keys()]
            all_precedence = [pre for pre in self.precedence if pre[0] in completion_time.keys()]
            all_immediate = [imm for imm in self.immediate if imm[0] in completion_time.keys()]
            for all_imm in all_immediate:
                all_precedence.append(all_imm[0: 2])

            if step4_flag:
                v = [value for key, value in completion_time.items() if key in precedence or key in immediate]
                if v:
                    t_bar = max(v)
                else:
                    t_bar = 0
            step4_flag = False

            T = 0
            solved = False
            pmj = self.job[now_job].modes[now_mode].duration

            for res_name in self.res_by_job[now_job]:
                limit_immediate_upper = 0
                limit_immediate_lower = "inf"

                usage = self.job[now_job].modes[now_mode].resource[res_name]

                for imm in immediate_consts[res_name]:
                    if imm[0] in completion_time.keys():
                        if limit_immediate_lower == "inf":
                            limit_immediate_lower = completion_time[imm[0]] - 1
                        else:
                            limit_immediate_lower = min(limit_immediate_lower, completion_time[imm[0]] - 1)
                    if imm[1] in start_time.keys():
                        limit_immediate_upper = max(limit_immediate_upper, start_time[imm[1]])

                if limit_immediate_lower == "inf":
                    limit_immediate_lower = -1

                if t_bar <= limit_immediate_lower:
                    t_list = list(range(t_bar, limit_immediate_lower + 1)) + list(range(limit_immediate_upper, max_t))
                else:
                    t_list = list(range(max(t_bar, limit_immediate_upper), max_t))

                for t in t_list:
                    after = remain_resource[res_name][t: t + pmj] - usage
                    if np.all(after >= 0):
                        T = max(T, t)
                        solved = True
                        break
                if not solved:
                    return "failure"

            for res_name in self.res_by_job[now_job]:
                usage = self.job[now_job].modes[now_mode].resource[res_name]
                after = remain_resource[res_name][T: T + pmj] - usage
                remain_resource[res_name][T: T + pmj] = after
                start_time[now_job] = T
                completion_time[now_job] = T + pmj

            back_tracking_flag = False
            for imm in all_immediate:
                if imm[1] == now_job:
                    for j_dash in self.job_by_res[imm[2]]:
                        if imm[0] != j_dash and imm[0] in completion_time.keys() and j_dash in start_time.keys():
                            if completion_time[imm[0]] <= start_time[j_dash] < T:
                                back_tracking_flag = True
                                if [imm[0], j_dash] in all_precedence:
                                    i = job_list.index(j_dash)
                                    t_bar = T
                                    index = job_list.index(j_dash)
                                else:
                                    i = job_list.index(imm[0])
                                    imm_0_mode_name = mode_list[job_list.index(imm[0])]
                                    dur = self.job[imm[0]].modes[imm_0_mode_name].duration
                                    t_bar = start_time[j_dash] + 1 - dur
                                    index = job_list.index(imm[0])

                                rest_jobs = job_list[index:]
                                rest_modes = mode_list[index:]
                                for rest_j, rest_m in zip(rest_jobs, rest_modes):
                                    if rest_j in start_time.keys():
                                        for res_name in self.res_by_job[rest_j]:
                                            usage = self.job[rest_j].modes[rest_m].resource[res_name]
                                            start_rest = start_time[rest_j]
                                            rest_dur = self.job[rest_j].modes[rest_m].duration
                                            after = remain_resource[res_name][start_rest: start_rest + rest_dur] + usage
                                            remain_resource[res_name][start_rest: start_rest + rest_dur] = after
                                        del start_time[rest_j]
                                        del completion_time[rest_j]
                                break
                    else:
                        continue
                    break

            if not back_tracking_flag:
                start_time[now_job] = T
                completion_time[now_job] = T + pmj
                i += 1
                step4_flag = True

        return start_time
