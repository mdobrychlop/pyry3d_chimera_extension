from PyRy3D_input_generator import InSequences, InStructures
from shutil import copyfile
import os
import shutil
import Pmw
import Tkinter
import tkFileDialog
import tkMessageBox
import webbrowser


class Parameters_Window():
    def display(self):
        self.params_window = Tkinter.Tk()
        self.params_window.title("Simulation / scoring parameters")

        self.pwframe = Tkinter.Frame(
                        self.params_window,
                        bd=1,
                        relief="ridge",
                        pady=3,
                        padx=3
                        )
        self.pwframe.pack(fill="x")

        self.display_scaling_ranges_window()
        self.display_move_state_window()
        self.display_covalent_bonds_window()

        pw = self.pwframe

        # Hide / show certain parameters

        self.frame00 = Tkinter.LabelFrame(pw, text="PyRy3D mode")
        self.frame00.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.pyrymode_var = Tkinter.IntVar()
        self.pyrymode_var.set(1)

        self.pyrymode1_radio = Tkinter.Radiobutton(
                                self.frame00,
                                text="Evaluation / ranking",
                                variable=self.pyrymode_var,
                                value=1,
                                command=lambda: self.choose_pyrymode(1)
                                )
        self.pyrymode1_radio.grid(row=0, column=0, sticky="e")

        self.pyrymode2_radio = Tkinter.Radiobutton(
                                self.frame00,
                                text="Simulation",
                                variable=self.pyrymode_var,
                                value=2,
                                command=lambda: self.choose_pyrymode(2)
                                )
        self.pyrymode2_radio.grid(row=0, column=1, sticky="e")

        #  Basic simulation parameters

        self.frame1 = Tkinter.LabelFrame(
                        pw,
                        text="Basic simulation parameters"
                        )
        self.frame1.grid(row=1, column=0, sticky="nsew")

        self.bzz0 = Tkinter.Frame(self.frame1)
        self.bzz0.pack(side="right")
        bzz0 = Tkinter.Label(self.bzz0, text="")
        bzz0.pack()  # i give up, it's the only way to align this correctly

        self.frame0 = Tkinter.Frame(self.frame1)
        self.frame0.pack(side="right")

        self.simmet_menu = Pmw.OptionMenu(
                            self.frame0,
                            labelpos="w",
                            label_text="SIMMETHOD",
                            initialitem="SimulatedAnnealing",
                            items=[
                                "SimulatedAnnealing",
                                "Genetic",
                                "ReplicaExchange"
                                 ],
                            menubutton_width=17,
                            command=self.choose_simmethod
                            )
        self.simmet_menu.grid(row=0, column=0, sticky="e", padx=2)

        self.steps_entry = Pmw.EntryField(
                            self.frame0,
                            labelpos="w",
                            label_text="STEPS",
                            entry_bg="white",
                            value="1000",
                            entry_width=10,
                            validate={
                                "validator": "real",
                                "min": 1
                                }
                            )
        self.steps_entry.grid(row=2, column=0, sticky="e", padx=2)

        self.maxrot_entry = Pmw.EntryField(
                                self.frame0,
                                labelpos="w",
                                label_text="MAXROT",
                                entry_bg="white",
                                value="5",
                                entry_width=10,
                                validate={
                                    "validator": "real",
                                    "min": 1,
                                    "max": 360
                                    }
                                )
        self.maxrot_entry.grid(row=3, column=0, sticky="e", padx=2)

        self.maxtrans_frame = Tkinter.Frame(self.frame0)
        self.maxtrans_frame.grid(row=4, column=0, sticky="e", padx=2)

        self.maxtrx_entry = Pmw.EntryField(
                                self.maxtrans_frame,
                                labelpos="w",
                                label_text="MAXTRANS    x",
                                entry_bg="white",
                                value="5",
                                entry_width=3,
                                validate={"validator": "real"}
                                )
        self.maxtrx_entry.pack(side="left")

        self.maxtry_entry = Pmw.EntryField(
                                self.maxtrans_frame,
                                labelpos="w",
                                label_text="y",
                                entry_bg="white",
                                value="5",
                                entry_width=3,
                                validate={"validator": "real"}
                                )
        self.maxtry_entry.pack(side="left")

        self.maxtrz_entry = Pmw.EntryField(
                                self.maxtrans_frame,
                                labelpos="w",
                                label_text="z",
                                entry_bg="white",
                                value="5",
                                entry_width=3,
                                validate={"validator": "real"}
                                )
        self.maxtrz_entry.pack(side="left")

        self.reheat_frame = Tkinter.Frame(self.frame0)
        self.reheat_frame.grid(row=5, column=0, sticky="e", padx=2)

        self.reheat_entry = Pmw.EntryField(
                                self.reheat_frame,
                                labelpos="w",
                                label_text="REHEAT",
                                entry_bg="white",
                                value="1",
                                entry_width=5,
                                validate={"validator": "real"}
                                )
        self.reheat_entry.pack(side="left")

        self.reheat_menu = Pmw.OptionMenu(
                            self.reheat_frame,
                            initialitem="False",
                            items=["True", "False"],
                            menubutton_width=5
                            )
        self.reheat_menu.pack(side="right")

        # Mutation frequencies

        self.frame3 = Tkinter.LabelFrame(pw, text="Mutation frequencies")
        self.frame3.grid(row=1, column=1, sticky="nsew", rowspan=2)

        self.rotation_freq_entry = Pmw.EntryField(
                                    self.frame3,
                                    labelpos="w",
                                    label_text="ROTATION_FREQ",
                                    entry_bg="white",
                                    value="0.3",
                                    entry_width=4,
                                    validate={"validator": "real"}
                                    )
        self.rotation_freq_entry.grid(row=0, column=0, sticky="e", padx=2)

        self.rotation_cov_freq_entry = Pmw.EntryField(
                                        self.frame3,
                                        labelpos="w",
                                        label_text="ROTATION_COV_FREQ",
                                        entry_bg="white",
                                        value="0.0",
                                        entry_width=4,
                                        validate={"validator": "real"}
                                        )
        self.rotation_cov_freq_entry.grid(row=1, column=0, sticky="e", padx=2)

        self.translation_freq_entry = Pmw.EntryField(
                                        self.frame3,
                                        labelpos="w",
                                        label_text="TRANSLATION_FREQ",
                                        entry_bg="white",
                                        value="0.3",
                                        entry_width=4,
                                        validate={"validator": "real"}
                                        )
        self.translation_freq_entry.grid(row=2, column=0, sticky="e", padx=2)

        self.exchange_freq_entry = Pmw.EntryField(
                                    self.frame3,
                                    labelpos="w",
                                    label_text="EXCHANGE_FREQ",
                                    entry_bg="white",
                                    value="0.0",
                                    entry_width=4,
                                    validate={"validator": "real"}
                                    )
        self.exchange_freq_entry.grid(row=3, column=0, sticky="e", padx=2)

        self.simul_dd_freq_entry = Pmw.EntryField(
                                    self.frame3,
                                    labelpos="w",
                                    label_text="SIMUL_DD_FREQ",
                                    entry_bg="white",
                                    value="0.0",
                                    entry_width=4,
                                    validate={"validator": "real"}
                                    )
        self.simul_dd_freq_entry.grid(row=4, column=0, sticky="e", padx=2)

        self.translation_all_freq_entry = Pmw.EntryField(
                                            self.frame3,
                                            labelpos="w",
                                            label_text="TRANSLATION_ALL_FREQ",
                                            entry_bg="white",
                                            value="0.2",
                                            entry_width=4,
                                            validate={"validator": "real"}
                                            )
        self.translation_all_freq_entry.grid(
            row=5, column=0, sticky="e", padx=2)

        self.rotation_all_freq_entry = Pmw.EntryField(
                                        self.frame3,
                                        labelpos="w",
                                        label_text="ROTATION_ALL_FREQ",
                                        entry_bg="white",
                                        value="0.2",
                                        entry_width=4,
                                        validate={"validator": "real"}
                                        )
        self.rotation_all_freq_entry.grid(row=6, column=0, sticky="e", padx=2)

        self.exchangesample_freq_entry = Pmw.EntryField(
                                            self.frame3,
                                            labelpos="w",
                                            label_text="EXCHANGESAMPLE_FREQ",
                                            entry_bg="white",
                                            value="0.0",
                                            entry_width=4,
                                            validate={"validator": "real"}
                                            )
        self.exchangesample_freq_entry.grid(
            row=7, column=0, sticky="e", padx=2)

        self.warning_frame = Tkinter.LabelFrame(self.frame3, text="Important")
        self.warning_frame.grid(row=8, column=0, sticky="nsew")

        warning_label = Tkinter.Label(
                            self.warning_frame,
                            text="Sum of FREQ parameters must be equal to 1!\
                                    Click [Help] for more info.",
                            wraplength=150,
                            fg="blue"
                            )
        warning_label.pack()

        # Method dependent parameters

        self.frame2 = Tkinter.LabelFrame(
                        pw,
                        text="Method dependent parameters"
                        )
        self.frame2.grid(row=3, column=1, columnspan=2, sticky="nsew")

        self.bzzx = Tkinter.Frame(self.frame2)  # what
        self.bzzx.pack(side="right")  # what
        bzzx = Tkinter.Label(self.bzzx, text="")  # what
        bzzx.pack()  # what

        self.frame2_5 = Tkinter.Frame(self.frame2)
        self.frame2_5.pack(side="right")

        self.ann_temp_entry = Pmw.EntryField(
                                self.frame2_5,
                                labelpos="w",
                                label_text="ANN_TEMP",
                                entry_bg="white",
                                value="10",
                                entry_width=10,
                                validate={
                                    "validator": "real",
                                    "min": 1,
                                    "max": 100
                                    }
                                )
        self.ann_temp_entry.grid(row=0, column=0, sticky="e", padx=2)

        self.replicaexchange_freq_entry = Pmw.EntryField(
                                    self.frame2_5,
                                    labelpos="w",
                                    label_text="REPLICA EXCHANGE_FREQ",
                                    label_wraplength=108,
                                    entry_bg="white",
                                    value="1",
                                    entry_width=10,
                                    validate={
                                        "validator": "real",
                                        "min": 1,
                                        "max": self.steps_entry.getvalue()})
        self.replicaexchange_freq_entry.grid(
                row=1, column=0, sticky="e", padx=2
                )

        self.replicatemperatures_entry = Pmw.EntryField(
                                            self.frame2_5,
                                            labelpos="w",
                                            label_text="REPLICA TEMPERATURES",
                                            label_wraplength=108,
                                            entry_bg="white",
                                            entry_width=10
                                            )
        self.replicatemperatures_entry.grid(
            row=2, column=0, sticky="e", padx=2)

        self.reductmet_menu = Pmw.OptionMenu(
                                self.frame2_5,
                                labelpos="w",
                                label_text="REDUCTMETHOD",
                                initialitem="roulette",
                                items=[
                                    "roulette",
                                    "cutoff",
                                    "tournament"
                                    ],
                                menubutton_width=10
                                )
        self.reductmet_menu.grid(row=3, column=0, sticky="e", padx=2)

        # Scoring function parameters

        self.frame5 = Tkinter.LabelFrame(pw, text="Scoring function weights")
        self.frame5.grid(row=2, column=0, sticky="nsew")

        self.bzz1 = Tkinter.Frame(self.frame5)  # what
        self.bzz1.pack(side="right")
        bzz1 = Tkinter.Label(self.bzz1, text="")
        bzz1.pack()

        self.frame4 = Tkinter.Frame(self.frame5)
        self.frame4.pack(side="right")

        self.outbox_entry1 = Pmw.EntryField(
                                self.frame4,
                                labelpos="w",
                                label_text="OUTBOX",
                                entry_bg="white",
                                value="1",
                                entry_width=3,
                                validate={"validator": "real"}
                                )
        self.outbox_entry1.grid(row=0, column=0, sticky="e")

        self.outbox_entry2 = Pmw.EntryField(
                                self.frame4,
                                labelpos="w",
                                label_text="-",
                                entry_bg="white",
                                value="1",
                                entry_width=3,
                                validate={"validator": "real"}
                                )
        self.outbox_entry2.grid(row=0, column=1, sticky="e")

        self.map_freespace_entry1 = Pmw.EntryField(
                                        self.frame4,
                                        labelpos="w",
                                        label_text="MAP_FREESPACE",
                                        entry_bg="white",
                                        value="1",
                                        entry_width=3,
                                        validate={"validator": "real"}
                                        )
        self.map_freespace_entry1.grid(row=1, column=0, sticky="e")

        self.map_freespace_entry2 = Pmw.EntryField(
                                        self.frame4,
                                        labelpos="w",
                                        label_text="-",
                                        entry_bg="white",
                                        value="1",
                                        entry_width=3,
                                        validate={"validator": "real"}
                                        )
        self.map_freespace_entry2.grid(row=1, column=1, sticky="e")

        self.clashes_menu = Pmw.OptionMenu(
                                self.frame4,
                                labelpos="w",
                                label_text="CLASHES",
                                initialitem="CLASHES_ALLATOMS",
                                items=["CLASHES_ALLATOMS", "CLASHES"],
                                menubutton_width=8
                                )
        self.clashes_menu.grid(row=2, column=0, sticky="e", padx=2)

        self.clashes_entry1 = Pmw.EntryField(
                                self.frame4,
                                labelpos="w",
                                label_text="",
                                entry_bg="white",
                                value="1",
                                entry_width=3,
                                validate={"validator": "real"}
                                    )
        self.clashes_entry1.grid(row=2, column=1, sticky="e")

        self.clashes_entry2 = Pmw.EntryField(
                                self.frame4,
                                labelpos="w",
                                label_text="-",
                                entry_bg="white",
                                value="1",
                                entry_width=3,
                                validate={"validator": "real"}
                                )
        self.clashes_entry2.grid(row=2, column=2, sticky="e")

        self.restraints_entry1 = Pmw.EntryField(
                                    self.frame4,
                                    labelpos="w",
                                    label_text="RESTRAINTS",
                                    entry_bg="white",
                                    value="1",
                                    entry_width=3,
                                    validate={"validator": "real"}
                                    )
        self.restraints_entry1.grid(row=4, column=0, sticky="e")

        self.restraints_entry2 = Pmw.EntryField(
                                    self.frame4,
                                    labelpos="w",
                                    label_text="-",
                                    entry_bg="white",
                                    value="1",
                                    entry_width=3,
                                    validate={"validator": "real"}
                                    )
        self.restraints_entry2.grid(row=4, column=1, sticky="e")

        self.density_entry1 = Pmw.EntryField(
                                self.frame4,
                                labelpos="w",
                                label_text="DENSITY",
                                entry_bg="white",
                                value="1",
                                entry_width=3,
                                validate={"validator": "real"}
                                )
        self.density_entry1.grid(row=5, column=0, sticky="e")

        self.density_entry2 = Pmw.EntryField(
                                self.frame4,
                                labelpos="w",
                                label_text="-",
                                entry_bg="white",
                                value="1",
                                entry_width=3,
                                validate={"validator": "real"}
                                )
        self.density_entry2.grid(row=5, column=1, sticky="e")

        self.symmetry_entry1 = Pmw.EntryField(
                                self.frame4,
                                labelpos="w",
                                label_text="SYMMETRY",
                                entry_bg="white",
                                value="1",
                                entry_width=3,
                                validate={"validator": "real"}
                                )
        self.symmetry_entry1.grid(row=6, column=0, sticky="e")

        self.symmetry_entry2 = Pmw.EntryField(
                                self.frame4,
                                labelpos="w",
                                label_text="-",
                                entry_bg="white",
                                value="1",
                                entry_width=3,
                                validate={"validator": "real"}
                                )
        self.symmetry_entry2.grid(row=6, column=1, sticky="e")

        # self.chi2_entry1=Pmw.EntryField(self.frame4,labelpos="w",label_text="	CHI2",entry_bg="white",value="1",entry_width=3,validate={"validator":"real"})
        # self.chi2_entry1.grid(row=7,column=0,sticky="e")
        # self.chi2_entry2=Pmw.EntryField(self.frame4,labelpos="w",label_text="-",entry_bg="white",value="1",entry_width=3,validate={"validator":"real"})
        # self.chi2_entry2.grid(row=7,column=1,sticky="e")
        #
        # self.rge_entry1=Pmw.EntryField(self.frame4,labelpos="w",label_text="	RGE",entry_bg="white",value="1",entry_width=3,validate={"validator":"real"})
        # self.rge_entry1.grid(row=8,column=0,sticky="e")
        # self.rge_entry2=Pmw.EntryField(self.frame4,labelpos="w",label_text="-",entry_bg="white",value="1",entry_width=3,validate={"validator":"real"})
        # self.rge_entry2.grid(row=8,column=1,sticky="e")

        # Input data descriptors

        self.frame6 = Tkinter.LabelFrame(pw, text="Input data descriptors")
        self.frame6.grid(row=3, column=0, rowspan=2, sticky="nsew")

        self.bzz2 = Tkinter.Frame(self.frame6)  # what
        self.bzz2.pack(side="right")
        bzz2 = Tkinter.Label(self.bzz2, text="")
        bzz2.pack()  # (-_-)

        self.frame7 = Tkinter.Frame(self.frame6)
        self.frame7.pack(side="right")

        self.threshold_kvol_var = Tkinter.IntVar()
        self.threshold_kvol_var.set(1)

        self.threshold_radio = Tkinter.Radiobutton(
                                self.frame7,
                                variable=self.threshold_kvol_var,
                                value=1,
                                command=lambda: self.choose_threshold_kvol(1)
                                )
        self.threshold_radio.grid(row=0, column=2, sticky="e")

        self.kvol_radio = Tkinter.Radiobutton(
                            self.frame7,
                            variable=self.threshold_kvol_var,
                            value=2,
                            command=lambda: self.choose_threshold_kvol(2)
                            )
        self.kvol_radio.grid(row=1, column=2, sticky="e")

        self.threshold_entry = Pmw.EntryField(
                                self.frame7,
                                labelpos="w",
                                label_text="THRESHOLD",
                                entry_bg="white",
                                value="20",
                                entry_width=10,
                                validate={"validator": "real"}
                                )
        self.threshold_entry.grid(row=0, column=1, sticky="e")

        self.kvol_entry = Pmw.EntryField(
                            self.frame7,
                            labelpos="w",
                            label_text="KVOL",
                            entry_bg="white",
                            value="0.3",
                            entry_width=10,
                            validate={"validator": "real"}
                            )
        self.kvol_entry.grid(row=1, column=1, sticky="e")

        self.simbox_entry = Pmw.EntryField(
                                self.frame7,
                                labelpos="w",
                                label_text="SIMBOX",
                                entry_bg="white",
                                value="1.5",
                                entry_width=10,
                                validate={"validator": "real"}
                                )
        self.simbox_entry.grid(row=2, column=1, sticky="e")

        self.gridradius_entry = Pmw.EntryField(
                                    self.frame7,
                                    labelpos="w",
                                    label_text="GRIDRADIUS",
                                    entry_bg="white",
                                    value="1.2",
                                    entry_width=10,
                                    validate={"validator": "real"}
                                    )
        self.gridradius_entry.grid(row=3, column=1, sticky="e")

        self.saxsradius_entry = Pmw.EntryField(
                                    self.frame7,
                                    labelpos="w",
                                    label_text="SAXSRADIUS",
                                    entry_bg="white",
                                    value="2.0",
                                    entry_width=10,
                                    validate={"validator": "real"}
                                    )
        self.saxsradius_entry.grid(row=4, column=1, sticky="e")

        self.component_representation_menu = Pmw.OptionMenu(
                                        self.frame7,
                                        labelpos="w",
                                        label_wraplength=100,
                                        label_text="COMPONENT_REPRESENTATION",
                                        initialitem="fa",
                                        items=["ca", "cacb", "3p", "fa"],
                                        menubutton_width=5
                                        )
        self.component_representation_menu.grid(row=6, column=1, sticky="e")

        # Output parameters

        self.frame8 = Tkinter.LabelFrame(pw, text="Output parameters")
        self.frame8.grid(row=4, column=1, sticky="nsew")

        self.bzz4 = Tkinter.Frame(self.frame8)
        self.bzz4.pack(side="right")
        bzz4 = Tkinter.Label(self.bzz2, text="")
        bzz4.pack()  # (-_-)

        self.frame9 = Tkinter.Frame(self.frame8)
        self.frame9.pack(side="right")

        self.write_n_iter_entry = Pmw.EntryField(
                                    self.frame9,
                                    labelpos="w",
                                    label_text="WRITE_N_ITER",
                                    entry_bg="white",
                                    value="1",
                                    entry_width=10,
                                    validate={"validator": "real"}
                                    )
        self.write_n_iter_entry.grid(row=0, column=0, sticky="e")

        self.out_steps_entry = Pmw.EntryField(
                                self.frame9,
                                labelpos="w",
                                label_text="OUT_STEPS",
                                entry_bg="white",
                                value="1 2",
                                entry_width=10
                                )
        self.out_steps_entry.grid(row=1, column=0, sticky="e")

        self.struct_nr_entry = Pmw.EntryField(
                                self.frame9,
                                labelpos="w",
                                label_text="STRUCT_NR",
                                entry_bg="white",
                                value="1",
                                entry_width=10
                                )
        self.struct_nr_entry.grid(row=2, column=0, sticky="e")

        self.write_eachbetter_menu = Pmw.OptionMenu(
                                        self.frame9,
                                        labelpos="w",
                                        label_wraplength=70,
                                        label_text="WRITE_EACHBETTER",
                                        initialitem="False",
                                        items=["False", "True"],
                                        menubutton_width=5
                                        )
        self.write_eachbetter_menu.grid(row=3, column=0, sticky="e")

        self.write_n_iter_out_steps_var = Tkinter.IntVar()

        self.write_n_iter_radio = Tkinter.Radiobutton(
                        self.frame9,
                        variable=self.write_n_iter_out_steps_var,
                        value=1,
                        command=lambda: self.choose_write_n_iter_out_steps(1)
                        )
        self.write_n_iter_radio.grid(row=0, column=1, sticky="e")

        self.out_steps_radio = Tkinter.Radiobutton(
                        self.frame9,
                        variable=self.write_n_iter_out_steps_var,
                        value=2,
                        command=lambda: self.choose_write_n_iter_out_steps(2)
                        )
        self.out_steps_radio.grid(row=1, column=1, sticky="e")

        self.write_n_iter_out_steps_var.set(1)

        # Other

        self.frame10 = Tkinter.LabelFrame(pw, text="Other")
        self.frame10.grid(row=5, column=0, columnspan=2, sticky="nsew")

        # self.bzz5=Tkinter.Frame(self.frame10)
        # self.bzz5.pack(side="right")
        # bzz5=Tkinter.Label(self.bzz5,text="")
        # bzz5.pack() ### (-_-)

        self.frame11 = Tkinter.Frame(self.frame10)
        self.frame11.pack(fill="x")

        self.scaling_ranges_button = Tkinter.Button(
                                        self.frame11,
                                        text="SCALE_PARAMS...",
                                        command=self.psrwin.deiconify
                                        )
        self.scaling_ranges_button.grid(
            row=0, column=0, sticky="ew", padx=12, pady=3)

        self.move_state_button = Tkinter.Button(
                                    self.frame11,
                                    text="MOVE_STATE...",
                                    command=self.mvstwin.deiconify)
        self.move_state_button.grid(
            row=0, column=1, sticky="ew", padx=12, pady=3)

        self.covalent_bonds_button = Tkinter.Button(
                                        self.frame11, text="COVALENT_BONDS...",
                                        command=self.covbonwin.deiconify
                                        )
        self.covalent_bonds_button.grid(
            row=0, column=2, sticky="ew", padx=12, pady=3)

        # Help, default, apply, close buttons

        self.hdac_frame = Tkinter.Frame(
            pw, bd=1, relief="ridge", pady=3, padx=3)
        self.hdac_frame.grid(row=6, column=0, columnspan=2, sticky="nsew")

        closeparams_button = Tkinter.Button(
            self.hdac_frame,
            text="Close",
            width=10,
            command=self.params_window.withdraw)
        closeparams_button.pack(side='right')

        paramshelp_button = Tkinter.Button(
                                self.hdac_frame,
                                text="Help",
                                width=10,
                                command=lambda: webbrowser.open(
                                     "http://genesilico.pl/pyry3d/index.php\
                                     ?option=com_content&view=\
                                     article&id=52&Itemid=199#3.2")
                                )
        paramshelp_button.pack(side='left')

        paramsdef_button = Tkinter.Button(
                            self.hdac_frame,
                            text="Set defaults",
                            width=10,
                            command=self.set_defaults
                            )
        paramsdef_button.pack(side="left")

        applyparams_button = Tkinter.Button(
                                self.hdac_frame,
                                text="Apply",
                                width=10,
                                command=lambda: self.get_parameters
                                )
        applyparams_button.pack(side='right')

        self.choose_simmethod(1)
        self.choose_threshold_kvol(1)
        self.choose_write_n_iter_out_steps(1)
        self.get_parameters()

        self.params_window.protocol("WM_DELETE_WINDOW", self.handler)

    def handler(self):
        self.params_window.withdraw()

    def setState(self, widget, state='disabled'):
        # print type(widget)
        try:
            widget.configure(state=state)
        except Tkinter.TclError:
            pass
        for child in widget.winfo_children():
            self.setState(child, state=state)

    def choose_pyrymode(self, x):
        if x == 1:
            self.frame1.configure(fg="grey")
            self.frame2.configure(fg="grey")
            self.frame3.configure(fg="grey")
            self.frame8.configure(fg="grey")
            self.frame10.configure(fg="grey")
            self.warning_frame.configure(fg="grey")
            self.setState(self.frame1, "disabled")
            self.setState(self.frame2, "disabled")
            self.setState(self.frame3, "disabled")
            self.setState(self.frame8, "disabled")
            self.setState(self.frame10, "disabled")
            self.setState(self.warning_frame, "disabled")
        else:
            self.frame1.configure(fg="black")
            self.frame2.configure(fg="black")
            self.frame3.configure(fg="black")
            self.frame8.configure(fg="black")
            self.frame10.configure(fg="black")
            self.warning_frame.configure(fg="black")
            self.setState(self.frame1, "normal")
            self.setState(self.frame2, "normal")
            self.setState(self.frame3, "normal")
            self.setState(self.frame8, "normal")
            self.setState(self.frame10, "normal")
            self.setState(self.warning_frame, "normal")

    def choose_simmethod(self, x):
        # "SimulatedAnnealing","Genetic","ReplicaExchange"
        if self.simmet_menu.getvalue() == "SimulatedAnnealing":
            self.ann_temp_entry.configure(entry_state="normal")
            self.replicaexchange_freq_entry.configure(entry_state="disabled")
            self.replicatemperatures_entry.configure(entry_state="disabled")
            self.reheat_menu.configure(menubutton_state="normal")
            if self.reheat_menu.getvalue() == "True":
                self.reheat_entry.configure(entry_state="normal")
            self.reductmet_menu.configure(menubutton_state="disabled")

        if self.simmet_menu.getvalue() == "Genetic":
            self.ann_temp_entry.configure(entry_state="disabled")
            self.replicaexchange_freq_entry.configure(entry_state="disabled")
            self.replicatemperatures_entry.configure(entry_state="disabled")
            self.reheat_menu.configure(menubutton_state="disabled")
            self.reheat_entry.configure(entry_state="disabled")
            self.reductmet_menu.configure(menubutton_state="normal")

        if self.simmet_menu.getvalue() == "ReplicaExchange":
            self.ann_temp_entry.configure(entry_state="disabled")
            self.replicaexchange_freq_entry.configure(entry_state="normal")
            self.replicatemperatures_entry.configure(entry_state="normal")
            self.reheat_menu.configure(menubutton_state="disabled")
            self.reheat_entry.configure(entry_state="disabled")
            self.reductmet_menu.configure(menubutton_state="disabled")

    def choose_threshold_kvol(self, v):
        if v == 1:
            # print v
            self.threshold_kvol_var.set(1)
            # print "uotnau 1", self.threshold_kvol_var.get()
            self.threshold_entry.configure(entry_state="normal")
            self.kvol_entry.configure(entry_state="disabled")
        if v == 2:
            # print v
            self.threshold_kvol_var.set(2)
            # print "uotnau 2", self.threshold_kvol_var.get()
            self.threshold_entry.configure(entry_state="disabled")
            self.kvol_entry.configure(entry_state="normal")

    def choose_write_n_iter_out_steps(self, v):
        if v == 1:
            self.write_n_iter_out_steps_var.set(1)
            self.write_n_iter_entry.configure(entry_state="normal")
            self.out_steps_entry.configure(entry_state="disabled")
        if v == 2:
            self.write_n_iter_out_steps_var.set(2)
            self.write_n_iter_entry.configure(entry_state="disabled")
            self.out_steps_entry.configure(entry_state="normal")

    def show_scalrang_window_example(self):
        example = "PARAMSCALINGRANGES 	0 25 50\n\
                    PARAMSCALINGR1 	50 100\n\
                    PARAMSCALINGR2 	25 50\n\
                    PARAMSCALINGR3 	0 25"
        self.psrli.setvalue(example)

    def display_scaling_ranges_window(self):
        self.psrwin = Tkinter.Toplevel(self.params_window)
        self.psrwin.title("SCALEPARAMS")
        self.psrwf = Tkinter.LabelFrame(self.psrwin, text="Scale params")
        self.psrwf.pack(fill="x")

        psr_label = Tkinter.Label(
            self.psrwf,
            text="Use the field below to enter your parameters. \n\
                    Click [Help] for instructions.",
            fg="blue")
        psr_label.pack(fill="x")

        self.psrli = Pmw.ScrolledText(
                        self.psrwf,
                        columnheader=1,
                        rowheader=0,
                        rowcolumnheader=0,
                        usehullsize=1,
                        hull_width=250,
                        hull_height=150,
                        text_wrap='none',
                        Header_foreground='black',
                        text_padx=4,
                        text_pady=4,
                        Header_padx=4,
                        )
        self.psrli.pack(fill="x")

        up2 = ["Type in the field below"]

        headerLine = ''
        for column in range(len(up2)):
            headerLine = headerLine + ('%-7s   ' % (up2[column],))
        headerLine = headerLine[:-3]
        self.psrli.component('columnheader').insert('0.0', headerLine)

        self.psrf2 = Tkinter.Frame(
            self.psrwin, bd=1, relief="ridge", pady=3, padx=3)
        self.psrf2.pack(fill="x")

        closepsr_button = Tkinter.Button(
                            self.psrf2,
                            text="Close",
                            width=10,
                            command=self.psrwin.withdraw
                            )
        closepsr_button.pack(side='right')

        psrhelp_button = Tkinter.Button(
                            self.psrf2,
                            text="Help",
                            width=10,
                            command=lambda: webbrowser.open(
                                        "http://genesilico.pl/pyry3d/index.php\
                                        ?option=com_content&view=article&id=52\
                                        &Itemid=199#3.2")
                                        )
        psrhelp_button.pack(side='left')

        psrdef_button = Tkinter.Button(
                            self.psrf2,
                            text="Show example",
                            width=10,
                            command=self.show_scalrang_window_example
                            )
        psrdef_button.pack(side="left")

        applypsr_button = Tkinter.Button(
                            self.psrf2,
                            text="Apply",
                            width=10,
                            command=self.get_parameters
                            )
        applypsr_button.pack(side='right')

        self.psrwin.withdraw()

    def show_movestate_window_example(self):
        self.mvstli.setvalue(
                "D movable 5 5 5 0.1 0.1 0.1 10 10 10 0.1 0.1 1 5 30")

    def display_move_state_window(self):
        self.mvstwin = Tkinter.Toplevel(self.params_window)
        self.mvstwin.title("MOVE_STATE")
        self.mvstwf = Tkinter.LabelFrame(self.mvstwin, text="Move state")
        self.mvstwf.pack(fill="x")

        mvst_label = Tkinter.Label(
                        self.mvstwf,
                        text="Use the field below to enter your parameters. \n\
                                Click [Help] for instructions.",
                        fg="blue"
                        )
        mvst_label.pack(fill="x")

        self.mvstli = Pmw.ScrolledText(
                        self.mvstwf,
                        columnheader=1,
                        rowheader=0,
                        rowcolumnheader=0,
                        usehullsize=1,
                        hull_width=250,
                        hull_height=150,
                        text_wrap='none',
                        Header_foreground='black',
                        text_padx=4,
                        text_pady=4,
                        Header_padx=4,
                        )
        self.mvstli.pack(fill="x")

        up2 = ["Type in the field below"]

        headerLine = ''
        for column in range(len(up2)):
            headerLine = headerLine + ('%-7s   ' % (up2[column],))
        headerLine = headerLine[:-3]
        self.mvstli.component('columnheader').insert('0.0', headerLine)

        self.mvstf2 = Tkinter.Frame(
                        self.mvstwin,
                        bd=1,
                        relief="ridge",
                        pady=3,
                        padx=3
                        )
        self.mvstf2.pack(fill="x")

        closemvst_button = Tkinter.Button(
                            self.mvstf2,
                            text="Close",
                            width=10,
                            command=self.mvstwin.withdraw
                            )
        closemvst_button.pack(side='right')

        mvsthelp_button = Tkinter.Button(
                            self.mvstf2,
                            text="Help",
                            width=10,
                            command=lambda: webbrowser.open(
                                    "http://genesilico.pl/pyry3d/faq/#3.2")
                                    )
        mvsthelp_button.pack(side='left')

        mvstdef_button = Tkinter.Button(
                            self.mvstf2,
                            text="Show example",
                            width=10,
                            command=self.show_movestate_window_example)
        mvstdef_button.pack(side="left")

        applymvst_button = Tkinter.Button(
                            self.mvstf2,
                            text="Apply",
                            width=10,
                            command=self.get_parameters
                            )
        applymvst_button.pack(side='right')

        self.mvstwin.withdraw()

    def show_covbond_window_example(self):
        self.covbonli.setvalue("A ['Z','D'] [10,'CA'] [11,'CA']")

    def display_covalent_bonds_window(self):
        self.covbonwin = Tkinter.Toplevel(self.params_window)
        self.covbonwin.title("COVALENT_BONDS")
        self.covbonwf = Tkinter.LabelFrame(
            self.covbonwin, text="Covalent bonds")
        self.covbonwf.pack(fill="x")

        covbon_label = Tkinter.Label(
                        self.covbonwf,
                        text="Use the field below to enter your parameters. \n\
                                Click [Help] for instructions.",
                        fg="blue")
        covbon_label.pack(fill="x")

        self.covbonli = Pmw.ScrolledText(
                            self.covbonwf,
                            columnheader=1,
                            rowheader=0,
                            rowcolumnheader=0,
                            usehullsize=1,
                            hull_width=250,
                            hull_height=150,
                            text_wrap='none',
                            Header_foreground='black',
                            text_padx=4,
                            text_pady=4,
                            Header_padx=4,
                            )
        self.covbonli.pack(fill="x")

        up2 = ["Type in the field below"]

        headerLine = ''
        for column in range(len(up2)):
            headerLine = headerLine + ('%-7s   ' % (up2[column],))
        headerLine = headerLine[:-3]
        self.covbonli.component('columnheader').insert('0.0', headerLine)

        self.covbonf2 = Tkinter.Frame(
            self.covbonwin, bd=1, relief="ridge", pady=3, padx=3)
        self.covbonf2.pack(fill="x")

        closecovbon_button = Tkinter.Button(
                                self.covbonf2,
                                text="Close",
                                width=10,
                                command=self.covbonwin.withdraw
                                )
        closecovbon_button.pack(side='right')

        covbonhelp_button = Tkinter.Button(
                                self.covbonf2,
                                text="Help",
                                width=10,
                                command=lambda: webbrowser.open(
                                    "http://genesilico.pl/pyry3d/faq/#3.2")
                                    )
        covbonhelp_button.pack(side='left')

        covbondef_button = Tkinter.Button(
                            self.covbonf2,
                            text="Show example",
                            width=10,
                            command=self.show_covbond_window_example
                            )
        covbondef_button.pack(side="left")

        applycovbon_button = Tkinter.Button(
                                self.covbonf2,
                                text="Apply",
                                width=10,
                                command=self.get_parameters
                                )
        applycovbon_button.pack(side='right')

        self.covbonwin.withdraw()

    def set_defaults(self):
        self.simmet_menu.invoke("SimulatedAnnealing")
        self.choose_simmethod(1)
        self.steps_entry.setvalue("1000")
        self.maxrot_entry.setvalue("5")
        self.maxtrx_entry.setvalue("5")
        self.maxtry_entry.setvalue("5")
        self.maxtrz_entry.setvalue("5")

        self.reheat_entry.setvalue("1")
        self.reheat_menu.invoke("False")

        self.outbox_entry1.setvalue("1")
        self.outbox_entry2.setvalue("1")
        self.map_freespace_entry1.setvalue("1")
        self.map_freespace_entry2.setvalue("1")
        self.clashes_entry1.setvalue("1")
        self.clashes_entry2.setvalue("1")
        # self.clashes_allatoms_entry1.setvalue("1")
        # self.clashes_allatoms_entry2.setvalue("1")
        self.restraints_entry1.setvalue("1")
        self.restraints_entry2.setvalue("1")
        self.density_entry1.setvalue("1")
        self.density_entry2.setvalue("1")
        self.symmetry_entry1.setvalue("1")
        self.symmetry_entry2.setvalue("1")
        # self.chi2_entry1.setvalue("1")
        # self.chi2_entry2.setvalue("1")
        # self.rge_entry1.setvalue("1")
        # self.rge_entry2.setvalue("1")

        self.threshold_entry.setvalue("20")
        self.kvol_entry.setvalue("0.3")
        self.threshold_kvol_var.set(1)
        self.choose_threshold_kvol(1)
        self.simbox_entry.setvalue("1.5")
        self.gridradius_entry.setvalue("1.2")
        self.component_representation_menu.invoke("fa")

        self.rotation_freq_entry.setvalue("0.3")
        self.rotation_cov_freq_entry.setvalue("0.0")
        self.translation_freq_entry.setvalue("0.3")
        self.exchange_freq_entry.setvalue("0.0")
        self.simul_dd_freq_entry.setvalue("0.0")
        self.translation_all_freq_entry.setvalue("0.2")
        self.rotation_all_freq_entry.setvalue("0.2")
        self.exchangesample_freq_entry.setvalue("0.0")

        self.write_n_iter_entry.setvalue("1")
        self.choose_write_n_iter_out_steps(1)
        self.write_n_iter_out_steps_var.set(1)
        self.struct_nr_entry.setvalue("1")
        self.out_steps_entry.setvalue("1")

        self.write_eachbetter_menu.invoke("True")

        self.ann_temp_entry.setvalue("100")
        self.replicaexchange_freq_entry.setvalue("1")
        self.replicatemperatures_entry.setvalue("")
        self.reductmet_menu.invoke("roulette")

    def get_parameters(self):
        """
        Gets values of parameters provided by the user.
        Creates strings ready to be written as cfg file lines.
        """
        self.simmethod = "SIMMETHOD " + self.simmet_menu.getvalue()
        self.steps = "STEPS " + self.steps_entry.getvalue()
        self.maxrot = "MAXROT " + self.maxrot_entry.getvalue()
        self.maxtrans = "MAXTRANS " + self.maxtrx_entry.getvalue() + " " + \
                        self.maxtry_entry.getvalue() + " " + \
                        self.maxtrz_entry.getvalue()
        self.reheat = "REHEAT " + self.reheat_menu.getvalue() + " " + \
                      self.reheat_entry.getvalue()
        self.outbox = "OUTBOX " + self.outbox_entry1.getvalue() + " " + \
                      self.outbox_entry2.getvalue()
        self.map_freespace = "MAP_FREESPACE " + \
                             self.map_freespace_entry1.getvalue() + " " + \
                             self.map_freespace_entry2.getvalue()
        if self.clashes_menu.getvalue() == "CLASHES":
            self.clashes = "CLASHES " + \
                           self.clashes_entry1.getvalue() + " " + \
                           self.clashes_entry2.getvalue()
        else:
            self.clashes = "CLASHES_ALLATOMS " + \
                           self.clashes_entry1.getvalue() + " " + \
                           self.clashes_entry2.getvalue()
        self.restraints = "RESTRAINTS " + \
                          self.restraints_entry1.getvalue() + " " + \
                          self.restraints_entry2.getvalue()
        self.density = "DENSITY " + self.density_entry1.getvalue() + " " + \
                       self.density_entry2.getvalue()
        self.symmetry = "SYMMETRY " + self.symmetry_entry1.getvalue() + " " + \
                        self.symmetry_entry2.getvalue()
        # self.chi2="CHI2 "+self.chi2_entry1.getvalue()+" "+self.chi2_entry2.getvalue()
        # self.rge="RGE "+self.rge_entry1.getvalue()+" "+self.rge_entry2.getvalue()
        self.threshold = "THRESHOLD " + self.threshold_entry.getvalue()
        self.kvol = "KVOL " + self.kvol_entry.getvalue()
        self.simbox = "SIMBOX " + self.simbox_entry.getvalue()
        self.gridradius = "GRIDRADIUS " + self.gridradius_entry.getvalue()
        self.component_representation = "COMPONENT_REPRESENTATION " + \
            self.component_representation_menu.getvalue()
        self.rotation_freq = "ROTATION_FREQ " + \
                             self.rotation_freq_entry.getvalue()
        self.rotation_cov_freq = "ROTATION_COV_FREQ " + \
            self.rotation_cov_freq_entry.getvalue()
        self.translation_freq = "TRANSLATION_FREQ " + \
            self.translation_freq_entry.getvalue()
        self.exchange_freq = "EXCHANGE_FREQ " + \
                             self.exchange_freq_entry.getvalue()
        self.simul_dd_freq = "SIMUL_DD_FREQ " + \
                             self.simul_dd_freq_entry.getvalue()
        self.translation_all_freq = "TRANSLATION_ALL_FREQ " + \
                                    self.translation_all_freq_entry.getvalue()
        self.rotation_all_freq = "ROTATION_ALL_FREQ " + \
                                 self.rotation_all_freq_entry.getvalue()
        self.exchangesample_freq = "EXCHANGESAMPLE_FREQ " + \
                                   self.exchangesample_freq_entry.getvalue()

        self.write_n_iter = "WRITE_N_ITER " + \
                            self.write_n_iter_entry.getvalue()
        self.struct_nr = "STRUCT_NR " + self.struct_nr_entry.getvalue()
        self.out_steps = "OUT_STEPS " + self.out_steps_entry.getvalue()
        self.write_eachbetter = "WRITE_EACHBETTER " + \
                                self.write_eachbetter_menu.getvalue()
        self.ann_temp = "ANN_TEMP " + self.ann_temp_entry.getvalue()
        self.replicaexchange_freq = "REPLICAEXCHANGE_FREQ " + \
                                    self.replicaexchange_freq_entry.getvalue()
        self.replicatemperatures = "REPLICATEMPERATURES " + \
                                   self.replicatemperatures_entry.getvalue()
        self.reductmethod = "REDUCTMETHOD " + self.reductmet_menu.getvalue()
        self.params_scaling_ranges = self.psrli.getvalue()
        self.move_state = self.mvstli.getvalue()
        self.covalent_bonds = self.covbonli.getvalue()

        self.obvious_params = [self.simmethod, self.steps,
                               self.maxrot, self.maxtrans,
                               self.outbox, self.map_freespace,
                               self.clashes, self.restraints,
                               self.density, self.symmetry,
                               # self.chi2, self.rge,
                               self.simbox, self.gridradius,
                               self.component_representation,
                               self.rotation_freq, self.rotation_cov_freq,
                               self.translation_freq, self.exchange_freq,
                               self.simul_dd_freq, self.translation_all_freq,
                               self.rotation_all_freq, self.struct_nr,
                               self.write_eachbetter, self.exchangesample_freq,
                               ]

    def generate_config(self, outpath):

        self.get_parameters()

        cfg_file = open(outpath + "/config.txt", "w")

        print >> cfg_file, "#-----"
        print >> cfg_file, "#PYRY3D CONFIG FILE"
        print >> cfg_file, "#GENERATED BY PYRY3D UCSF CHIMERA EXTENSION"
        print >> cfg_file, "#Joanna M. Kasprzak, Mateusz Dobrychlop, Janusz M. Bujnicki"
        print >> cfg_file, "#http://www.genesilico.pl/pyry3d"
        print >> cfg_file, "#-----"

        # Writing parameters that are always there ("obvious params")

        for param in self.obvious_params:
            print >> cfg_file, param

        print >> cfg_file, "#-----"

        # Writing parameters that might not be defined:

        if self.threshold_kvol_var.get() == 1:
            print >> cfg_file, self.threshold
        else:
            print >> cfg_file, self.kvol

        if self.simmet_menu.getvalue() == "SimulatedAnnealing":
            print >> cfg_file, self.ann_temp
            print >> cfg_file, self.reheat
        elif self.simmet_menu.getvalue() == "Genetic":
            print >> cfg_file, self.reductmethod
        elif self.simmet_menu.getvalue() == "ReplicaExchange":
            print >> cfg_file, self.replicaexchange_freq
            print >> cfg_file, self.replicatemperatures

        if self.write_n_iter_out_steps_var.get() == 1:
            print >> cfg_file, self.write_n_iter
        else:
            print >> cfg_file, self.out_steps

        if len(self.params_scaling_ranges) > 3:
            print >> cfg_file, "SCALEPARAMS on"
            print >> cfg_file, self.params_scaling_ranges
        else:
            print >> cfg_file, "SCALEPARAMS off"

        if len(self.move_state) > 3:
            print >> cfg_file, self.move_state

        if len(self.covalent_bonds) > 3:
            print >> cfg_file, self.covalent_bonds

        print >> cfg_file, "IDENTIFY_DISORDERS True"
        print >> cfg_file, "START_ORIENTATION True"


class P3F():
    def __init__(self):
        self.pw = Parameters_Window()
        self.init_params_window()

    def ig_choose_output_folder(self, parent, entry):
        outpath = tkFileDialog.askdirectory(
            parent=parent, initialdir="/", title="Choose output folder")
        entry.setvalue(outpath)
        entry.configure(entry_state="disabled")
        # outpath=outpath+"/input"
        return outpath

    def ig_choose_resfile(self, parent, entry):
        outpath = tkFileDialog.askopenfilename(
            parent=parent, initialdir="/", title="Choose file")
        entry.setvalue(outpath)
        entry.configure(entry_state="disabled")
        return outpath

    def generate_input_files(
                            self,
                            outpath,
                            inpath,
                            respath,
                            mappath,
                            cfg_v,
                            str_v,
                            res_v,
                            seq_v,
                            map_v,
                            nowindow=0,
                            rankmode=0,
                            rankname="",
                            ):

        if outpath == "" or outpath is None:
            tkMessageBox.showinfo(
                            "Output directory?",
                            "Please choose an output directory for your files."
                            )
        else:
            check_outdir = 1
            if nowindow == 0:
                if rankmode == 0:
                    check_outdir = self.check_dir(outpath)

            if check_outdir == 0:
                errcheck = 1
            else:
                errcheck = 0

            inseq = InSequences()
            instr = InStructures()

            if str_v == 1 and errcheck == 0:
                print "Generating structures..."
                instr.generate_pyry_instructures(inpath, outpath, rankname)
                print "Done."

            if cfg_v == 1 and errcheck == 0:
                print "Generating configuration file..."
                self.pw.generate_config(outpath)
                print "Done."
            if res_v == 1 and errcheck == 0:
                if respath == "" or respath is None:
                    tkMessageBox.showinfo(
                        "Restraints file?", "Please choose a restraints file."
                        )
                    errcheck = 1
                else:
                    print "Copying restraints file..."
                    copyfile(respath, outpath + "/restraints.txt")
                    print "Done."
            if seq_v == 1 and errcheck == 0:
                print "Generating sequences..."
                inseq.generate_pyry_insequences(
                    outpath + "/sequences.fasta", instr.structures)
                print "Done."
            if map_v == 1 and errcheck == 0:
                if mappath == "":
                    print "No density map chosen."
                else:
                    print "Copying map..."
                    map_filename = mappath.split("/")[-1]
                    copyfile(mappath, outpath + "/" + map_filename)
                    print "Done."
            if errcheck == 0:
                if nowindow == 0:
                    tkMessageBox.showinfo(
                        "Success", "Input files generated successfully."
                        )

    def check_dir(self, dire):
        if not os.path.exists(dire):
            os.makedirs(dire)
        else:
            def go_ahead_then(dire):
                shutil.rmtree(dire)
                os.makedirs(dire)
            wte = tkMessageBox.askyesno(
                                "Warning",
                                "All files in\n" +
                                dire +
                                "\nwill be deleted. Continue?"
                                )
            if wte:
                wtd = tkMessageBox.askyesno("Warning", "Are you sure?")
                if wtd:
                    go_ahead_then(dire)
                    print "Files erased. Continuing."
                    return 1
                else:
                    tkMessageBox.showinfo(
                        "PyRy3D info", "Choose a different directory \n\
                         and try again."
                         )
                    return 0
            else:
                tkMessageBox.showinfo(
                    "PyRy3D info",
                    "Choose a different directory \n and try again."
                    )
                return 0

    def init_params_window(self):
        self.pw.display()
        self.pw.params_window.withdraw()

    def show_params_window(self):
        self.pw.params_window.deiconify()
