from chimera import runCommand, openModels
from PyRy3D_input_generator import InStructures
import os
import shutil
import Tkinter
import tkFileDialog


InSctructures = InStructures()


class P1F:
    def __init__(self):
        pass

    def choosemap(self, maplist, initialdir):
        p = Tkinter.Tk()
        p.withdraw()
        mappath = tkFileDialog.askopenfilename(
                    parent=p, initialdir=initialdir, title="Choose .map file",
                    filetypes=[("EM and SAXS shape descriptors", ".map"),
                               ("EM and SAXS shape descriptors", ".mrc"),
                               ("EM and SAXS shape descriptors", ".pdb"),
                               ("EM and SAXS shape descriptors", ".ccp4")
                               ]
                    )

        if mappath != "" and mappath != ():
            mapname = mappath.split("/")[-1]
            maplist.settext("#0 "+mapname)
        return mappath

    def choosestruct(self, initialdir):
        p = Tkinter.Tk()
        p.withdraw()
        slist = []
        structures = tkFileDialog.askopenfilenames(
                        parent=p, initialdir=initialdir,
                        title="Choose structure files",
                        filetypes=[("pdb files", ".pdb")]
                        )

        # WARNING! askopenfilenames:
        # on Windows, it returns a string. On Linux, it returns a list.

        if type(structures) is list or type(structures) is tuple:  # if on Linux
            for i in structures:
                slist.append(i)
        elif len(structures) > 1:  # if on Windows and anything was chosen
            structures = structures.split(" ")
            for i in structures:
                slist.append(i)
        else:  # if "cancel"
            pass
        return slist

    def opencommand(self, mappath, slist):
        if mappath != "":
            command1 = "open "+mappath
            runCommand(command1)
        for i in slist:
            command = "open "+i
            runCommand(command)

    def write_via_ig(self, iopath):
        self.check_dir(iopath)
        InStructures.extract_structures(iopath)
        InStructures.create_outfolder(iopath)
        InStructures.prepare_instructures()

    def writeAllPDBs(self, outpath, mappath):
        self.check_dir(outpath)
        opened = openModels.list()
        howmany = len(opened)
        if mappath != "":
            if howmany > 1:
                    for m in opened:
                        id_ = m.oslIdent()[1:]
                        if id_ != "0":
                            command = "write relative 0 "+id_+" " + \
                                            outpath+"/"+id_+".pdb"
                            runCommand(command)
        else:
            if howmany > 0:
                for m in opened:
                    id_ = m.oslIdent()[1:]
                    command = "write "+id_+" "+outpath+"/"+id_+".pdb"
                    runCommand(command)

    def check_dir(self, dire):
        if not os.path.exists(dire):
            os.makedirs(dire)
        else:
            shutil.rmtree(dire)
            os.makedirs(dire)

    def clearlist(self, smlist):
        smlist.settext("")

    def define_pyry3d_path(self, parent):
        """
        fossil, get rid of it
        """
        path = tkFileDialog.askdirectory(parent=parent, initialdir="/",
                                         title="Point the PyRy3D directory"
                                         )
        return path
