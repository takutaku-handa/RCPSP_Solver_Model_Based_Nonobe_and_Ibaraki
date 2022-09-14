import time

from main import *

# model
model = Model(15)

# resource
machine1 = Resource("machine1")
machine2 = Resource("machine2")
machine_dummy = Resource("dummy_machine")
machine1.setMax([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
machine2.setMax([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
machine_dummy.setMax([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
model.addResource(machine1)
model.addResource(machine2)
model.addResource(machine_dummy)

# job
jb_dict = {(1, 1): 1, (1, 2): 2, (2, 1): 2, (2, 2): 1, (3, 1): 2, (3, 2): 1}
for key, value in jb_dict.items():
    job = Job(f"job{key[0]}_{key[1]}")
    model.addJob(job)
    mode = Mode(f"mode{key[0]}_{key[1]}")
    mode.addResource(f"machine{value}", 1)
    if key == (1, 1) or key == (2, 1):
        mode.addResource("dummy_machine", 0)
    mode.setDuration(4 - key[0])
    model.addMode(f"job{key[0]}_{key[1]}", mode)

# setup job
setup_job = Job("setup_job3_1")
model.addJob(setup_job)
setup_mode = Mode("setup_mode3_1")
setup_mode.addResource("machine2", 1)
setup_mode.setDuration(1)
model.addMode("setup_job3_1", setup_mode)
model.setSetupMode("setup_job3_1", None, ["setup_mode3_1"])

# dummy
dummy_job = Job("dummy")
model.addJob(dummy_job)
dummy_mode = Mode("dummy_mode")
dummy_mode.addResource("dummy_machine", 0)
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

# optimize
st = time.time()
model.optimize(100, 0, st)
print(time.time() - st)

print(model.resource)
print(model.job)
print(model.all_precedence)

# あとやること。
# セットアップジョブのモードを、CONSTRUCTで動的に扱う
# 近傍にモードの変換を加える
# 問題の入力を簡単にする
# タブーリストの長さを調整する技術を学び、実装する
