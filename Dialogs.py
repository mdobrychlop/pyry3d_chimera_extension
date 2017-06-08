import Tkinter
import ttk

class Display:
    def simpledialog(self,ttl,msg):
        dialog=Tkinter.Tk()
        dialog.title(ttl)
        mf=Tkinter.Frame(dialog,bd=1,relief="ridge",pady=5,padx=5)
        mf.pack(fill="x")
        message=Tkinter.Label(mf,text=msg).pack()
        bf=Tkinter.Frame(dialog,bd=1,relief="ridge",pady=5,padx=5)
        bf.pack(fill="x")
        button=Tkinter.Button(bf,text="OK",command=dialog.destroy).pack()
    def please_wait_window(self,reason):
        self.please_wait=Tkinter.Tk()
        self.please_wait.title("Please wait")
        please_wait=self.please_wait
        wait_frame=Tkinter.Frame(please_wait,bd=1,relief="ridge",pady=5,padx=5)
        wait_frame.pack(fill="x")
        please_wait_label=Tkinter.Label(wait_frame,text="Please wait. "+str(reason))
        please_wait_label.pack()
    def please_wait_window_prog(self):
        self.please_wait_prog=Tkinter.Tk()
        self.please_wait_prog.title("Please wait")
        please_wait=self.please_wait_prog
        wait_frame=Tkinter.Frame(please_wait,bd=1,relief="ridge",pady=5,padx=5)
        wait_frame.pack(fill="x")
        please_wait_label=Tkinter.Label(wait_frame,text="Please wait. "+"Evaluation in progress")
        please_wait_label.pack()
        prog=ttk.Progressbar(wait_frame,mode='indeterminate', length=150)
        prog.pack()
        prog.start()
        self.please_wait_prog.attributes('-topmost', 1)
        self.please_wait_prog.mainloop()
    def score_results(self,scorelist):
        scoreresults=Tkinter.Tk()
        scoreresults.title("Scoring results")
        sr=scoreresults
        
        srf1=Tkinter.Frame(sr,bd=1,relief="ridge",pady=3,padx=3)
        srf1.pack(fill="x")
        
        simscore_label=Tkinter.Label(srf1,text="Overall score: ")
        simscore_label.grid(row=0,column=0,sticky="w")
        simscore_val_label=Tkinter.Label(srf1,text=scorelist[0])
        simscore_val_label.grid(row=0,column=1,sticky="w")
        
        srf2=Tkinter.Frame(sr,bd=1,relief="ridge",pady=3,padx=3)
        srf2.pack(fill="x")
        
        clashes_label=Tkinter.Label(srf2,text="Clashes penalty: ")
        clashes_label.grid(row=0,column=0,sticky="w")
        clashes_val_label=Tkinter.Label(srf2,text=scorelist[2])
        clashes_val_label.grid(row=0,column=1,sticky="w")
        
        restraints_label=Tkinter.Label(srf2,text="Restraints penalty: ")
        restraints_label.grid(row=1,column=0,sticky="w")
        restraints_val_label=Tkinter.Label(srf2,text=scorelist[1])
        restraints_val_label.grid(row=1,column=1,sticky="w")        
        
        empty_score_label=Tkinter.Label(srf2,text="Empty map space penalty: ")
        empty_score_label.grid(row=2,column=0,sticky="w")
        empty_score_val_label=Tkinter.Label(srf2,text=scorelist[3])
        empty_score_val_label.grid(row=2,column=1,sticky="w")
        
        outbox_label=Tkinter.Label(srf2,text="Outbox penalty: ")
        outbox_label.grid(row=3,column=0,sticky="w")
        outbox_val_label=Tkinter.Label(srf2,text=scorelist[4])
        outbox_val_label.grid(row=3,column=1,sticky="w")
        
        srf3=Tkinter.Frame(sr,bd=1,relief="ridge",pady=3,padx=3)
        srf3.pack(fill="x")
        srf_close_button=Tkinter.Button(srf3,text="Close",command=sr.destroy)
        srf_close_button.pack(side="right")
    def box_grid_question(self,fun):
        def yes():
            self.question.destroy()
            fun(1)
        def no():
            self.question.destroy()
            fun(0)
        self.question=Tkinter.Tk()
        self.question.title("Question")
        self.question_frame=Tkinter.Frame(self.question,bd=1,relief="ridge",pady=5,padx=5)
        self.question_frame.pack(fill="x")
        self.question_label=Tkinter.Label(self.question_frame,text="Would you like to display simulation box and grid?")
        self.question_label.pack()
        self.question_buttons=Tkinter.Frame(self.question,bd=1,relief="ridge",pady=5,padx=5)
        self.question_buttons.pack(fill="x")
        self.q_yes=Tkinter.Button(self.question_buttons,text="Yes, please",command=yes)
        self.q_no=Tkinter.Button(self.question_buttons,text="No, thank you",command=no)
        self.q_yes.pack(side="left",fill="x")
        self.q_no.pack(side="left",fill="x")