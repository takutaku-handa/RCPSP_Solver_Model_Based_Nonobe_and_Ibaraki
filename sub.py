from main import *

# model
model = Model()

# resource
machine1 = Resource("machine1")
machine2 = Resource("machine2")
machine_dummy = Resource("dummy_machine")
machine1.setMax(np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))
machine2.setMax(np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))
machine_dummy.setMax(np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))
model.addResource(machine1)
model.addResource(machine2)
model.addResource(machine_dummy)

# job
jb_dict = {(1, 1): 1, (1, 2): 2, (2, 1): 2, (2, 2): 1, (3, 1): 2, (3, 2): 1}
for key, value in jb_dict.items():
    job = Job(f"job{key[0]}_{key[1]}")
    model.addJob(job)
    mode = Mode(f"mode{key[0]}_{key[1]}")
    mode.addResource(f"machine{value}", np.array([1 for r in range(4 - key[0])]))
    if key == (1, 1) or key == (2, 1):
        mode.addResource("dummy_machine", np.array([0 for j in range(4 - key[0])]))
    mode.setDuration(4 - key[0])
    model.addMode(f"job{key[0]}_{key[1]}", mode)

# setup job
setup_job = Job("setup_job3_1")
model.addJob(setup_job)
setup_mode = Mode("setup_mode3_1")
setup_mode.addResource("machine2", np.array([1]))
setup_mode.setDuration(1)
model.addMode("setup_job3_1", setup_mode)
model.setSetupMode("setup_job3_1", None, ["setup_mode3_1"])

# dummy
dummy_job = Job("dummy")
model.addJob(dummy_job)
dummy_mode = Mode("dummy_mode")
dummy_mode.addResource("dummy_machine", np.array([]))
dummy_mode.setDuration(0)
model.addMode("dummy", dummy_mode)

# sink
sink = Job("sink")
model.addJob(sink)
sink_mode = Mode("sink")
sink_mode.setDuration(0)
model.addMode("sink", sink_mode)

# precedence constraint
for i in range(1, 4):
    model.addPrecedence(f"job{i}_1", f"job{i}_2")
    model.addPrecedence(f"job{i}_2", "sink")

# immediate precedence
model.addImmediatePrecedence("dummy", "job1_1", "dummy_machine")
model.addImmediatePrecedence("dummy", "job2_1", "dummy_machine")
model.addImmediatePrecedence("setup_job3_1", "job3_1", "machine2")

job_list = ["setup_job3_1", "job3_1", "dummy", "job1_1", "job2_1", "job3_2", "job1_2", "job2_2", "sink"]
mode_list = ["setup_mode3_1", "mode3_1", "dummy_mode", "mode1_1", "mode2_1", "mode3_2", "mode1_2", "mode2_2", "sink"]

s, c, g = model.CONSTRUCT(job_list=job_list, mode_list=mode_list, max_t=15)
print(g)

path1, path2 = simple_directed_path("job1_1", g, s)
print(path1)
print(path2)
