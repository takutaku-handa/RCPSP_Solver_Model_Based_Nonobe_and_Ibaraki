import time
import tkinter as tk
from tkinter import ttk
from main import *
from open_file import openFile


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.master.geometry("300x200")

        menuBar = tk.Menu()
        self.master.config(menu=menuBar)

        self.optimize_model = openFile("data.csv")

        fileMenu_file = tk.Menu()
        fileMenu_file.add_command(label="Exit", command=self.onExit)
        fileMenu_file.add_command(label="Open", command=self.onOpen)
        fileMenu_file.add_command(label="Save", command=self.onSave)
        fileMenu_file.add_command(label="New", command=self.onNew)
        menuBar.add_cascade(label="File", menu=fileMenu_file)

        fileMenu_model = tk.Menu()
        fileMenu_model.add_command(label="Resource", command=self.onResource)
        fileMenu_model.add_command(label="Job", command=self.onJob)
        fileMenu_model.add_command(label="Mode", command=self.onMode)
        fileMenu_model.add_command(label="Precedence", command=self.onPrecedence)
        menuBar.add_cascade(label="Model", menu=fileMenu_model)

        fileMenu_optimize = tk.Menu()
        fileMenu_optimize.add_command(label="Optimize", command=self.optimize)
        menuBar.add_cascade(label="Optimize", menu=fileMenu_optimize)

        """Resource Frame"""
        self.frame_resource = tk.Frame()
        self.frame_resource.grid(row=0, column=0, sticky="nsew")
        titleLabel = tk.Label(self.frame_resource, text="Resource page", font=('Helvetica', '35'))
        titleLabel.pack(anchor="w")

        self.res_lb_frame = tk.Frame(self.frame_resource)
        self.res_lb_frame.pack(anchor="w")

        self.resource_listbox = tk.Listbox(self.res_lb_frame)
        for res in self.optimize_model.resource.keys():
            self.resource_listbox.insert(-1, res)
        self.resource_listbox.pack(anchor="w", side=tk.LEFT)

        self.amount_listbox = tk.Listbox(self.res_lb_frame, width=50)
        for res in self.optimize_model.resource.values():
            self.amount_listbox.insert(-1, res.max)
        self.amount_listbox.pack(anchor="w", side=tk.LEFT)

        self.new_resource_entry = tk.Entry(self.frame_resource)
        self.new_resource_entry.pack(anchor="w")
        self.new_resource_amount_entry = tk.Entry(self.frame_resource)
        self.new_resource_amount_entry.pack(anchor="w")

        button = tk.Button(self.frame_resource, text="Add Resource", command=self.addResource)
        button.pack(anchor="w")

        """Job Frame"""
        self.frame_job = tk.Frame()
        self.frame_job.grid(row=0, column=0, sticky="nsew")
        titleLabel = tk.Label(self.frame_job, text="Job page", font=('Helvetica', '35'))
        titleLabel.pack(anchor="w")

        self.job_listbox = tk.Listbox(self.frame_job)
        for job in self.optimize_model.job_list:
            self.job_listbox.insert(0, job)
        self.job_listbox.pack(anchor="w")

        self.new_job_entry = tk.Entry(self.frame_job)
        self.new_job_entry.pack(anchor="w")
        button = tk.Button(self.frame_job, text="Add Job", command=self.addJob)
        button.pack(anchor="w")

        """Mode Frame"""
        self.frame_mode = tk.Frame()
        self.frame_mode.grid(row=0, column=0, sticky="nsew")
        titleLabel = tk.Label(self.frame_mode, text="Mode page", font=('Helvetica', '35'))
        titleLabel.pack(anchor="w")

        self.mode_combobox = ttk.Combobox(master=self.frame_mode, values=self.optimize_model.job_list)
        self.mode_combobox.pack(anchor="w")
        self.mode_combobox.bind('<<ComboboxSelected>>', self.showMode)
        self.target_job = None

        self.mode_listbox = tk.Listbox(self.frame_mode)
        self.mode_listbox.pack(anchor="w")
        self.mode_listbox.bind("<<ListboxSelect>>", self.setTargetMode)
        self.mode_index = None

        self.mode_entry_1 = tk.Entry(self.frame_mode)
        self.mode_entry_2 = tk.Entry(self.frame_mode)
        self.add_res_name_entry = tk.Entry(self.frame_mode)
        self.add_res_amount_entry = tk.Entry(self.frame_mode)
        self.mode_entry_1.pack(anchor="w")
        self.mode_entry_2.pack(anchor="w")

        self.new_mode_button = tk.Button(self.frame_mode, text="Add Mode", command=self.settingMode)
        self.new_mode_button.pack(anchor="w")

        self.mode_detail_text = tk.StringVar()
        self.mode_detail_text.set("")
        self.mode_detail = tk.Label(self.frame_mode, textvariable=self.mode_detail_text)
        self.mode_detail.pack(anchor="w")

        """Precedence Frame"""
        self.frame_precedence = tk.Frame()
        self.frame_precedence.grid(row=0, column=0, sticky="nsew")
        titleLabel = tk.Label(self.frame_precedence, text="Precedence page", font=('Helvetica', '35'))
        titleLabel.pack(anchor="w")

        self.frame_lb_pre = tk.Frame(self.frame_precedence)
        self.frame_lb_pre.pack(anchor="w")
        self.precedence_job1_listbox = tk.Listbox(self.frame_lb_pre)
        self.precedence_job2_listbox = tk.Listbox(self.frame_lb_pre)
        for pre in self.optimize_model.precedence:
            self.precedence_job1_listbox.insert(0, pre[0])
            self.precedence_job2_listbox.insert(0, pre[1])
        self.precedence_job1_listbox.pack(anchor="w", side=tk.LEFT)
        self.precedence_job2_listbox.pack(anchor="w", side=tk.LEFT)

        self.frame_pre_job = tk.Frame(self.frame_precedence)
        self.frame_pre_job.pack(anchor="w")
        self.precedence_job1 = tk.Entry(self.frame_pre_job)
        self.precedence_job1.pack(anchor="w", side=tk.LEFT)
        self.precedence_job2 = tk.Entry(self.frame_pre_job)
        self.precedence_job2.pack(anchor="w", side=tk.LEFT)

        button = tk.Button(self.frame_precedence, text="Add Precedence", command=self.addPrecedence)
        button.pack(anchor="w")

        """Optimize Frame"""
        self.frame_optimize = tk.Frame()
        self.frame_optimize.grid(row=0, column=0, sticky="nsew")
        titleLabel = tk.Label(self.frame_optimize, text="Optimize page", font=("Helvetica", "35"))
        titleLabel.pack(anchor="w")

        self.max_t_entry = tk.Entry(self.frame_optimize)
        self.max_t_entry.insert(0, self.optimize_model.max_t)
        self.max_t_entry.pack(anchor="w")
        self.max_trial = tk.Entry(self.frame_optimize)
        self.max_trial.insert(0, self.optimize_model.max_trial)
        self.max_trial.pack(anchor="w")
        self.tabu_length = tk.Entry(self.frame_optimize)
        self.tabu_length.insert(0, self.optimize_model.tabu_length)
        self.tabu_length.pack(anchor="w")

        button = tk.Button(self.frame_optimize, text="Optimize", command=self.gui_opt)
        button.pack(anchor="w")

        self.answer = tk.StringVar()
        self.answer.set("")
        self.answer_label = tk.Label(self.frame_optimize, textvariable=self.answer)
        self.answer_label.pack(anchor="w")

    def changePage(self, page):
        page.tkraise()

    def onExit(self):
        self.quit()

    def onOpen(self):
        print("open")

    def onSave(self):
        print("save")

    def onNew(self):
        print("new")

    def onResource(self):
        self.changePage(self.frame_resource)

    def onJob(self):
        self.changePage(self.frame_job)

    def onMode(self):
        self.frame_mode = tk.Frame()
        self.frame_mode.grid(row=0, column=0, sticky="nsew")
        titleLabel = tk.Label(self.frame_mode, text="Mode page", font=('Helvetica', '35'))
        titleLabel.pack(anchor="w")

        self.mode_combobox = ttk.Combobox(master=self.frame_mode, values=self.optimize_model.job_list)
        self.mode_combobox.pack(anchor="w")
        self.mode_combobox.bind('<<ComboboxSelected>>', self.showMode)
        self.target_job = None

        self.mode_listbox = tk.Listbox(self.frame_mode)
        self.mode_listbox.pack(anchor="w")
        self.mode_listbox.bind("<<ListboxSelect>>", self.setTargetMode)
        self.mode_index = None

        self.mode_entry_1 = tk.Entry(self.frame_mode)
        self.mode_entry_2 = tk.Entry(self.frame_mode)
        self.add_res_name_entry = tk.Entry(self.frame_mode)
        self.add_res_amount_entry = tk.Entry(self.frame_mode)
        self.mode_entry_1.pack(anchor="w")
        self.mode_entry_2.pack(anchor="w")

        self.new_mode_button = tk.Button(self.frame_mode, text="Add Mode", command=self.settingMode)
        self.new_mode_button.pack(anchor="w")

        self.mode_detail_text = tk.StringVar()
        self.mode_detail_text.set("")
        self.mode_detail = tk.Label(self.frame_mode, textvariable=self.mode_detail_text)
        self.mode_detail.pack(anchor="w")

        self.changePage(self.frame_mode)

    def onPrecedence(self):
        self.changePage(self.frame_precedence)

    def optimize(self):

        self.changePage(self.frame_optimize)

    def setSettings(self):
        max_t = int(self.max_t_entry.get())
        max_trial = int(self.max_trial.get())
        tabu_length = int(self.tabu_length.get())
        self.optimize_model.setMax_t(max_t)
        self.optimize_model.setMax_trial(max_trial)
        self.optimize_model.setTabu_length(tabu_length)

    def addResource(self):
        res_name = self.new_resource_entry.get()
        res_amount = self.new_resource_amount_entry.get()
        res_amount_list = [int(res_amount) for i in range(self.optimize_model.max_t)]

        if res_name not in self.optimize_model.resource.keys():
            self.resource_listbox.insert(0, res_name)
            self.amount_listbox.insert(0, res_amount_list)
            res = Resource(res_name)
            res.setMax(res_amount_list)
            self.optimize_model.addResource(res)
            self.add_res_name_entry.delete(0, tk.END)
            self.add_res_amount_entry.delete(0, tk.END)

    def addJob(self):
        job_name = self.new_job_entry.get()
        if job_name not in self.optimize_model.job_list:
            job = Job(job_name)
            self.job_listbox.insert(0, job_name)
            self.optimize_model.addJob(job)
            self.mode_combobox.insert(tk.END, job_name)
            self.new_job_entry.delete(0, tk.END)

    def showMode(self, event):
        self.mode_listbox.delete(0, tk.END)
        job_name = self.mode_combobox.get()
        job = self.optimize_model.job[job_name]
        self.target_job = job_name
        for m in job.mode.keys():
            self.mode_listbox.insert(0, m)
        self.mode_listbox.insert(0, "New Mode")
        self.mode_detail_text.set("")

    def setTargetMode(self, event):
        if len(self.mode_listbox.curselection()) == 0:
            return
        self.mode_index = self.mode_listbox.curselection()
        if self.mode_index != 0:
            mode_name = self.mode_listbox.get(self.mode_index)
            if mode_name == "New Mode":
                self.mode_detail_text.set("")
            else:
                target_mode_name = self.optimize_model.job[self.target_job].mode[mode_name].name
                target_mode = self.optimize_model.job[self.target_job].mode[target_mode_name]
                detail_text = f"name: {target_mode.name} ,   duration: {str(target_mode.duration)}\nresource"
                for res, amount in target_mode.resource.items():
                    detail_text += f"\n{res}        {amount}"
                self.mode_detail_text.set(detail_text)

    def settingMode(self):
        mode_name = self.mode_listbox.get(self.mode_index)
        if mode_name == "New Mode":
            target_job = self.optimize_model.job[self.target_job].name
            new_mode = Mode(name=self.mode_entry_1.get())
            new_mode.setDuration(duration=int(self.mode_entry_2.get()))
            self.optimize_model.addMode(job_name=target_job, mode=new_mode)
            self.showMode(event=None)
        else:
            target_mode = self.optimize_model.job[self.target_job].mode[mode_name]
            self.optimize_model.addResource_to_Mode(self.target_job, target_mode.name, self.mode_entry_1.get(),
                                                    int(self.mode_entry_2.get()))
            detail_text = f"name: {target_mode.name} ,   duration: {str(target_mode.duration)}\nresource"
            for res, amount in target_mode.resource.items():
                detail_text += f"\n{res}        {amount}"
            self.mode_detail_text.set(detail_text)
        self.mode_entry_1.delete(0, tk.END)
        self.mode_entry_2.delete(0, tk.END)

    def addPrecedence(self):
        job1 = self.precedence_job1.get()
        job2 = self.precedence_job2.get()
        if (job1, job2) not in self.optimize_model.precedence \
                and job1 in self.optimize_model.job_list and \
                job2 in self.optimize_model.job_list:
            self.optimize_model.addPrecedence(job1, job2)
            self.precedence_job1_listbox.insert(0, job1)
            self.precedence_job2_listbox.insert(0, job2)
            self.precedence_job1.delete(0, tk.END)
            self.precedence_job2.delete(0, tk.END)

    def gui_opt(self):
        self.setSettings()
        self.answer.set("")
        self.answer_label.update()
        st, ct = self.optimize_model.optimize(time.time())
        self.answer.set(st)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
