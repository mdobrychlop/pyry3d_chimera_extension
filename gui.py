import os
import sys
import glob
import shutil
import Tkinter
import Pmw
import tkFileDialog
import tkMessageBox

import webbrowser

import chimera
from chimera import runCommand
from chimera.baseDialog import ModelessDialog


from Page1_functions import P1F
from Page3_functions import P3F
from Paths import Paths
from Dialogs import Display
from WidgetState import WS

import PyRy3D_Extension

work_already = Pmw.EntryField()

P1F=P1F(); P3F=P3F(); Paths=Paths(); Display=Display(); WS=WS()

Paths.pyrypath = Paths.pluginpath + "/PyRy3D"

if os.path.exists(Paths.pyrypath) is False:
    tkMessageBox.showwarning("PyRy3D directory?", "PyRy3D software should be placed in PATH_TO_PYRY3D_EXTENSION/PyRy3D directory.")

sys.path.append(Paths.pyrypath)

from Modules.Error.Errors import InputError, ConfigError
from Calculate import calculate_threshold
from Draw_Plot import Log_Diagram
from Calculate import run


class PyRyDialog(ModelessDialog):

    name = "PyRy3D Extension"

    buttons = ("Close")

    help = (
            "http://genesilico.pl/pyry3d/tutorials",
            PyRy3D_Extension
            )

    title = "PyRy3D Extension"

    def save_path(self, newpath):
        print newpath
        if newpath != "":
            self.initialdir = newpath

    def fillInUI(self, parent):

        self.initialdir = "/"

        # ----- U S E R S   I N T E R F A C E

        self.parento = parent

        self.StatusPathFrame = Tkinter.Frame(parent)
        self.StatusPathFrame.pack(fill="x")

        # ----- SEPARATING THE WINDOW IN TWO (STATUS + NOTEBOOK)

        self.StatusFrame = Tkinter.LabelFrame(
                            self.StatusPathFrame,
                            text="PYRY3D EXTENSION STATUS:",
                            fg="blue", pady=3, padx=3
                            )
        self.StatusFrame.pack(fill="x")

        self.StatusLabel = Tkinter.Label(
                            self.StatusFrame,
                            text="Welcome to PyRy3D Chimera Extension",
                            fg="blue"
                            )
        self.StatusLabel.pack()

        # ----- CREATING THE NOTEBOOK

        self.notebook = Pmw.NoteBook(parent)
        self.notebook.pack(fill='both', expand=1, padx=10, pady=10)

        # ----- ADDING NOTEBOOK'S FIRST PAGE - OPEN MODELS

        self.page1 = self.notebook.add("Models")
        page1 = self.page1
        self.notebook.tab("Models").focus_set()

        # ----- ADDING FIRST PAGE'S CONTENT

        # ----- FIRST FRAME (MODELS ADDING BUTTONS + MAPS / COMPONENTS LISTS):

        df0 = Tkinter.Frame(page1, bd=1, relief="ridge", pady=3, padx=3)
        df0.pack(fill="x")

        self.complist = []

        self.dens_button = Tkinter.Button(
                            df0, text="Add density map...",
                            command=self.choosemap
                            )
        self.dens_button.pack(side='left', fill="x")

        self.comp_button = Tkinter.Button(
                            df0, text="Add structure...",
                            command=self.choosecomp
                            )
        self.comp_button.pack(side='left', fill="x")

        df = Tkinter.Frame(page1, bd=1, relief="ridge", pady=3, padx=3)
        df.pack(fill="x")

        fixedFont = Pmw.logicalfont('Fixed')

        # Frame displaying selected density map filename
        self.mapli = Pmw.ScrolledText(
                        df,
                        labelpos='n',
                        label_text='',
                        columnheader=1,
                        rowheader=0,
                        rowcolumnheader=0,
                        usehullsize=1,
                        hull_width=420,
                        hull_height=120,
                        text_wrap='none',
                        Header_foreground='blue',
                        text_padx=4,
                        text_pady=4,
                        Header_padx=4,
                        )
        self.mapli.grid(row=0, columnspan=2)

        up1 = ["Map ready to open: (not required)"]

        headerLine = ''
        for column in range(len(up1)):
            headerLine = headerLine + ('%-7s   ' % (up1[column],))
        headerLine = headerLine[:-3]
        self.mapli.component('columnheader').insert('0.0', headerLine)
        self.mapli.configure(text_state='disabled', Header_state='disabled')

        # Frame displaying selected components' filenames
        self.struli = Pmw.ScrolledText(
                        df,
                        columnheader=1,
                        rowheader=0,
                        rowcolumnheader=0,
                        usehullsize=1,
                        hull_width=420,
                        hull_height=220,
                        text_wrap='none',
                        Header_foreground='blue',
                        text_padx=4,
                        text_pady=4,
                        Header_padx=4,
                        )
        self.struli.grid(row=1, columnspan=2, sticky="nsew")

        up2 = ["Structures ready to open: (at least two required)"]

        headerLine = ''
        for column in range(len(up2)):
            headerLine = headerLine + ('%-7s   ' % (up2[column],))
        headerLine = headerLine[:-3]
        self.struli.component('columnheader').insert('0.0', headerLine)

        self.struli.configure(text_state='disabled', Header_state='disabled')

        # ----- SECOND FRAME - LOAD/CLEAR DATA, NEW SESSION BUTTONS

        of = Tkinter.Frame(page1, bd=1, relief="ridge", pady=3, padx=3)
        of.pack(fill="x")

        self.open_button = Tkinter.Button(
                            of, text="Load data",
                            command=self.openandsaveall
                            )
        self.open_button.grid(row=0, column=0, sticky="ew")

        self.clear_button = Tkinter.Button(
                            of, text="Clear data",
                            command=self.clear
                            )
        self.clear_button.grid(row=0, column=1, sticky="ew")

        self.new_session_button = Tkinter.Button(
                            of, text="New session",
                            command=self.new_session
                            )
        self.new_session_button.grid(row=0, column=2, sticky="ew")
        self.new_session_button.configure(state="disabled")

        # ----- ADDING NOTEBOOK'S SECOND PAGE - SIMULATION / SCORE

        self.page2 = self.notebook.add("Sim/Score")

        # ----- ADDING SECOND PAGE'S CONTENT

        # ----- FRAME1: CONFIGURATION PARAMETERS

        self.conf_params_frame = Tkinter.Frame(
                                    self.page2, bd=1, relief="ridge",
                                    pady=3, padx=3
                                    )
        self.conf_params_frame.pack(fill="x")
        sscf = self.conf_params_frame

        self.cfg_v = Tkinter.IntVar(sscf)
        self.cfg_v.set(1)

        self.ss_cfg_win_checkbutton = Tkinter.Radiobutton(
                                        sscf,
                                        text="Get parameters from parameters window",
                                        variable=self.cfg_v,
                                        value=1,
                                        command=lambda: self.cfg_choice(self.cfg_v)
                                        )
        self.ss_cfg_win_checkbutton.grid(row=1, column=0, columnspan=2, sticky="w")

        self.ss_params_button = Tkinter.Button(
                                    sscf, text="Parameters window...",
                                    command=P3F.show_params_window
                                    )
        self.ss_params_button.grid(row=2, column=0, sticky="w")

        self.ss_cfg_fil_checkbutton = Tkinter.Radiobutton(
                                        sscf,
                                        text="Get parameters from configuration file",
                                        variable=self.cfg_v, value=2,
                                        command=lambda: self.cfg_choice(self.cfg_v)
                                        )
        self.ss_cfg_fil_checkbutton.grid(row=3, column=0, columnspan=2, sticky="w")

        self.ss_cfg_fil_entry = Pmw.EntryField(
                                    sscf, labelpos="w",
                                    label_text="Configuration file:",
                                    entry_bg="white", entry_width=15
                                    )
        self.ss_cfg_fil_entry.grid(row=4, column=0, sticky="e")

        self.ss_cfg_fil_button = Tkinter.Button(
                                    sscf, text="Browse",
                                    command=self.ss_choose_cfg
                                    )
        self.ss_cfg_fil_button.grid(row=4, column=1, sticky="e")

        self.cfg_choice(self.cfg_v)

        # ----- FRAME2: RESTRAINTS
        self.restraints_frame = Tkinter.Frame(
                        self.page2, bd=1,
                        relief="ridge",
                        pady=3, padx=3
                        )
        self.restraints_frame.pack(fill="x")
        rsf = self.restraints_frame

        res_v = Tkinter.IntVar(rsf)
        res_v.set(1)

        self.res_empty_radiobutton = Tkinter.Radiobutton(
                                        rsf,
                                        text="Do not use experimental restraints",
                                        variable=res_v, value=1,
                                        command=lambda: self.res_choice(res_v)
                                        )
        self.res_empty_radiobutton.grid(row=1, column=0, columnspan=2, sticky="w")

        self.res_fil_radiobutton = Tkinter.Radiobutton(
                                    rsf,
                                    text="Use restraints file from hard drive",
                                    variable=res_v, value=2,
                                    command=lambda: self.res_choice(res_v)
                                    )
        self.res_fil_radiobutton.grid(row=2, column=0, columnspan=2, sticky="w")

        self.res_fil_entry = Pmw.EntryField(
                                rsf, labelpos="w",
                                label_text="Restraints file:",
                                entry_bg="white", entry_width=15)
        self.res_fil_entry.grid(row=3, column=0, sticky="e")

        self.res_fil_button = Tkinter.Button(
                                rsf, text="Browse",
                                command=self.ss_choose_resfile
                                )
        self.res_fil_button.grid(row=3, column=1, sticky="e")

        self.res_choice(res_v)

        # ----- FRAME3: SEQUENCES
        self.sequence_frame = Tkinter.Frame(
                                self.page2, bd=1,
                                relief="ridge",
                                pady=3, padx=3
                                )
        self.sequence_frame.pack(fill="x")

        sframe = self.sequence_frame

        self.simseq_v = Tkinter.IntVar(sframe)
        self.simseq_v.set(1)

        self.seq_gen_radiobutton = Tkinter.Radiobutton(
                                    sframe,
                                    text="Generate sequences automatically",
                                    variable=self.simseq_v, value=1,
                                    command=lambda: self.seq_choice(self.simseq_v)
                                    )
        self.seq_gen_radiobutton.grid(row=1, column=0, columnspan=2, sticky="w")

        self.seq_fil_radiobutton = Tkinter.Radiobutton(
                                    sframe,
                                    text="Use sequence file from hard drive",
                                    variable=self.simseq_v, value=2,
                                    command=lambda: self.seq_choice(self.simseq_v)
                                    )
        self.seq_fil_radiobutton.grid(row=2, column=0, columnspan=2, sticky="w")

        self.seq_fil_entry = Pmw.EntryField(
                                sframe,
                                labelpos="w",
                                label_text="Fasta file:",
                                entry_bg="white", entry_width=15
                                )
        self.seq_fil_entry.grid(row=3, column=0, sticky="e")

        self.seq_fil_button = Tkinter.Button(
                                sframe,
                                text="Browse",
                                command=self.ss_choose_seqfile
                                )
        self.seq_fil_button.grid(row=3, column=1, sticky="e")

        self.seq_text_radiobutton = Tkinter.Radiobutton(
                                    sframe,
                                    text="Input sequences manually",
                                    variable=self.simseq_v, value=3,
                                    command=lambda: self.seq_choice(self.simseq_v)
                                    )
        self.seq_text_radiobutton.grid(row=4, column=0, columnspan=2, sticky="w")

        self.seq_text_button = Tkinter.Button(
                                sframe,
                                text="Input window...",
                                command=self.display_text_sequence_window
                                )
        self.seq_text_button.grid(row=5, column=0, sticky="w")

        # Manual input sequence window
        self.seq_text_win = Tkinter.Tk()
        self.seq_text_win.title("Sequences")
        self.seq_text_wf = Tkinter.LabelFrame(
                            self.seq_text_win,
                            text="Sequences"
                            )

        self.seq_text_wf.pack(fill="x")
        seq_text_label = Tkinter.Label(
                            self.seq_text_wf,
                            text="Use the field below to enter your sequences in FASTA format.\
                             \nEnter sequences for all structures.", fg="blue"
                             )
        seq_text_label.pack(fill="x")

        self.seq_text_li = Pmw.ScrolledText(
                            self.seq_text_wf,
                            columnheader=0,
                            rowheader=0,
                            rowcolumnheader=0,
                            usehullsize=1,
                            hull_width=400,
                            hull_height=300,
                            text_wrap='none',
                            text_padx=4,
                            text_pady=4,
                            )
        self.seq_text_li.pack(fill="x")

        self.seq_text_f2 = Tkinter.Frame(
                            self.seq_text_win,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.seq_text_f2.pack(fill="x")

        closeseq_text__button = Tkinter.Button(
                                self.seq_text_f2,
                                text="Apply and close",
                                width=10,
                                command=self.seq_text_win.withdraw
                                )
        closeseq_text__button.pack(side='right')

        seq_text_help_button = Tkinter.Button(
                                self.seq_text_f2,
                                text="Help",
                                width=10,
                                command=lambda: webbrowser.open("http://genesilico.pl/pyry3d/concepts#sequences")
                                )
        seq_text_help_button.pack(side='left')

        self.seq_text_win.withdraw()
        ###

        self.seq_choice(self.simseq_v)

        # ----- OUTPUT DIR FRAME

        self.outdir_frame = Tkinter.Frame(
                            self.page2,
                            bd=1,
                            relief="ridge",
                            pady=4, padx=4
                            )
        self.outdir_frame.pack(fill="x")
        odfr = self.outdir_frame

        self.outdir_entry = Pmw.EntryField(
                            odfr,
                            labelpos="w",
                            label_text="Output directory:",
                            entry_bg="white",
                            entry_width=15
                            )
        self.outdir_entry.grid(row=0, column=0, sticky="e")

        self.outdir_button = Tkinter.Button(
                                odfr,
                                text="Browse",
                                command=self.ss_choose_outdir
                                )
        self.outdir_button.grid(row=0, column=1, sticky="e")

        # ----- ACTIONS FRAMES

        self.autoscore_frame = Tkinter.Frame(
                                self.page2,
                                bd=1, relief="ridge",
                                pady=4, padx=4
                                )
        self.autoscore_frame.pack(fill="x")

        self.autoscore_button = Tkinter.Button(
                                self.autoscore_frame,
                                text="Calculate PyRy3D score for displayed complex",
                                width=37, command=self.score_complex
                                )
        self.autoscore_button.pack(fill="x")
        self.autoscore_button.configure(state="disabled")

        self.simulation_frame = Tkinter.Frame(
                                self.page2, bd=1,
                                relief="ridge",
                                pady=4, padx=4
                                )
        self.simulation_frame.pack(fill="x")

        self.simulation_button = Tkinter.Button(
                                    self.simulation_frame,
                                    text="Perform PyRy3D simulation",
                                    width=37,
                                    command=self.simulate_complex_fin)
        self.simulation_button.pack(fill="x")
        self.simulation_button.configure(state="disabled")

        self.threshold_frame = Tkinter.Frame(
                                self.page2,
                                bd=1, relief="ridge",
                                pady=4, padx=4
                                )
        self.threshold_frame.pack(fill="x")

        self.threshold_button = Tkinter.Button(
                                self.threshold_frame,
                                text="Calculate density threshold",
                                width=37,
                                command=self.calc_threshold
                                )
        self.threshold_button.pack(fill="x")

        # ----- ADDING NOTEBOOK'S THIRD PAGE - INPUT GENERATOR

        self.page3 = self.notebook.add("Input Gen")

        # ----- ADDING THIRD PAGE'S CONTENT

        ig_str_v = Tkinter.IntVar()
        ig_map_v = Tkinter.IntVar()
        ig_seq_v = Tkinter.IntVar()
        ig_res_v = Tkinter.IntVar()
        ig_res_v.set(0)
        ig_con_v = Tkinter.IntVar()
        ig_con_v.set(0)

        self.ingen1_frame = Tkinter.Frame(
                            self.page3,
                            bd=1,
                            relief="ridge",
                            pady=3, padx=3
                            )
        self.ingen1_frame.pack(fill="x")
        ig1f = self.ingen1_frame

        ig1_label = Tkinter.Label(
                    ig1f,
                    text="Choose input files to generate:"
                    )
        ig1_label.grid(row=0, column=0, columnspan=2, sticky="w")

        self.ig_str_checkbutton = Tkinter.Checkbutton(
                                    ig1f,
                                    text="Structures",
                                    variable=ig_str_v,
                                    command=lambda: self.ig_check_elements(
                                                    ig_str_v,
                                                    ig_map_v,
                                                    ig_seq_v
                                                    )
                                    )
        self.ig_str_checkbutton.grid(row=1, column=0, sticky="w")

        self.ig_map_checkbutton = Tkinter.Checkbutton(
                                    ig1f,
                                    text="Density map",
                                    variable=ig_map_v,
                                    command=lambda: self.ig_check_elements(
                                                    ig_str_v,
                                                    ig_map_v,
                                                    ig_seq_v
                                                    )
                                    )
        self.ig_map_checkbutton.grid(row=2, column=0, sticky="w")

        self.ig_seq_checkbutton = Tkinter.Checkbutton(
                                    ig1f,
                                    text="Sequences",
                                    variable=ig_seq_v,
                                    command=lambda: self.ig_check_elements(
                                                    ig_str_v,
                                                    ig_map_v,
                                                    ig_seq_v
                                                    )
                                    )
        self.ig_seq_checkbutton.grid(row=3, column=0, sticky="w")

        def ig_choose_resfile():
            Paths.ig_respath = P3F.ig_choose_resfile(
                                self.page3,
                                self.ig_res_entry
                                )

        self.ig_res_checkbutton = Tkinter.Checkbutton(
                                    ig1f,
                                    text="Restraints",
                                    variable=ig_res_v,
                                    command=lambda: self.ig_check_res(ig_res_v)
                                    )
        self.ig_res_checkbutton.grid(row=4, column=0, sticky="w")

        self.ig_res_entry = Pmw.EntryField(
                            ig1f,
                            labelpos="w",
                            label_text="Restraints file:",
                            entry_width=17,
                            entry_bg="white"
                            )
        self.ig_res_entry.grid(row=5, column=0, sticky="w")

        self.ig_res_button = Tkinter.Button(
                                ig1f,
                                text="Browse",
                                command=ig_choose_resfile
                                )
        self.ig_res_button.grid(row=5, column=1, sticky="w")

        self.ig_con_checkbutton = Tkinter.Checkbutton(
                                    ig1f,
                                    text="Configuration file",
                                    variable=ig_con_v,
                                    command=lambda: self.ig_check_con(ig_con_v)
                                    )
        self.ig_con_checkbutton.grid(row=6, column=0, sticky="w")

        self.ig_con_button = Tkinter.Button(
                                ig1f,
                                text="Parameters window...",
                                command=P3F.show_params_window
                                )
        self.ig_con_button.grid(row=7, column=0, sticky="w")

        self.ingen2_frame = Tkinter.Frame(
                            self.page3,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.ingen2_frame.pack(fill="x")
        ig2f = self.ingen2_frame

        def ig_choose_output_folder():
            Paths.ig_outpath = P3F.ig_choose_output_folder(
                                self.page3,
                                self.ig_out_entry
                                )

        self.ig_out_entry = Pmw.EntryField(
                            ig2f,
                            labelpos="w",
                            label_text="Generate files in:",
                            entry_width=17,
                            entry_bg="white"
                            )
        self.ig_out_entry.grid(row=0, column=0, sticky="w")

        self.ig_out_button = Tkinter.Button(
                                ig2f,
                                text="Browse",
                                command=ig_choose_output_folder
                                )
        self.ig_out_button.grid(row=0, column=1, sticky="w")

        self.ingen3_frame = Tkinter.Frame(
                            self.page3,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.ingen3_frame.pack(fill="x")

        def ig_generate_input_files():
            try:
                P1F.writeAllPDBs(Paths.temppath, Paths.mappath)
                P3F.generate_input_files(
                    Paths.ig_outpath, Paths.temppath, Paths.ig_respath,
                    Paths.mappath, ig_con_v.get(), ig_str_v.get(),
                    ig_res_v.get(), ig_seq_v.get(), ig_map_v.get(),
                    nowindow=0
                    )
            except Exception as e:
                tkMessageBox.showwarning("Error", e)

        self.ingen_button = Tkinter.Button(
                            self.ingen3_frame,
                            text="Generate defined input files",
                            command=ig_generate_input_files
                            )
        self.ingen_button.grid()

        self.ig_check_res(ig_res_v)
        self.ig_check_con(ig_con_v)

        # ----- ADDING NOTEBOOK'S FOURTH PAGE - ANIMATION GENERATOR

        self.page4 = self.notebook.add("Animations")
        page4 = self.page4

        def set_anim_movie_out():
            path = tkFileDialog.askdirectory(
                    parent=parent,
                    initialdir=self.initialdir,
                    title="Choose directory"
                    )
            self.anim_dir_entry.setvalue(path)
            self.save_path(path)

        def set_anim_img_out():
            path = tkFileDialog.askdirectory(
                    parent=parent,
                    initialdir=self.initialdir,
                    title="Choose directory"
                    )
            self.anim_img_out.setvalue(path)
            self.save_path(path)

        def generate_movie():
            from Movies import Anim

            try:
                A = Anim()

                A.dirpath = self.anim_dir_entry.getvalue()
                A.paths = A.get_paths()
                A.wait = 5
                A.step = self.rec_entry.getvalue()
                A.img_outdir = self.anim_img_out.getvalue()
                A.output = self.anim_out_entry.getvalue()
                A.format = self.anim_format.getvalue()
                A.size_x = self.anim_dimensions_x_entry.getvalue()
                A.size_y = self.anim_dimensions_y_entry.getvalue()

                if A.dirpath == "" or A.paths == ""\
                   or A.wait == "" or A.step == ""\
                   or A.img_outdir == "" or A.output == ""\
                   or A.format == "":
                    tkMessageBox.showinfo(
                        "PyRy3D info",
                        "Please fill all the fields except size before continuing."
                        )
                elif len(chimera.openModels.list()) == 0:
                    tkMessageBox.showinfo(
                        "PyRy3D info",
                        "Please open and position your shape descriptor first."
                        )
                elif len(chimera.openModels.list()) > 1:
                    tkMessageBox.showinfo(
                        "PyRy3D info",
                        "Only your shape descriptor should be opened in Chimera before starting."
                        )
                else:
                    A.generate_alt()

            except Exception as e:
                tkMessageBox.showwarning("Error", e)

        def anim_get_inpdir():
            path = tkFileDialog.askdirectory(
                    initialdir=self.initialdir,
                    title="Choose input folder"
                    )
            self.anim_dir_entry.setvalue(path)
            self.anim_dir_entry.configure(entry_state="disabled")
            potential_frames = os.listdir(path)
            self.potential_frames_number = len(potential_frames)
            self.save_path(path)

        def anim_get_imgdir():
            path = tkFileDialog.askdirectory(
                    initialdir=self.initialdir,
                    title="Choose input folder"
                    )
            self.anim_img_out.setvalue(path)
            self.anim_img_out.configure(entry_state="disabled")
            self.save_path(path)

        def anim_calc_frames():
            frac = self.potential_frames_number / int(self.rec_entry.getvalue())
            self.rec_lab3.configure(text=str(frac))

        def anim_get_outfile():
            allowed_format = "."+self.anim_format.getvalue()
            path = tkFileDialog.asksaveasfilename(
                    initialdir=self.initialdir,
                    title="Choose output file",
                    filetypes=[("movie files", allowed_format)]
                    )
            self.anim_out_entry.setvalue(path)
            self.anim_out_entry.configure(entry_state="disabled")
            self.save_path(path)

        # ----- ADDING FOURTH PAGE'S CONTENT

        self.anim_f0 = Tkinter.Frame(
                        page4,
                        bd=1, relief="ridge",
                        pady=3, padx=3
                        )
        self.anim_f0.pack(fill="x")

        self.anim_text = Tkinter.Label(
                            self.anim_f0,
                            text="Before starting the animation generation,\
                            \nopen and position your shape descriptor in the\
                            \nChimera graphics window.",
                            fg="blue"
                            )
        self.anim_text.pack()

        self.anim_f1 = Tkinter.Frame(
                        page4,
                        bd=1, relief="ridge",
                        pady=3, padx=3
                        )
        self.anim_f1.pack(fill="x")

        self.anim_dir_entry = Pmw.EntryField(
                                self.anim_f1,
                                labelpos="w",
                                label_text="PyRy3D output files:",
                                entry_width=10,
                                entry_bg="white"
                                )
        self.anim_dir_entry.pack(side="left")

        self.anim_dir_button = Tkinter.Button(
                                self.anim_f1,
                                text="Browse",
                                command=anim_get_inpdir
                                )
        self.anim_dir_button.pack(side="left")

        self.anim_f2 = Tkinter.Frame(
                        page4,
                        bd=1, relief="ridge",
                        pady=3, padx=3
                        )
        self.anim_f2.pack(fill="x")

        self.rec_entry = Pmw.EntryField(
                            self.anim_f2,
                            labelpos="w",
                            label_text="Record 1 in",
                            entry_width=5,
                            entry_bg="white",
                            validate={"validator": "real"},
                            command=anim_calc_frames
                            )
        self.rec_entry.pack(side="left")

        self.rec_lab = Tkinter.Label(self.anim_f2, text=" files")
        self.rec_lab.pack(side="left")

        self.anim_f3 = Tkinter.Frame(
                        page4,
                        bd=1, relief="ridge",
                        pady=3, padx=3
                        )
        self.anim_f3.pack(fill="x")

        self.rec_lab2 = Tkinter.Label(self.anim_f3, text="Number of frames:")
        self.rec_lab2.pack(side="left")

        self.rec_lab3 = Tkinter.Label(self.anim_f3, text="0")
        self.rec_lab3.pack(side="left")

        self.rec_calc_button = Tkinter.Button(
                                self.anim_f3,
                                text="Calculate",
                                command=anim_calc_frames
                                )
        self.rec_calc_button.pack(side="left")

        self.anim_f4 = Tkinter.Frame(
                        page4,
                        bd=1, relief="ridge",
                        pady=3, padx=3
                        )
        self.anim_f4.pack(fill="x")

        self.anim_out_entry = Pmw.EntryField(
                                self.anim_f4,
                                labelpos="w",
                                label_text="Save movie file as:",
                                entry_width=20,
                                entry_bg="white"
                                )
        self.anim_out_entry.grid(row=0, column=0, sticky="w")

        self.anim_out_button = Tkinter.Button(
                                self.anim_f4,
                                text="Browse",
                                command=anim_get_outfile
                                )
        self.anim_out_button.grid(row=0, column=1, sticky="w")

        self.anim_format = Pmw.OptionMenu(
                            self.anim_f4,
                            labelpos="w",
                            label_text="Movie format:",
                            initialitem="mov",
                            items=["h264", "vp8", "theora", "mov",
                                     "avi", "mp4", "mp2", "mpeg"]
                            )
        self.anim_format.grid(row=1, column=0, sticky="w")

        self.anim_f6 = Tkinter.Frame(
                        page4,
                        bd=1, relief="ridge",
                        pady=3, padx=3
                        )
        self.anim_f6.pack(fill="x")

        self.anim_img_out = Pmw.EntryField(
                            self.anim_f6,
                            labelpos="w",
                            label_text="Save images in:",
                            entry_width=15,
                            entry_bg="white"
                            )
        self.anim_img_out.pack(side="left")

        self.anim_img_but = Tkinter.Button(
                            self.anim_f6,
                            text="Browse",
                            command=anim_get_imgdir
                            )
        self.anim_img_but.pack(side="left")

        self.anim_f5 = Tkinter.Frame(
                        page4,
                        bd=1, relief="ridge",
                        pady=3, padx=3
                        )
        self.anim_f5.pack(fill="x")

        self.anim_dimensions_x_entry = Pmw.EntryField(
                                        self.anim_f5,
                                        labelpos="w",
                                        label_text="Movie size:    width:",
                                        entry_width=5, entry_bg="white",
                                        validate={"validator": "real"}
                                        )
        self.anim_dimensions_x_entry.pack(side="left")

        self.anim_dimensions_y_entry = Pmw.EntryField(
                                        self.anim_f5,
                                        labelpos="w",
                                        label_text="height:",
                                        entry_width=5, entry_bg="white",
                                        validate={"validator": "real"}
                                        )
        self.anim_dimensions_y_entry.pack(side="left")

        self.anim_f8 = Tkinter.Frame(
                        page4,
                        bd=1, relief="ridge",
                        pady=3, padx=3
                        )
        self.anim_f8.pack(fill="x")

        self.anim_start = Tkinter.Button(
                            self.anim_f8,
                            text="Generate movie",
                            command=generate_movie
                            )
        self.anim_start.pack(side="right")

        ahl = "http://genesilico.pl/pyry3d/pyry_tutorial/Tutorial_part7.pdf"
        self.anim_help = Tkinter.Button(
                            self.anim_f8,
                            text="Help", width=10,
                            command=lambda: webbrowser.open(ahl)
                            )
        self.anim_help.pack(side="right")

        # ----- ADDING NOTEBOOK'S FIFTH PAGE - RANKING

        self.page5 = self.notebook.add("Ranking")
        page5 = self.page5

        # ----- ADDING FIFTH PAGE'S CONTENT

        # THE WAY STRUCTURES ARE LOADED

        self.rank_fc_v = Tkinter.IntVar()
        self.rank_fc_v.set(0)
        self.p5_cfg_v = Tkinter.IntVar(sscf)
        self.p5_cfg_v.set(1)

        self.p51_frame = Tkinter.Frame(
                            self.page5,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.p51_frame.pack(fill="x")
        p51 = self.p51_frame

        self.p5_fromchimera_check = Tkinter.Radiobutton(
                                    p51,
                                    text="Load complexes and map from Chimera window",
                                    variable=self.rank_fc_v,
                                    value=0, command=self.ranking_inp_choose
                                    )
        self.p5_fromchimera_check.grid(row=0, sticky="w")

        self.p5_fromfiles_check = Tkinter.Radiobutton(
                                    p51,
                                    text="Load complexes and map from files",
                                    variable=self.rank_fc_v,
                                    value=1, command=self.ranking_inp_choose
                                    )
        self.p5_fromfiles_check.grid(row=1, sticky="w")

        # INPUT STRUCTURES

        self.p54_frame = Tkinter.Frame(
                            self.page5,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.p54_frame.pack(fill="x")
        p54 = self.p54_frame

        self.p5_input_entry = Pmw.EntryField(
                                p54,
                                labelpos="w",
                                label_text="Structures directory:",
                                entry_width=15, entry_bg="white",
                                entry_state="disabled",
                                label_state="disabled"
                                )
        self.p5_input_entry.grid(row=0, column=0, sticky="e")

        self.p5_input_button = Tkinter.Button(
                                p54,
                                text="Browse",
                                command=self.ranking_input_set
                                )
        self.p5_input_button.grid(row=0, column=1, sticky="w")

        # PARAMETERS

        self.p55_frame = Tkinter.Frame(
                            self.page5,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.p55_frame.pack(fill="x")
        p55 = self.p55_frame

        self.p5_cfg_win_checkbutton = Tkinter.Radiobutton(
                                        p55,
                                        text="Get parameters from parameters window",
                                        variable=self.p5_cfg_v,
                                        value=1,
                                        command=lambda: self.p5_cfg_choice(self.p5_cfg_v)
                                        )
        self.p5_cfg_win_checkbutton.grid(row=2, column=0, columnspan=2, sticky="w")

        self.p5_params_button = Tkinter.Button(
                                p55, text="Parameters window...",
                                command=P3F.show_params_window
                                )
        self.p5_params_button.grid(row=3, column=0, sticky="w")

        self.p5_cfg_fil_checkbutton = Tkinter.Radiobutton(
                                        p55,
                                        text="Get parameters from configuration file",
                                        variable=self.p5_cfg_v,
                                        value=2,
                                        command=lambda: self.p5_cfg_choice(self.p5_cfg_v)
                                        )
        self.p5_cfg_fil_checkbutton.grid(row=4, column=0, columnspan=2, sticky="w")

        self.p5_cfg_entry = Pmw.EntryField(
                            p55,
                            labelpos="w",
                            label_text="Configuration file:",
                            entry_width=15,
                            entry_bg="white"
                            )
        self.p5_cfg_entry.grid(row=5, column=0, sticky="e")

        self.p5_cfg_button = Tkinter.Button(
                                p55,
                                text="Browse",
                                command=self.ranking_cfg_set
                                )
        self.p5_cfg_button.grid(row=5, column=1, sticky="w")

        # RESTRAINTS

        self.p56_frame = Tkinter.Frame(
                            self.page5,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.p56_frame.pack(fill="x")
        p56 = self.p56_frame

        self.p5_res_v = Tkinter.IntVar(p56)
        self.p5_res_v.set(1)

        self.p5_empty_radiobutton = Tkinter.Radiobutton(
                                    p56,
                                    text="Do not use experimental restraints",
                                    variable=self.p5_res_v,
                                    value=1,
                                    command=lambda: self.p5_res_choice(self.p5_res_v)
                                    )
        self.p5_empty_radiobutton.grid(row=1, column=0, columnspan=2, sticky="w")

        self.p5_fil_radiobutton = Tkinter.Radiobutton(
                                    p56,
                                    text="Use restraints file from hard drive",
                                    variable=self.p5_res_v,
                                    value=2,
                                    command=lambda: self.p5_res_choice(self.p5_res_v)
                                    )
        self.p5_fil_radiobutton.grid(row=2, column=0, columnspan=2, sticky="w")

        self.p5_res_entry = Pmw.EntryField(
                            p56,
                            labelpos="w",
                            label_text="Restraints file:",
                            entry_width=15,
                            entry_bg="white"
                            )
        self.p5_res_entry.grid(row=3, column=0, sticky="e")

        self.p5_res_button = Tkinter.Button(
                                p56,
                                text="Browse",
                                command=self.ranking_res_set
                                )
        self.p5_res_button.grid(row=3, column=1, sticky="w")

        self.p5_res_choice(self.p5_res_v)

        # SEQUENCES

        self.p57_frame = Tkinter.Frame(
                            self.page5,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.p57_frame.pack(fill="x")
        p57 = self.p57_frame

        self.p5_simseq_v = Tkinter.IntVar(p57)
        self.p5_simseq_v.set(1)

        self.p5_seq_gen_radiobutton = Tkinter.Radiobutton(
                                        p57,
                                        text="Generate sequences automatically",
                                        variable=self.p5_simseq_v,
                                        value=1,
                                        command=lambda: self.p5_seq_choice(self.p5_simseq_v)
                                        )
        self.p5_seq_gen_radiobutton.grid(row=1, column=0, columnspan=2, sticky="w")

        self.p5_seq_fil_radiobutton = Tkinter.Radiobutton(
                                        p57,
                                        text="Use sequence file from hard drive",
                                        variable=self.p5_simseq_v,
                                        value=2,
                                        command=lambda: self.p5_seq_choice(self.p5_simseq_v)
                                        )
        self.p5_seq_fil_radiobutton.grid(row=2, column=0, columnspan=2, sticky="w")

        self.p5_seq_entry = Pmw.EntryField(
                            p57,
                            labelpos="w",
                            label_text="Fasta file:",
                            entry_width=15,
                            entry_bg="white"
                            )
        self.p5_seq_entry.grid(row=3, column=0, sticky="e")

        self.p5_seq_button = Tkinter.Button(
                                p57,
                                text="Browse",
                                command=self.ranking_seq_set
                                )
        self.p5_seq_button.grid(row=3, column=1, sticky="w")

        self.p5_seq_text_radiobutton = Tkinter.Radiobutton(
                                        p57,
                                        text="Input sequences manually",
                                        variable=self.p5_simseq_v,
                                        value=3,
                                        command=lambda: self.p5_seq_choice(self.p5_simseq_v)
                                        )
        self.p5_seq_text_radiobutton.grid(row=4, column=0, columnspan=2, sticky="w")

        self.p5_seq_text_button = Tkinter.Button(
                                    p57,
                                    text="Input window...",
                                    command=self.display_text_sequence_window
                                    )
        self.p5_seq_text_button.grid(row=5, column=0, sticky="w")

        self.p5_seq_choice(self.p5_simseq_v)

        # MAP AND SORTING

        self.p58_frame = Tkinter.Frame(
                            self.page5,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.p58_frame.pack(fill="x")
        p58 = self.p58_frame

        self.p5_map_entry = Pmw.EntryField(
                            p58,
                            labelpos="w",
                            label_text="Map file:",
                            entry_width=15,
                            entry_bg="white",
                            entry_state="disabled",
                            label_state="disabled"
                            )
        self.p5_map_entry.grid(row=7, column=0, sticky="e")

        self.p5_map_button = Tkinter.Button(
                                p58,
                                text="Browse",
                                command=self.ranking_map_set
                                )
        self.p5_map_button.grid(row=7, column=1, sticky="w")

        self.p5_sort_menu = Pmw.OptionMenu(
                            p58,
                            labelpos="w",
                            label_text="Sort results by:",
                            initialitem="Overall score",
                            items=[
                                "Overall score", "Collisions",
                                "Restraints", "Outside box",
                                "Map empty space", "Density"
                                ]
                            )
        self.p5_sort_menu.grid(row=8, column=0, sticky="e")

        self.p52_frame = Tkinter.Frame(
                            self.page5,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.p52_frame.pack(fill="x")

        self.p5_runranking_button = Tkinter.Button(
                                    self.p52_frame,
                                    text="Create ranking",
                                    command=self.make_ranking
                                    )
        self.p5_runranking_button.pack(side="right")

        self.p5_cfg_choice(self.p5_cfg_v)

        # ----- ADDING NOTEBOOK'S SIXTH PAGE - CLUSTERING

        self.page6 = self.notebook.add("Clustering")

        # ----- ADDING SIXTH PAGE'S CONTENT

        self.p61_frame = Tkinter.Frame(
                            self.page6,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        self.p61_frame.pack(fill="x")
        p61 = self.p61_frame

        self.p6_input_entry = Pmw.EntryField(
                                p61,
                                labelpos="w",
                                label_text="Input directory:",
                                entry_width=15,
                                entry_bg="white"
                                )
        self.p6_input_entry.grid(row=0, column=0, sticky="e")

        self.p6_input_button = Tkinter.Button(
                                p61,
                                text="Browse",
                                command=self.clust_input_set
                                )
        self.p6_input_button.grid(row=0, column=1, sticky="w")

        self.p6_map_entry = Pmw.EntryField(
                            p61,
                            labelpos="w",
                            label_text="Map file:",
                            entry_width=15,
                            entry_bg="white"
                            )
        self.p6_map_entry.grid(row=1, column=0, sticky="e")

        self.p6_map_button = Tkinter.Button(
                                p61,
                                text="Browse",
                                command=self.clust_map_set
                                )
        self.p6_map_button.grid(row=1, column=1, sticky="w")

        self.p62_frame = Tkinter.Frame(
                            self.page6,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        p62 = self.p62_frame
        p62.pack(fill="x")

        self.p6_scoretype_menu = Pmw.OptionMenu(
                                    p62,
                                    labelpos="w",
                                    label_text="Score type:",
                                    initialitem="pyry3d",
                                    items=["ccc", "pyry3d"]
                                    )
        self.p6_scoretype_menu.grid(row=0, column=0, sticky="e")

        self.p6_measuretype_menu = Pmw.OptionMenu(
                                    p62,
                                    labelpos="w",
                                    label_text="Measure type:",
                                    initialitem="RMSD",
                                    items=["RMSD", "TM_Score", "GDT_TS"]
                                    )
        self.p6_measuretype_menu.grid(row=1, column=0, sticky="e")

        self.p6_representation_menu = Pmw.OptionMenu(
                                        p62,
                                        labelpos="w",
                                        label_text="Representation:",
                                        initialitem="fa",
                                        items=["fa", "ca", "sphere"]
                                        )
        self.p6_representation_menu.grid(row=2, column=0, sticky="e")

        self.p63_frame = Tkinter.Frame(
                            self.page6,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        p63 = self.p63_frame
        p63.pack(fill="x")

        self.p6_thresh_entry = Pmw.EntryField(
                                p63,
                                labelpos="w",
                                label_text="Density threshold:",
                                entry_width=15,
                                entry_bg="white",
                                validate={"validator": "real"}
                                )
        self.p6_thresh_entry.grid(row=0, column=0, sticky="e")

        self.p6_clusthresh_entry = Pmw.EntryField(
                                    p63,
                                    labelpos="w",
                                    label_text="Clustering threshold:",
                                    entry_width=15,
                                    entry_bg="white",
                                    validate={"validator": "real"}
                                    )
        self.p6_clusthresh_entry.grid(row=1, column=0, sticky="e")

        self.p6_numstruct_entry = Pmw.EntryField(
                                    p63,
                                    labelpos="w",
                                    label_text="Number of structures:",
                                    entry_width=15,
                                    entry_bg="white",
                                    validate={"validator": "real"}
                                    )
        self.p6_numstruct_entry.grid(row=2, column=0, sticky="e")

        self.p635_frame = Tkinter.Frame(
                            self.page6,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        p635 = self.p635_frame
        p635.pack(fill="x")

        self.oligos = Tkinter.IntVar()
        self.oligos.set(0)

        self.p6_clustoligos_checkbutton = Tkinter.Checkbutton(
                                            p635,
                                            text="Structures are oligomers",
                                            variable=self.oligos
                                            )
        self.p6_clustoligos_checkbutton.grid(row=0, column=0, sticky="w")

        self.clustsort = Tkinter.IntVar()
        self.clustsort.set(0)

        self.p6_clustsort_checkbutton = Tkinter.Checkbutton(
                                        p635,
                                        text="Sort results into different folders",
                                        variable=self.clustsort,
                                        command=self.check_clustsort
                                        )
        self.p6_clustsort_checkbutton.grid(row=1, column=0, sticky="w")

        self.p6_clustsort_entry = Pmw.EntryField(
                                    p635,
                                    labelpos="w",
                                    label_text="Sort clusters containing at least ",
                                    entry_width=5,
                                    entry_bg="white",
                                    validate={"validator": "real"}
                                    )
        self.p6_clustsort_entry.grid(row=2, column=0, sticky="w")

        self.p6_clustsort_label = Tkinter.Label(p635, text=" structures")
        self.p6_clustsort_label.grid(row=2, column=1, sticky="w")

        self.check_clustsort()

        self.p64_frame = Tkinter.Frame(
                            self.page6,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        p64 = self.p64_frame
        p64.pack(fill="x")

        self.p6_output_entry = Pmw.EntryField(
                                p64,
                                labelpos="w",
                                label_text="Output folder:",
                                entry_width=15,
                                entry_bg="white"
                                )
        self.p6_output_entry.grid(row=0, column=0, sticky="e")

        self.p6_out_button = Tkinter.Button(
                                p64,
                                text="Browse",
                                command=self.clust_out_set
                                )
        self.p6_out_button.grid(row=0, column=1, sticky="w")

        self.p65_frame = Tkinter.Frame(
                            self.page6,
                            bd=1, relief="ridge",
                            pady=3, padx=3
                            )
        p65 = self.p65_frame
        p65.pack(fill="x")

        self.p6_start_button = Tkinter.Button(
                                p65,
                                text="Start clustering",
                                command=self.start_clustering
                                )
        self.p6_start_button.pack(side="right")

        self.notebook.tab(0).configure(state="normal")
        self.notebook.tab(1).configure(state="disabled")
        self.notebook.tab(2).configure(state="disabled")
        self.notebook.tab(3).configure(state="normal")
        self.notebook.tab(4).configure(state="normal")
        self.notebook.tab(5).configure(state="normal")

        self.notebook.setnaturalsize()

        # ----- F U N C T I O N S

    def rank_cfg_set(self):
        pass

    def start_clustering(self):
        try:
            self.update_status("blue", "PLEASE WAIT. CLUSTERING IN PROGRESS...")
            infolder = self.p6_input_entry.getvalue()
            score_type = self.p6_scoretype_menu.getvalue()
            density_map = self.p6_map_entry.getvalue()
            density_map_threshold = self.p6_thresh_entry.getvalue()
            measure = self.p6_measuretype_menu.getvalue()
            threshold = self.p6_clusthresh_entry.getvalue()
            struct_nr = self.p6_numstruct_entry.getvalue()
            representation = self.p6_representation_menu.getvalue()
            output = self.p6_output_entry.getvalue()

            if self.oligos.get() == 1:
                oligomers = "oligo"
            else:
                oligomers = None

            if self.clustsort.get() == 1:
                sort_num = int(self.p6_clustsort_entry.getvalue())
            else:
                sort_num = None

            start_clustering(
                    infolder, score_type, density_map,
                    density_map_threshold, measure, threshold,
                    struct_nr, representation, output,
                    oligomers, sort_num
                    )
            self.update_status("lime green", "Ready")

            tkMessageBox.showinfo(
                    "Success",
                    "Clustering results files can be found in " + output
                    )

        except Exception as e:
            tkMessageBox.showwarning("Error", e)
            self.update_status("lime green", "Ready")

    def ranking_inp_choose(self):
        if self.rank_fc_v.get() == 0:
            self.p5_map_entry.configure(
                entry_state="disabled",
                label_state="disabled"
                )
            self.p5_input_entry.configure(
                entry_state="disabled",
                label_state="disabled"
                )
            self.p5_map_button.configure(state="disabled")
            self.p5_input_button.configure(state="disabled")
            self.p5_seq_gen_radiobutton.configure(state="normal")

        if self.rank_fc_v.get() == 1:
            self.p5_map_entry.configure(
                entry_state="normal",
                label_state="normal"
                )
            self.p5_input_entry.configure(
                entry_state="normal",
                label_state="normal"
                )
            self.p5_map_button.configure(state="normal")
            self.p5_input_button.configure(state="normal")
            self.p5_seq_gen_radiobutton.configure(state="disabled")
            self.p5_simseq_v.set(2)
            self.p5_seq_choice(self.simseq_v)
            self.p5_seq_entry.configure(
                label_state="normal",
                entry_state="normal"
                )
            self.p5_seq_button.configure(state="normal")

    def update_status(self, c, t):
        self.StatusLabel.configure(text=t, fg=c)

    def clust_input_set(self):
        path = tkFileDialog.askdirectory(
                parent=self.page5,
                initialdir=self.initialdir,
                title="Choose input folder"
                )
        self.p6_input_entry.setvalue(path)
        self.save_path(path)

    def clust_map_set(self):
        path = tkFileDialog.askopenfilename(
                parent=self.page5,
                initialdir=self.initialdir,
                title="Choose density map file"
                )
        self.p6_map_entry.setvalue(path)
        self.save_path(path)

    def clust_out_set(self):
        path = tkFileDialog.askdirectory(
            parent=self.page5,
            initialdir=self.initialdir,
            title="Choose output folder"
            )
        self.p6_output_entry.setvalue(path)
        self.save_path(path)

    def ranking_input_set(self):
        path = tkFileDialog.askdirectory(
                parent=self.page5,
                initialdir=self.initialdir,
                title="Choose input folder"
                )
        self.p5_input_entry.setvalue(path)
        self.save_path(path)

    def ranking_seq_set(self):
        path = tkFileDialog.askopenfilename(
                parent=self.page5,
                initialdir=self.initialdir,
                title="Choose sequences file"
                )
        self.p5_seq_entry.setvalue(path)
        self.save_path(path)

    def ranking_cfg_set(self):
        path = tkFileDialog.askopenfilename(
                parent=self.page5,
                initialdir=self.initialdir,
                title="Choose config file"
                )
        self.p5_cfg_entry.setvalue(path)
        self.save_path(path)

    def ranking_res_set(self):
        path = tkFileDialog.askopenfilename(
                parent=self.page5,
                initialdir=self.initialdir,
                title="Choose restraints file"
                )
        self.p5_res_entry.setvalue(path)
        self.save_path(path)

    def ranking_map_set(self):
        path = tkFileDialog.askopenfilename(
                parent=self.page5,
                initialdir=self.initialdir,
                title="Choose density map file"
                )
        self.p5_map_entry.setvalue(path)
        self.save_path(path)

    def check_clustsort(self):
        if self.clustsort.get() == 0:
            self.p6_clustsort_entry.configure(label_state="disabled")
            self.p6_clustsort_entry.configure(entry_state="disabled")
            self.p6_clustsort_label.configure(state="disabled")
        else:
            self.p6_clustsort_entry.configure(label_state="normal")
            self.p6_clustsort_entry.configure(entry_state="normal")
            self.p6_clustsort_label.configure(state="normal")

    def handler_main_window(self):
        pass

    def handler_parameters(self):
        pass

    def handler_path(self):
        self.p3dpd.withdraw()

    def choosecomp(self):
        if self.complist == []:
            self.complist = P1F.choosestruct(self.initialdir)
        else:
            newcomponents = P1F.choosestruct(self.initialdir)
            for i in newcomponents:
                self.complist.append(i)
        u = 1
        labeltext = ""
        for i in self.complist:
            sname = i.split("/")[-1]
            if u == 1:
                labeltext = labeltext+"#"+str(u)+" "+sname
            else:
                labeltext = labeltext+"\n#"+str(u)+" "+sname
            u = u+1
        self.struli.settext(labeltext)
        if self.complist != []:
            last_directory = "/".join(self.complist[-1].split("/")[:-1])
            self.save_path(last_directory)

    def choosemap(self):
        Paths.mappath = P1F.choosemap(self.mapli, self.initialdir)
        if Paths.mappath == ():
            Paths.mappath = ""
        last_directory = "/".join(Paths.mappath.split("/")[:-1])
        self.save_path(last_directory)

    def clear(self):
        P1F.clearlist(self.struli)
        P1F.clearlist(self.mapli)
        self.complist = []
        Paths.mappath = ""

    def new_session(self):
        rly = tkMessageBox.askyesno(
                "Warning",
                "This will close all opened models. Continue?"
                )
        if rly is True:
            self.clear()
            self.clear_button.configure(state="normal")
            self.open_button.configure(state="normal")
            self.dens_button.configure(state="normal")
            self.comp_button.configure(state="normal")
            self.new_session_button.configure("disabled")
            chimera.runCommand("close all")

    def openandsaveall(self):
        if len(self.complist) <= 1:
            tkMessageBox.showinfo(
                "PyRy3D info",
                "You must add at least two structures."
                )
        else:
            rly1 = True
            if Paths.mappath == "" or Paths.mappath == ():
                rly1 = tkMessageBox.askyesno(
                        "Warning",
                        "No shape descriptor provided. Continue?"
                        )

            if rly1 is True:
                rly2 = tkMessageBox.askyesno(
                        "Warning",
                        "This will close all opened models before loading new data. Continue?"
                        )
                if rly2 is True:
                    runCommand("close all")
                    P1F.opencommand(Paths.mappath, self.complist)
                    P1F.writeAllPDBs(Paths.temppath, Paths.mappath)
                    runCommand("windowsize 9999 9999")
                    self.open_button.configure(state="disabled")
                    self.dens_button.configure(state="disabled")
                    self.comp_button.configure(state="disabled")
                    self.clear_button.configure(state="disabled")
                    self.new_session_button.configure(state="normal")
                    self.notebook.tab(1).configure(state="normal")
                    self.notebook.tab(2).configure(state="normal")
                    self.notebook.tab(3).configure(state="normal")
                    self.notebook.tab(3).configure(state="normal")

    # ----- FUNCTIONS TRIGGERED BY WIDGETS ON THE --- SECOND PAGE ---

    def ss_choose_cfg(self):
        Paths.configpath = P3F.ig_choose_resfile(
                            self.page3,
                            self.ss_cfg_fil_entry
                            )

    def ss_choose_resfile(self):
        Paths.ig_respath = P3F.ig_choose_resfile(
                            self.page3,
                            self.res_fil_entry
                            )

    def ss_choose_seqfile(self):
        Paths.user_seqpath = P3F.ig_choose_resfile(
                                self.page2,
                                self.seq_fil_entry
                                )

    def ss_choose_outdir(self):
        Paths.ss_outpath = P3F.ig_choose_output_folder(
                            self.page3,
                            self.outdir_entry
                            )
        if Paths.ss_outpath != "":
            rly = tkMessageBox.askyesno(
                    "Warning",
                    "All files in "+Paths.ss_outpath+" will be deleted. Continue?"
                     )
            if rly is True:
                self.autoscore_button.configure(state="normal")
                self.simulation_button.configure(state="normal")
            else:
                self.outdir_entry.configure(entry_state="normal")
                self.autoscore_button.configure(state="disabled")
                self.simulation_button.configure(state="disabled")
                Paths.ss_outpath = ""
        else:
            self.outdir_entry.configure(entry_state="normal")
            Paths.ss_outpath = ""
            self.autoscore_button.configure(state="disabled")
            self.simulation_button.configure(state="disabled")

    def cfg_choice(self,variable):
        if variable.get() == 1:
            self.ss_cfg_fil_button.configure(state="disabled")
            self.ss_cfg_fil_entry.configure(
                        label_state="disabled",
                        entry_state="disabled"
                        )
            self.ss_params_button.configure(state="normal")
        if variable.get() == 2:
            self.ss_cfg_fil_button.configure(state="normal")
            self.ss_cfg_fil_entry.configure(
                        label_state="normal",
                        entry_state="normal"
                        )
            self.ss_params_button.configure(state="disabled")

    def p5_cfg_choice(self, variable):
        if variable.get() == 1:
            self.p5_cfg_button.configure(state="disabled")
            self.p5_cfg_entry.configure(
                        label_state="disabled",
                        entry_state="disabled"
                        )
            self.p5_params_button.configure(state="normal")
        if variable.get() == 2:
            self.p5_cfg_button.configure(state="normal")
            self.p5_cfg_entry.configure(
                        label_state="normal",
                        entry_state="normal"
                        )
            self.p5_params_button.configure(state="disabled")

    def seq_choice(self, variable):
        if variable.get() == 1:
            self.seq_fil_entry.configure(
                        label_state="disabled",
                        entry_state="disabled"
                        )
            self.seq_fil_button.configure(state="disabled")
            self.seq_text_button.configure(state="disabled")
        if variable.get() == 2:
            self.seq_fil_entry.configure(
                        label_state="normal",
                        entry_state="normal"
                        )
            self.seq_fil_button.configure(state="normal")
            self.seq_text_button.configure(state="disabled")
        if variable.get() == 3:
            self.seq_fil_entry.configure(
                        label_state="disabled",
                        entry_state="disabled"
                        )
            self.seq_fil_button.configure(state="disabled")
            self.seq_text_button.configure(state="normal")

    def p5_seq_choice(self, variable):
        if variable.get() == 1:
            self.p5_seq_entry.configure(
                        label_state="disabled",
                        entry_state="disabled"
                        )
            self.p5_seq_button.configure(state="disabled")
            self.p5_seq_text_button.configure(state="disabled")
        if variable.get() == 2:
            self.p5_seq_entry.configure(
                        label_state="normal",
                        entry_state="normal"
                        )
            self.p5_seq_button.configure(state="normal")
            self.p5_seq_text_button.configure(state="disabled")
        if variable.get() == 3:
                self.p5_seq_entry.configure(
                            label_state="disabled",
                            entry_state="disabled"
                            )
                self.p5_seq_button.configure(state="disabled")
                self.p5_seq_text_button.configure(state="normal")

    def res_choice(self, variable):
        if variable.get() == 1:
            self.res_fil_entry.configure(
                        label_state="disabled",
                        entry_state="disabled"
                        )
            self.res_fil_button.configure(state="disabled")
            Paths.ig_respath = None
        if variable.get() == 2:
            self.res_fil_entry.configure(
                        label_state="normal",
                        entry_state="normal"
                        )
            self.res_fil_button.configure(state="normal")

    def p5_res_choice(self, variable):
        if variable.get() == 1:
            self.p5_res_entry.configure(
                        label_state="disabled",
                        entry_state="disabled"
                        )
            self.p5_res_button.configure(state="disabled")
        if variable.get() == 2:
            self.p5_res_entry.configure(
                        label_state="normal",
                        entry_state="normal"
                        )
            self.p5_res_button.configure(state="normal")

    def set_user_seq(self):
        Paths.user_seqpath = P3F.ig_choose_resfile(
                                self.dis_ask_seq,
                                self.useq_entry
                                )

    def calc_threshold(self, no_out=0, elapsed="0.0"):
        """
        Calculates density map threshold based on the volume
        of displayed structures.
        """
        try:
            # deactivate GUI elements for the time of calculations
            self.update_status("blue", "PLEASE WAIT. CALCULATING THRESHOLD...")
            self.notebook.tab(0).configure(state="disabled")
            self.notebook.tab(1).configure(state="disabled")
            self.notebook.tab(2).configure(state="disabled")
            self.notebook.tab(3).configure(state="disabled")
            self.notebook.tab(4).configure(state="disabled")
            self.notebook.tab(5).configure(state="disabled")
            self.autoscore_button.configure(state="disabled")
            self.simulation_button.configure(state="disabled")
            self.threshold_button.configure(state="disabled")

            # remove outfolder?? wtf?
            if os.path.exists(Paths.simscoreinputpath):
                shutil.rmtree(Paths.simscoreinputpath)

            WS.draw_box_grid = 1

            if not os.path.exists(Paths.simscoreinputpath):
                os.makedirs(Paths.simscoreinputpath)

            ld = Log_Diagram()
            P1F.writeAllPDBs(Paths.temppath, Paths.mappath)

            sequence_file = Paths.simscoreinputpath+"/sequences.fasta"

            le_config_file = Paths.simscoreinputpath+"/config.txt"

            if Paths.mappath != "":
                    if Paths.mappath[-3:] == "pdb" \
                     or Paths.mappath[-3:] == "PDB":
                        saxs_file_path = Paths.simscoreinputpath + "/" +\
                                            Paths.mappath.split("/")[-1]
                        map_file_path = None
                    else:
                        map_file_path = Paths.simscoreinputpath + "/" +\
                                            Paths.mappath.split("/")[-1]
                        saxs_file_path = None
            else:
                map_file_path = ""
                saxs_file_path = None

            P3F.generate_input_files(
                    Paths.simscoreinputpath,
                    Paths.temppath,
                    Paths.ig_respath,
                    Paths.mappath,
                    1, 1, 0, 1, 1,
                    nowindow=1
                    )

            restraints_path = None

            history_path = "history.txt"
            fullatom = "full.pdb"

            if no_out == 0:
                opath = Paths.ss_outpath

            if no_out == 1:
                if not os.path.exists(Paths.temp_out_path):
                    os.makedirs(Paths.temp_out_path)
                opath = Paths.temp_out_path

            opath = Paths.pluginpath+"/threshold_temp"

            calculated_threshold = calculate_threshold(
                                    WS.draw_box_grid,
                                    "evaluate",
                                    Paths.simscoreinputpath+"/input.tar",
                                    map_file_path,
                                    restraints_path,
                                    sequence_file,
                                    le_config_file,
                                    opath,
                                    history_path=history_path,
                                    fullatom=fullatom,
                                    sax_path=saxs_file_path,
                                    last_elapsed=elapsed
                                    )

            tkMessageBox.showinfo(
                        "Threshold calculated",
                        "Density threshold's value for complex's volume is: " +
                        str(calculated_threshold)
                        )

            shutil.rmtree(Paths.pluginpath+"/threshold_temp")

            self.threshold_button.configure(state="normal")
            self.update_status("lime green", "READY.")
            self.notebook.tab(0).configure(state="normal")
            self.notebook.tab(1).configure(state="normal")
            self.notebook.tab(2).configure(state="normal")
            self.notebook.tab(3).configure(state="normal")
            self.notebook.tab(4).configure(state="normal")
            self.notebook.tab(5).configure(state="normal")
            self.autoscore_button.configure(state="normal")
            self.simulation_button.configure(state="normal")
            self.threshold_button.configure(state="normal")

        except Exception as e:
            tkMessageBox.showwarning("Error", e)
            self.update_status("lime green", "READY.")
            self.notebook.tab(0).configure(state="normal")
            self.notebook.tab(1).configure(state="normal")
            self.notebook.tab(2).configure(state="normal")
            self.notebook.tab(3).configure(state="normal")
            self.notebook.tab(4).configure(state="normal")
            self.notebook.tab(5).configure(state="normal")
            self.autoscore_button.configure(state="normal")
            self.simulation_button.configure(state="normal")
            self.threshold_button.configure(state="normal")

    def score_complex(self, no_out=0, elapsed="0.0", smode=None):
            if Paths.ss_outpath == "":
                tkMessageBox.showwarning(
                        "Error",
                        "Please specify the output directory."
                        )
            else:
                if os.path.exists(Paths.simscoreinputpath):
                    shutil.rmtree(Paths.simscoreinputpath)

            WS.draw_box_grid = 1

            self.update_status(
                    "blue",
                    "PLEASE WAIT. EVALUATION IN PROGRESS..."
                    )
            self.notebook.tab(0).configure(state="disabled")
            self.notebook.tab(1).configure(state="disabled")
            self.notebook.tab(2).configure(state="disabled")
            self.notebook.tab(3).configure(state="disabled")
            self.notebook.tab(4).configure(state="disabled")
            self.notebook.tab(5).configure(state="disabled")
            self.autoscore_button.configure(state="disabled")
            self.simulation_button.configure(state="disabled")
            self.threshold_button.configure(state="disabled")

            if not os.path.exists(Paths.simscoreinputpath):
                os.makedirs(Paths.simscoreinputpath)

            try:
                ld = Log_Diagram()
                P1F.writeAllPDBs(Paths.temppath, Paths.mappath)

                if self.simseq_v.get() == 1 or smode == "reopened":
                    print "REOPENED"
                    sequence_file = Paths.simscoreinputpath+"/sequences.fasta"
                elif self.simseq_v.get() == 2:
                    sequence_file = Paths.user_seqpath
                elif self.simseq_v.get() == 3:
                    raw_sequence = self.seq_text_li.getvalue()
                    sequence_file = Paths.ss_outpath+"/sequences_inp.fasta"
                    sf = open(sequence_file, "w")
                    sf.write(raw_sequence)
                    sf.close()

                if self.cfg_v.get() == 2:
                    le_config_file = self.ss_cfg_fil_entry.getvalue()
                else:
                    le_config_file = Paths.simscoreinputpath+"/config.txt"

                if Paths.mappath != "":
                        if Paths.mappath[-3:] == "pdb" or Paths.mappath[-3:] == "PDB":
                            saxs_file_path = Paths.simscoreinputpath+"/"+Paths.mappath.split("/")[-1]
                            map_file_path = None
                        else:
                            map_file_path = Paths.simscoreinputpath+"/"+Paths.mappath.split("/")[-1]
                            saxs_file_path = None
                else:
                    map_file_path = ""
                    saxs_file_path = None

                if Paths.ig_respath is not None:
                    P3F.generate_input_files(
                            Paths.simscoreinputpath,
                            Paths.temppath,
                            Paths.ig_respath,
                            Paths.mappath,
                            1, 1, 1, 1, 1,
                            nowindow=1
                            )
                    restraints_path = Paths.simscoreinputpath+"/restraints.txt"
                else:
                    P3F.generate_input_files(
                            Paths.simscoreinputpath,
                            Paths.temppath,
                            Paths.ig_respath,
                            Paths.mappath,
                            1, 1, 0, 1, 1,
                            nowindow=1
                            )
                    restraints_path = None

                history_path = "history.txt"
                fullatom = "full.pdb"

                if no_out == 0:
                    opath = Paths.ss_outpath

                if no_out == 1:
                    if not os.path.exists(Paths.temp_out_path):
                        os.makedirs(Paths.temp_out_path)
                        opath = Paths.temp_out_path

                if map_file_path == "" and restraints_path is None:
                    tkMessageBox.showinfo(
                            "PyRy3D info",
                            "You need either a shape descriptor or some distance restraints."
                            )
                else:
                    resultdir, logfile = run(
                                            WS.draw_box_grid,
                                            "evaluate",
                                            Paths.simscoreinputpath+"/input.tar",
                                            map_file_path,
                                            restraints_path,
                                            sequence_file,
                                            le_config_file,
                                            opath,
                                            history_path=history_path,
                                            fullatom=fullatom,
                                            sax_path=saxs_file_path,
                                            last_elapsed=elapsed
                                            )

                if os.path.exists(Paths.temp_out_path):
                    shutil.rmtree(Paths.temp_out_path)

                self.update_status("lime green", "READY.")
                self.notebook.tab(0).configure(state="normal")
                self.notebook.tab(1).configure(state="normal")
                self.notebook.tab(2).configure(state="normal")
                self.notebook.tab(3).configure(state="normal")
                self.notebook.tab(4).configure(state="normal")
                self.notebook.tab(5).configure(state="normal")
                self.autoscore_button.configure(state="normal")
                self.simulation_button.configure(state="normal")
                self.threshold_button.configure(state="normal")

            except InputError as e:
                tkMessageBox.showwarning("Input error", e)

                self.update_status("lime green", "READY.")
                self.notebook.tab(0).configure(state="normal")
                self.notebook.tab(1).configure(state="normal")
                self.notebook.tab(2).configure(state="normal")
                self.notebook.tab(3).configure(state="normal")
                self.notebook.tab(4).configure(state="normal")
                self.notebook.tab(5).configure(state="normal")
                self.autoscore_button.configure(state="normal")
                self.simulation_button.configure(state="normal")
                self.threshold_button.configure(state="normal")

            except ConfigError as e:
                tkMessageBox.showwarning("Config error", e)

                self.update_status("lime green", "READY.")
                self.notebook.tab(0).configure(state="normal")
                self.notebook.tab(1).configure(state="normal")
                self.notebook.tab(2).configure(state="normal")
                self.notebook.tab(3).configure(state="normal")
                self.notebook.tab(4).configure(state="normal")
                self.notebook.tab(5).configure(state="normal")
                self.autoscore_button.configure(state="normal")
                self.simulation_button.configure(state="normal")
                self.threshold_button.configure(state="normal")

            except Exception as e:
                tkMessageBox.showwarning("Error", e)

                self.update_status("lime green","READY.")
                self.notebook.tab(0).configure(state="normal")
                self.notebook.tab(1).configure(state="normal")
                self.notebook.tab(2).configure(state="normal")
                self.notebook.tab(3).configure(state="normal")
                self.notebook.tab(4).configure(state="normal")
                self.notebook.tab(5).configure(state="normal")
                self.autoscore_button.configure(state="normal")
                self.simulation_button.configure(state="normal")
                self.threshold_button.configure(state="normal")

    def simulate_complex_fin(self):

        if Paths.ss_outpath == "":
            tkMessageBox.showwarning("Error", "Please specify the output directory.")
        else:
            if os.path.exists(Paths.simscoreinputpath):
                shutil.rmtree(Paths.simscoreinputpath)

            self.update_status("blue", "PLEASE WAIT. SIMULATION IN PROGRESS...")
            self.notebook.tab(0).configure(state="disabled")
            self.notebook.tab(1).configure(state="disabled")
            self.notebook.tab(2).configure(state="disabled")
            self.notebook.tab(3).configure(state="disabled")
            self.notebook.tab(4).configure(state="disabled")
            self.notebook.tab(5).configure(state="disabled")
            self.autoscore_button.configure(state="disabled")
            self.simulation_button.configure(state="disabled")
            self.threshold_button.configure(state="disabled")

            from Calculate import run
            from Draw_Plot import Log_Diagram
            from Modules.Error.Errors import InputError, ConfigError
            ld = Log_Diagram()
            P1F.writeAllPDBs(Paths.temppath, Paths.mappath)

            try:

                if not os.path.exists(Paths.simscoreinputpath):
                    os.makedirs(Paths.simscoreinputpath)

                fullatomm = "full.pdb"
                history_path = "history.txt"
                trafl = "traject.trafl"

                if self.simseq_v.get() == 1:
                    sequence_file = Paths.simscoreinputpath+"/sequences.fasta"
                if self.simseq_v.get() == 2:
                    sequence_file = Paths.user_seqpath
                if self.simseq_v.get() == 3:
                    raw_sequence = self.seq_text_li.getvalue()
                    sequence_file = Paths.ss_outpath+"/sequences_inp.fasta"
                    sf = open(sequence_file, "w")  # rrr
                    sf.write(raw_sequence)
                    sf.close()
                if self.cfg_v.get() == 2:
                    le_config_file = self.ss_cfg_fil_entry.getvalue()
                else:
                    le_config_file = Paths.simscoreinputpath+"/config.txt"

                WS.draw_box_grid = 1

                if Paths.mappath != "":
                        if Paths.mappath[-3:] == "pdb" or Paths.mappath[-3:] == "PDB":
                            saxs_file_path = Paths.simscoreinputpath+"/"+Paths.mappath.split("/")[-1]
                            map_file_path = None
                        else:
                            map_file_path = Paths.simscoreinputpath+"/"+Paths.mappath.split("/")[-1]
                            saxs_file_path = None
                else:
                    map_file_path = ""
                    saxs_file_path = None

                map_filename = Paths.mappath.split("/")[-1]
                if Paths.ig_respath is not None:
                    P3F.generate_input_files(Paths.simscoreinputpath, Paths.temppath, Paths.ig_respath, Paths.mappath,1,1,1,1,1,nowindow=1)
                    restraints_path = Paths.simscoreinputpath+"/restraints.txt"
                else:
                    P3F.generate_input_files(Paths.simscoreinputpath, Paths.temppath, Paths.ig_respath, Paths.mappath,1,1,0,1,1,nowindow=1)
                    restraints_path = None
                history_path = "history.txt"
                fullatom = "full.pdb"

                if Paths.mappath == "" and Paths.ig_respath == "":
                    tkMessageBox.showinfo("PyRy3D info", "You need either a shape descriptor or some distance restraints.")
                else:
                    resultdir, logfile, elapsed = run(WS.draw_box_grid, "simulate", Paths.simscoreinputpath+"/input.tar",
                                  map_file_path, restraints_path,
                                  sequence_file, le_config_file,
                                  Paths.ss_outpath, history_path=history_path, fullatom=fullatom, sax_path=saxs_file_path)

                    if fullatomm is not None:
                        self.reopen_after_sim(elapsed=elapsed)

                    if os.path.exists(Paths.temp_out_path):
                        shutil.rmtree(Paths.temp_out_path)

                self.update_status("lime green", "READY.")
                self.notebook.tab(0).configure(state="normal")
                self.notebook.tab(1).configure(state="normal")
                self.notebook.tab(2).configure(state="normal")
                self.notebook.tab(3).configure(state="normal")
                self.notebook.tab(4).configure(state="normal")
                self.notebook.tab(5).configure(state="normal")
                self.autoscore_button.configure(state="normal")
                self.simulation_button.configure(state="normal")
                self.threshold_button.configure(state="normal")

                ld.draw_diagram(logfile)

            except InputError as e:
                tkMessageBox.showwarning("Input error", e)

                self.update_status("lime green","READY.")
                self.notebook.tab(0).configure(state="normal")
                self.notebook.tab(1).configure(state="normal")
                self.notebook.tab(2).configure(state="normal")
                self.notebook.tab(3).configure(state="normal")
                self.notebook.tab(4).configure(state="normal")
                self.notebook.tab(5).configure(state="normal")
                self.autoscore_button.configure(state="normal")
                self.simulation_button.configure(state="normal")
                self.threshold_button.configure(state="normal")

            except ConfigError as e:
                tkMessageBox.showwarning("Config error", e)

                self.update_status("lime green", "READY.")
                self.notebook.tab(0).configure(state="normal")
                self.notebook.tab(1).configure(state="normal")
                self.notebook.tab(2).configure(state="normal")
                self.notebook.tab(3).configure(state="normal")
                self.notebook.tab(4).configure(state="normal")
                self.notebook.tab(5).configure(state="normal")
                self.autoscore_button.configure(state="normal")
                self.simulation_button.configure(state="normal")
                self.threshold_button.configure(state="normal")

            except Exception as e:
                tkMessageBox.showwarning("Error", e)

                self.update_status("lime green", "READY.")
                self.notebook.tab(0).configure(state="normal")
                self.notebook.tab(1).configure(state="normal")
                self.notebook.tab(2).configure(state="normal")
                self.notebook.tab(3).configure(state="normal")
                self.notebook.tab(4).configure(state="normal")
                self.notebook.tab(5).configure(state="normal")
                self.autoscore_button.configure(state="normal")
                self.simulation_button.configure(state="normal")
                self.threshold_button.configure(state="normal")

    def reopen_after_sim(self, elapsed):
        runCommand("close all")
        if Paths.mappath != "":
            runCommand("open "+Paths.mappath)
        direct_dirname = Paths.ss_outpath.split("/")[-1]
        outfiles = os.listdir(Paths.ss_outpath)
        minsc = -999999999999.99
        minfname = ""
        for o in outfiles:
            print o
            if len(o.split("_")) > 1:
                sc = float(o.split("_")[1])
                if sc != 0.0:
                    if sc > minsc:
                        print sc
                        minsc = sc
                        minfname = o

        runCommand("open "+Paths.ss_outpath+"/"+minfname)
        if Paths.mappath != "":
            str_n = "1"
        else:
            str_n = "0"
        runCommand("split #"+str_n)

        P1F.writeAllPDBs(Paths.temppath, Paths.mappath)
        runCommand("close #"+str_n)
        new_structs = os.listdir(Paths.temppath)
        for i in new_structs:
            runCommand("open "+Paths.temppath+"/"+i)
        self.score_complex(no_out=1, elapsed=elapsed, smode="reopened")

    def prepare_ranking_from_window(self):

        outp = Paths.pluginpath+"/ranking_temp_input"
        outpf = Paths.pluginpath+"/ready"

        if not os.path.exists(outp):
                os.makedirs(outp)
        else:
            shutil.rmtree(outp)
            os.makedirs(outp)

        if not os.path.exists(outpf):
            os.makedirs(outpf)
            os.makedirs(outpf+"/packs")
        else:
            shutil.rmtree(outpf)
            os.makedirs(outpf)
            os.makedirs(outpf+"/packs")

        self.update_status("blue", "PLEASE WAIT. RANKING COMPLEXES...")

        count = len(chimera.openModels.list()) - 1

        chimera.runCommand("split")

        count2 = len(chimera.openModels.list()) - 1

        cps = count2 / count

        o = chimera.openModels.list()[1:]

        for i in xrange(0, len(o), cps):
            m = o[i:i+cps]

            for j in m:
                id_ = j.oslIdent()[1:]
                command = "write "+id_ + " "+outp+"/"+id_+".pdb"
                runCommand(command)

            name = j.name.split(".")[0]

            P3F.generate_input_files(outpf, outp, "", Paths.mappath, 1,1,0,1,1, nowindow=1, rankmode=1, rankname=name)

            files = glob.glob(outp+"/*")
            for f in files:
                os.remove(f)

            files = glob.glob(outpf+"/*.pdb")
            for f in files:
                os.remove(f)

    def make_ranking(self):
        try:
            if self.p5_cfg_v.get() == 1:
                cfg_choice = 1
            if self.p5_simseq_v.get() == 1:
                seq_choice = 1
            if self.p5_res_v.get() == 1:
                res_choice = 1

            self.p5_runranking_button.configure(state="disabled")

            self.update_status("blue", "PLEASE WAIT. GENERATING RANKING...")

            from Cx_Ranking import run_king  # it hurts

            outpf = Paths.pluginpath+"/ready"
            outp = Paths.pluginpath+"/ranking_temp_input"

            if self.rank_fc_v.get() == 0:
                self.prepare_ranking_from_window()
                outpfp = outpf+"/packs"

            if self.p5_cfg_v.get() == 1:
                P3F.generate_input_files(outpf,outp,"",Paths.mappath,1,0,0,0,0,nowindow=1)
                rank_cfg = outpf+"/config.txt"
            else:
                rank_cfg = self.p5_cfg_entry.get()

            if self.p5_simseq_v.get() == 1:
                rank_seq = outpf+"/sequences.fasta"
            elif self.p5_simseq_v.get() == 2:
                rank_seq = self.p5_seq_entry.get()
            elif self.p5_simseq_v.get() == 3:
                raw_sequence = self.seq_text_li.getvalue()
                rank_seq = outpf+"/sequences_inp.fasta"
                sf = open(rank_seq, "w")
                sf.write(raw_sequence)
                sf.close()

            if self.p5_res_v.get() == 1:
                rank_res = ""
            else:
                rank_res = self.p5_res_entry.get()

            if self.rank_fc_v.get() == 0:
                rank_input = outpfp
                rank_map = Paths.mappath
                # rank_seq = outpf+"/sequences.fasta"
            else:
                rank_input = self.p5_input_entry.get()
                rank_map = self.p5_map_entry.get()
                rank_seq = self.p5_seq_entry.get()

            if_rank_res = True

            if rank_input == "" or rank_seq == "" or rank_cfg == "":
                tkMessageBox.showwarning("Error",
                                         "Please provide paths for your structures, sequences and a configuration file.")
            else:
                if rank_res == "":
                    rank_res = None
                    if_rank_res = tkMessageBox.askyesno("Warning", "You didn't provide restraints file. Continue without spatial restraints?")
                if if_rank_res == True:
                    run_king(self.p5_sort_menu.getvalue(),rank_input,rank_seq,rank_res,rank_map,rank_cfg,Paths.pluginpath+"/ranking")

            files = glob.glob(outpf+"/*")
            for f in files:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)

            self.p5_runranking_button.configure(state="normal")
            self.update_status("lime green", "READY.")

            self.p5_runranking_button.configure(state="normal")

        except Exception as e:
            tkMessageBox.showwarning("Error", e)

    def ig_check_elements(self,str_v,map_v,seq_v):
        if str_v.get()==1:
            WS.ig_structures=1
        if str_v.get()==0:
            WS.ig_structures=0
        if map_v.get()==1:
            WS.ig_map=1
        if map_v.get()==0:
            WS.ig_map=0
        if seq_v.get()==1:
            WS.ig_structures=1
            str_v.set(1)
            WS.ig_sequences=1
        if seq_v.get()==0:
            WS.ig_sequences=0

    def ig_check_res(self, variable):
        if variable.get()==1:
            self.ig_res_entry.configure(label_state="normal",entry_state="normal")
            self.ig_res_button.configure(state="normal")
            WS.ig_restraints=1
        if variable.get()==0:
            self.ig_res_entry.configure(label_state="disabled",entry_state="disabled")
            self.ig_res_button.configure(state="disabled")
            WS.ig_restraints=0
            
    def ig_check_con(self,variable):
        if variable.get()==1:
            self.ig_con_button.configure(state="normal")
            WS.ig_config=1
        if variable.get()==0:
            self.ig_con_button.configure(state="disabled")
            WS.ig_config=0
            
        
    def display_psrwin(self):
        self.psrwin.deiconify()
    
    def display_text_sequence_window(self):
        self.seq_text_win.deiconify()   
    
        
    def set_default_scaling_parameters(self):
        self.psr01_entry.setvalue("0")
        self.psr02_entry.setvalue("25")
        self.psr03_entry.setvalue("50")
        self.psr11_entry.setvalue("50")
        self.psr12_entry.setvalue("100")
        self.psr21_entry.setvalue("25")
        self.psr22_entry.setvalue("50")
        self.psr31_entry.setvalue("0")
        self.psr32_entry.setvalue("25")
    
    #----- FUNCTIONS TRIGGERED BY WIDGETS ON THE --- FOURTH PAGE ---
    #----- FUNCTIONS TRIGGERED BY WIDGETS ON THE --- FIFTH PAGE ---
    



chimera.dialogs.register(PyRyDialog.name, PyRyDialog)

dir, file = os.path.split(__file__)
icon = os.path.join(dir, 'ExtensionUI.tiff')
chimera.tkgui.app.toolbar.add(icon, lambda d=chimera.dialogs.display, n=PyRyDialog.name: d(n), 'PyRy3D Extension', None)
