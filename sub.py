from main import *

# model
model = Model()

# resource
machine1 = Resource("machine1")
machine2 = Resource("machine2")
machine_dummy = Resource("dummy_machine")
machine1.setMax(np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))
machine2.setMax(np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))
machine_dummy.setMax(np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))
model.addResource(machine1)
model.addResource(machine2)
model.addResource(machine_dummy)

# job
for i in range(3):
    job_1 = Job(f"job{i + 1}_1")
    model.addJob(job_1)
    mode_1 = Mode(f"mode{i + 1}_1")
    mode_1.addResource("machine1", np.array([1 for j in range(3 - i)]))
    if i != 2:
        mode_1.addResource("dummy_machine", np.array([0 for dm in range(3 - i)]))
    model.addMode(f"job{i + 1}_1", mode_1)

    job_2 = Job(f"job{i + 1}_2")
    model.addJob(job_2)
    mode_2 = Mode(f"mode{i + 1}_2")
    mode_2.addResource("machine2", np.array([1 for j in range(3 - i)]))
    model.addMode(f"job{i + 1}_2", mode_2)

# setup job
setup_job = Job("setup_job3_1")
model.addJob(setup_job)
setup_mode = Mode("setup_mode3_1")
setup_mode.addResource("machine2", np.array([1]))
model.addMode("setup_job3_1", setup_mode)
model.setSetupMode("setup_job3_1", None, ["setup_mode3_1"])

# dummy
dummy_job = Job("dummy")
model.addJob(dummy_job)
dummy_mode = Mode("dummy_mode")
dummy_mode.addResource("dummy_machine", np.array([0]))
model.addMode("dummy", dummy_mode)

# sink
sink = Job("sink")
model.addJob(sink)
sink_mode = Mode("sink")
model.addMode("sink", sink_mode)

# precedence constraint
for i in range(1, 4):
    model.addPrecedence(f"job{i}_1", f"job{i}_2")
    model.addPrecedence(f"job{i}_2", "sink")

# immediate precedence
model.addImmediatePrecedence("dummy", "job1_1", "dummy_machine")
model.addImmediatePrecedence("dummy", "job2_1", "dummy_machine")
model.addImmediatePrecedence("setup_job3_1", "job3_1", "machine2")
