import random


class Resource:
    def __init__(self, name="unknown resource"):
        self.name = name
        self.max = None

    def setMax(self, res_max: list):
        self.max = res_max


class Mode:
    def __init__(self, name="unknown mode"):
        self.name = name
        self.resource = {}
        self.duration = None

    def addResource(self, name: str, amount: int):
        if name not in self.resource.keys():
            self.resource[name] = amount

    def setDuration(self, duration: int):
        self.duration = duration


class Job:
    def __init__(self, name="unknown job"):
        self.name = name
        self.mode = {}
        self.mode_list = []
        self.setups = {}


def all_path_from_g_arcs(g_arcs):
    arc_0 = [arc[0] for arc in g_arcs]
    arc_1 = [arc[1] for arc in g_arcs]
    to_go_dict = {}
    for arc in g_arcs:
        if arc[0] not in to_go_dict.keys():
            to_go_dict[arc[0]] = [arc[1]]
        elif arc[1] not in to_go_dict[arc[0]]:
            tgd = to_go_dict[arc[0]]
            tgd.append(arc[1])
            to_go_dict[arc[0]] = tgd
    start = list(set(arc_0) - (set(arc_0) & set(arc_1)))
    path = [[i] for i in start]
    flag = True
    while flag:
        flag = False
        tmp_paths = []
        for pt in path:
            target = pt[-1]
            if target in to_go_dict.keys():
                flag = True
                for to_go in to_go_dict[target]:
                    if to_go not in pt:
                        to_add = list(pt)
                        to_add.append(to_go)
                        tmp_paths.append(to_add)
        if flag:
            path = tmp_paths
        else:
            break
    return path


def simple_directed_path(job_name, all_path):
    candidate = []
    for path in all_path:
        if job_name in path:
            candidate.append(path)
    path_length = [len(i) for i in candidate]
    max_length = max(path_length)
    max_length_index = path_length.index(max_length)
    return candidate[max_length_index]


def PENALTY_for_minimize_makespan(completion_time: dict):
    return completion_time["sink"]


class Model:
    def __init__(self):
        self.max_t = None
        self.max_trial = None
        self.tabu_length = None
        self.resource = {}
        self.job = {}
        self.job_list = []
        self.job_by_res = {}
        self.res_by_job = {}
        self.precedence = []
        self.immediate = []
        self.precedence_arcs = []
        self.jobs_to_come = {}
        self.jobs_to_go = {}
        self.strongly_connected_components = []
        self.all_precedence = []

    def setMax_t(self, max_t: int):
        self.max_t = max_t

    def setMax_trial(self, max_trial: int):
        self.max_trial = max_trial

    def setTabu_length(self, tabu_length: int):
        self.tabu_length = tabu_length

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
            self.job_list.append(job.name)
            self.jobs_to_come[job.name] = [job.name]
            self.jobs_to_go[job.name] = [job.name]
        else:
            print(f"同じ名前のジョブ({job.name})が存在します")
            return

    def addMode(self, job_name: str, mode: Mode):
        job = self.job[job_name]
        if mode.name not in job.mode.keys():
            for res in mode.resource:
                if res not in self.resource.keys():
                    print(f"モード({mode.name}に含まれる({res})という資源は、このモデルに存在しません")
                    return
            job.mode[mode.name] = mode
            job.mode_list.append(mode.name)
            for res in mode.resource.keys():
                jbr = self.job_by_res[res]
                jbr.append(job_name)
                rbj = self.res_by_job[job_name]
                rbj.append(res)

        else:
            print(f"同じ名前のモード({mode.name})が存在します")
            return

    def addResource_to_Mode(self, job_name: str, mode_name: str, resource_name: str, amount: int):
        job = self.job[job_name]
        if mode_name in job.mode.keys():
            if resource_name not in self.resource.keys():
                print(f"モード({mode_name}に含まれる({resource_name})という資源は、このモデルに存在しません")
                return
            mode = job.mode[mode_name]
            if resource_name not in mode.resource.keys():
                mode.resource[resource_name] = amount
                jbr = self.job_by_res[resource_name]
                jbr.append(job_name)
                rbj = self.res_by_job[job_name]
                rbj.append(resource_name)

    def setSetupMode(self, job_name: str, predecessor_name, mode_list: list[str]):
        job = self.job[job_name]
        for md in mode_list:
            if md not in job.mode.keys():
                print(f"ジョブ({job_name})に{md}というモードは存在しません")
                return
        job.setups[predecessor_name] = mode_list

    def addPrecedenceArc(self, job1, job2):
        jc2 = self.jobs_to_come[job2]
        if job1 not in jc2:
            jc2.append(job1)
        jg1 = self.jobs_to_go[job1]
        if job2 not in jg1:
            jg1.append(job2)
        for come_to_job1 in self.jobs_to_come[job1]:
            for go_from_job2 in self.jobs_to_go[job2]:
                if (come_to_job1, go_from_job2) not in self.precedence_arcs and come_to_job1 != go_from_job2:
                    j2c_from_job2 = self.jobs_to_come[go_from_job2]
                    j2g_from_job1 = self.jobs_to_go[come_to_job1]
                    if come_to_job1 not in j2c_from_job2:
                        j2c_from_job2.append(come_to_job1)
                    if go_from_job2 not in j2g_from_job1:
                        j2g_from_job1.append(go_from_job2)

                    if (go_from_job2, come_to_job1) not in self.precedence_arcs:
                        self.precedence_arcs.append((come_to_job1, go_from_job2))
                    else:
                        for scc in self.strongly_connected_components:
                            if come_to_job1 in scc:
                                if go_from_job2 in scc:
                                    pass
                                else:
                                    scc.append(go_from_job2)
                                break
                            elif go_from_job2 in scc:
                                scc.append(come_to_job1)
                                break
                        else:
                            self.strongly_connected_components.append([come_to_job1, go_from_job2])

    def addPrecedence(self, job1, job2):
        if job1 in self.job.keys() and job2 in self.job.keys():
            self.precedence.append((job1, job2))
            self.all_precedence.append((job1, job2))
            self.addPrecedenceArc(job1, job2)
        else:
            print(f"{[job1, job2]}に一致するジョブは、このモデルに存在しません")
            return

    def addImmediatePrecedence(self, job1, job2, res: str):
        if job1 in self.job.keys() and job2 in self.job.keys():
            if res in self.resource:
                self.immediate.append((job1, job2, res))
                self.all_precedence.append((job1, job2))
                self.addPrecedenceArc(job1, job2)
                self.addPrecedenceArc(job2, job1)
            else:
                print(f"{res}という資源は、このモデルに存在しません")
                return
        else:
            print(f"{[job1, job2]}に一致するジョブは、このモデルに存在しません")
            return

    def __defAllPrecedence(self):
        for scc in self.strongly_connected_components:
            for job_in_scc in scc:
                for pre in self.all_precedence:
                    if job_in_scc == pre[0]:
                        for rest_of_scc in scc:
                            new_pre = (rest_of_scc, pre[1])
                            if pre[1] not in scc and new_pre not in self.all_precedence:
                                self.all_precedence.append(new_pre)
                    elif job_in_scc == pre[1]:
                        for rest_of_scc in scc:
                            new_pre = (pre[0], rest_of_scc)
                            if pre[0] not in scc and new_pre not in self.all_precedence:
                                self.all_precedence.append((pre[0], rest_of_scc))

    def __shiftBEFORE(self, job_list, job1, job2):
        index_1 = job_list.index(job1)
        index_2 = job_list.index(job2)

        if index_1 < index_2 and (job1, job2) not in self.all_precedence:
            u1 = [job1]
            u2 = [job2]
            for scc in self.strongly_connected_components:
                if job1 in scc:
                    u1 = scc
                if job2 in scc:
                    u2 = scc
            u1_index = [job_list.index(j1) for j1 in u1]
            u2_index = [job_list.index(j2) for j2 in u2]
            if u1 == u2:
                new_job_list = job_list[:index_1 + 1]
                save_list = []
                for jb in job_list[index_1 + 1: index_2]:
                    if (jb, job2) in self.precedence or (jb, job2) in self.precedence:
                        new_job_list.append(jb)
                    else:
                        save_list.append(jb)
                new_job_list.extend(save_list)
                new_job_list.extend(job_list[index_2:])
            else:
                new_job_list = job_list[: min(u1_index)]
                save_list = []
                for jb in job_list[max(u1_index) + 1: min(u2_index)]:
                    if (jb, job2) in self.all_precedence:
                        new_job_list.append(jb)
                    else:
                        save_list.append(jb)

                new_job_list.extend(job_list[min(u2_index): max(u2_index) + 1])
                new_job_list.extend(job_list[min(u1_index): max(u1_index) + 1])
                new_job_list.extend(save_list)
                new_job_list.extend(job_list[max(u2_index) + 1:])
            return new_job_list

        else:
            return []

    def __CONSTRUCT(self, job_list: list[str], mode_dict: dict):
        completion_time = {}
        start_time = {}
        i = 0
        t_bar = 0
        remain_resource = {}
        resource_user = {}
        immediate_consts = {}
        for rs_key, rs_value in self.resource.items():
            remain_resource[rs_key] = list(rs_value.max)  # ここをlist()にしないと、remain_resourceとselfが連動してしまう。
            resource_user[rs_key] = [[] for i in rs_value.max]
            immediate_consts[rs_key] = [imm[0: 2] for imm in self.immediate if imm[2] == rs_key]

        G_PRI_arcs = []
        G_B_arcs = []

        step4_flag = False

        while i < len(job_list):
            now_job = job_list[i]
            if now_job == "sink":
                sink = max([value for value in completion_time.values()])
                start_time["sink"] = sink
                completion_time["sink"] = sink
                break

            now_mode = mode_dict[now_job]
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
            pmj = self.job[now_job].mode[now_mode].duration

            max_limit_immediate_upper = 0
            immediate_upper_job = None

            for res_name in self.res_by_job[now_job]:
                limit_immediate_upper = 0
                limit_immediate_lower = "inf"

                usage = self.job[now_job].mode[now_mode].resource[res_name]

                for imm in immediate_consts[res_name]:
                    if imm[0] in completion_time.keys():
                        if limit_immediate_lower == "inf":
                            limit_immediate_lower = completion_time[imm[0]] - 1
                        else:
                            limit_immediate_lower = min(limit_immediate_lower, completion_time[imm[0]] - 1)
                    if imm[1] in start_time.keys():
                        limit_immediate_upper = max(limit_immediate_upper, start_time[imm[1]])
                        if limit_immediate_upper > max_limit_immediate_upper:
                            max_limit_immediate_upper = limit_immediate_upper
                            immediate_upper_job = imm[1]

                if limit_immediate_lower == "inf":
                    limit_immediate_lower = -1

                if t_bar <= limit_immediate_lower:
                    t_list = list(range(t_bar, limit_immediate_lower + 1)) + list(
                        range(limit_immediate_upper, self.max_t))
                else:
                    t_list = list(range(max(t_bar, limit_immediate_upper), self.max_t))

                for t in t_list:
                    after = [rere - usage for rere in list(remain_resource[res_name][t: t + pmj])]
                    bool_after = [True if aft >= 0 else False for aft in after]
                    if all(bool_after):
                        T = max(T, t)
                        solved = True
                        break
                    else:
                        for time in range(len(after)):
                            if after[time] < 0:
                                user = resource_user[res_name][t + time]
                                for us in user:
                                    if (us, now_job) not in G_PRI_arcs:
                                        G_PRI_arcs.append((us, now_job))
                if solved:
                    if T == max_limit_immediate_upper and immediate_upper_job:
                        G_PRI_arcs.append((immediate_upper_job, now_job))
                else:
                    return "failure", "failure", "failure"

            for res_name in self.res_by_job[now_job]:
                usage = self.job[now_job].mode[now_mode].resource[res_name]
                after = [rere - usage for rere in list(remain_resource[res_name][T: T + pmj])]
                remain_resource[res_name][T: T + pmj] = after
                for time in range(T, T + pmj):
                    resource_user[res_name][time].append(now_job)
                start_time[now_job] = T
                completion_time[now_job] = T + pmj

            back_tracking_flag = False
            for imm in all_immediate:
                if imm[1] == now_job:
                    for j_dash in self.job_by_res[imm[2]]:
                        if imm[0] != j_dash and imm[0] in completion_time.keys() and j_dash in start_time.keys():
                            if completion_time[imm[0]] <= start_time[j_dash] < T:
                                back_tracking_flag = True
                                if (imm[0], j_dash) in all_precedence:
                                    i = job_list.index(j_dash)
                                    t_bar = T
                                    index = job_list.index(j_dash)
                                    G_B_arcs.append((now_job, j_dash))
                                else:
                                    i = job_list.index(imm[0])
                                    imm_0_mode_name = mode_dict[imm[0]]
                                    dur = self.job[imm[0]].mode[imm_0_mode_name].duration
                                    t_bar = start_time[j_dash] + 1 - dur
                                    index = job_list.index(imm[0])
                                    G_B_arcs.append((j_dash, imm[0]))
                                rest_jobs = job_list[index:]
                                rest_modes = [mode_dict[rj] for rj in rest_jobs]
                                for rest_j, rest_m in zip(rest_jobs, rest_modes):
                                    if rest_j in start_time.keys():
                                        for res_name in self.res_by_job[rest_j]:
                                            usage = self.job[rest_j].mode[rest_m].resource[res_name]
                                            start_rest = start_time[rest_j]
                                            rest_dur = self.job[rest_j].mode[rest_m].duration
                                            after = [rere + usage for rere in
                                                     list(remain_resource[res_name][start_rest: start_rest + rest_dur])]
                                            remain_resource[res_name][start_rest: start_rest + rest_dur] = after
                                            for time in range(start_rest, start_rest + rest_dur):
                                                resource_user[res_name][time].remove(rest_j)
                                            for arc in G_PRI_arcs:
                                                if rest_j in arc:
                                                    G_PRI_arcs.remove(arc)
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

        for prd in self.precedence:
            if completion_time[prd[0]] == start_time[prd[1]]:
                G_PRI_arcs.append((prd[0], prd[1]))
        for imd in self.immediate:
            if completion_time[imd[0]] == start_time[imd[1]]:
                G_PRI_arcs.append((imd[0], imd[1]))

        G_arcs = list(set(G_PRI_arcs) | set(G_B_arcs))

        return start_time, completion_time, G_arcs

    def __MOVE_for_minimize_makespan(self, job_list, mode_dict, g_arcs, tabu_list):
        ret_job_list = []
        ret_mode_dict = mode_dict
        ret_g_arcs = None
        ret_penalty = "inf"
        ret_attribute = "shift"
        ret_job = None

        all_path = all_path_from_g_arcs(g_arcs)
        sdp = simple_directed_path("sink", all_path)
        path = sdp[0: -1]

        for i in range(len(path) - 1):
            if ("shift", path[i + 1]) not in tabu_list:
                new_job_list = self.__shiftBEFORE(job_list, path[i], path[i + 1])
                if new_job_list:
                    s, c, g = self.__CONSTRUCT(new_job_list, mode_dict)
                    if s != "failure":
                        p = PENALTY_for_minimize_makespan(c)
                        if ret_penalty == "inf":
                            ret_penalty = p
                            ret_job_list = new_job_list
                            ret_job = path[i + 1]
                            ret_g_arcs = g
                        elif p < ret_penalty:
                            ret_penalty = p
                            ret_job_list = new_job_list
                            ret_job = path[i + 1]
                            ret_g_arcs = g
        return ret_job_list, ret_mode_dict, ret_penalty, ret_g_arcs, (ret_attribute, ret_job)

    def __initial_job_list(self, rand: int):
        ret = []
        job_list = list(self.job_list)
        all_precedence = list(self.all_precedence)
        strongly_connected_components = list(self.strongly_connected_components)
        while set(ret) != set(job_list):
            list_origin = list(set(job_list) - set(ret))
            list_random = list_origin[rand:]
            list_random.extend(list_origin[:rand])
            for j in list_random:
                can_append = True
                for pre in all_precedence:
                    if j == pre[1]:
                        can_append = False
                if can_append:
                    for scc in strongly_connected_components:
                        if j in scc:
                            remove_scc = []
                            while set(scc) != set(remove_scc):
                                for job_of_scc in list(set(scc) - set(remove_scc)):
                                    can_append_scc = True
                                    for pre_scc in all_precedence:
                                        if job_of_scc == pre_scc[1]:
                                            can_append_scc = False
                                    if can_append_scc:
                                        remove_all_precedence = []
                                        for pre in all_precedence:
                                            if job_of_scc == pre[0]:
                                                remove_all_precedence.append(pre)
                                        for rm in remove_all_precedence:
                                            all_precedence.remove(rm)

                                        ret.append(job_of_scc)
                                        remove_scc.append(job_of_scc)
                                        break
                            break
                    else:
                        ret.append(j)
                        remove_all_precedence = []
                        for pre in all_precedence:
                            if j == pre[0]:
                                remove_all_precedence.append(pre)
                        for rm in remove_all_precedence:
                            all_precedence.remove(rm)
                    break
        return ret

    def optimize(self, random_seed):
        self.__defAllPrecedence()
        random.seed(random_seed)

        jl = self.job_list
        job_list = self.__initial_job_list(random.randint(0, len(jl) - 1))
        mode_dict = {}
        for job in job_list:
            ml = self.job[job].mode_list
            mode_dict[job] = ml[random.randint(0, len(ml) - 1)]

        s, c, garc = self.__CONSTRUCT(job_list, mode_dict)
        g_arcs = garc
        optimal_job_list = job_list
        optimal_mode_dict = mode_dict
        optimal_penalty = PENALTY_for_minimize_makespan(c)

        tabu_list = []

        num = 0
        while num < self.max_trial:
            jl, ml, pena, ga, atr_jb = self.__MOVE_for_minimize_makespan(job_list, mode_dict, g_arcs, tabu_list)
            if pena == "inf":
                break
            job_list = jl
            mode_dict = ml
            if pena < optimal_penalty:
                optimal_job_list = jl
                optimal_penalty = pena
            g_arcs = ga
            tabu_list.insert(0, atr_jb)
            if len(tabu_list) > self.tabu_length:
                tabu_list.remove(tabu_list[-1])
            num += 1

        optimal_start, optimal_completion, optimal_g_arcs = self.__CONSTRUCT(optimal_job_list, optimal_mode_dict)

        print(f"< 最適解 > ( {num}回 )\n{optimal_start}")

        return optimal_start, optimal_completion
