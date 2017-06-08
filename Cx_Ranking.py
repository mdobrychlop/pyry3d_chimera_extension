#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 
# www.genesilico.pl 
#

#creates ranked 3D models of macromoleular complexes 
#based on experimental restraints and a whole complex shape.

__author__ = "Joanna M. Kasprzak"
__code_reviewer__ = "Kristian Rother"
__copyright__ = "Copyright 2010, The PyRy3D Project"
__credits__ = ["Janusz Bujnicki"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Joanna Kasprzak"
__email__ = "jkasp@amu.edu.pl"
__status__ = "Prototype"

from Modules.Constans.Logfile       import logfile, trafl, outfolder

from numpy import array
from random import uniform
from shutil import rmtree
import os, sys

from Modules.Input.Input            import Input
from Modules.Config.Config          import Config
from Modules.Trans.Trans            import Trans
from Modules.Trans.Component        import Component
from Modules.Simul.Simul            import Simul
from Modules.Simul.Complex          import PyRyComplex
from Modules.Input.DataDownloader   import *

from External_Applications.filtrest3D.RestraintsParser import *
#from External_Applications.filtrest3D.PModel import PModel, EmptyStructure
#from External_Applications.filtrest3D.ModelSet import *
from External_Applications.MinkoFit3D.EMmap import EMmap
from External_Applications.MinkoFit3D.AtomicStructure import AtomicStructure
from External_Applications.MinkoFit3D.corcoe import CorCoe
from External_Applications.MinkoFit3D.ccp4_reader import CCP4


from Modules.Constans.Logfile       import logfile, trafl, outfolder
from Modules.Error.Errors           import InputError

from Calculate import *
import optparse

import glob, shutil

class Ranking():
    
    def __init__(self, name):
        self.complex_name = name
        self.score        = 0.0 #score
        self.clashes = 0.0
        self.restraints = 0.0
        self.density = 0.0
        self.outbox = 0.0
        self.freespace = 0.0
        self.cc = 0.0
        
    def __str__(self):
        return "%s %s" % (self.complex_name, self.score)
    
    def set_scores(self, tcomplex):
        self.score      = tcomplex.simulation_score
        self.clashes    = tcomplex.clashes
        self.restraints = tcomplex.restraints
        self.density    = tcomplex.density
        self.freespace  = tcomplex.freespace
        self.outbox     = tcomplex.outbox
        
    def calculate_cc(self, dmap, threshold):
        
        st = AtomicStructure()
        st.read(self.complex_name)
        
        volume = EMmap(dmap, threshold)
        volume.read_volume_fast()
        
        corcoe = CorCoe(volume, st)
        self.cc = corcoe.calculate_cc()

def assign_sequences(seqfile):
    seqs = Sequences()
    return seqs.get_seqs_data(seqfile)
    
def assign_restraints(restrfile): #, modelset):
    if restrfile != None:
        restrs = PyryRestraints()
        return restrs.get_restraints(restrfile) #, modelset)
    else:
        return []       
        
def assign_config(config):
    inp.config = config
    
def assign_map(mapfile):
    map = ShapeDescriptor()
    return map.get_density_map(mapfile)

def set_next_complex(structures): #seqfile, structures, restrfile, config, mapfile):
    
    if structures == None: raise InputError("No structure folder given, I have nothing to do!")
    structs = Structures()	
    return structs.get_structures(structures)
	
def rank_complexes(models, complexes):
    complex_list=[]
    for model in models:
#---geting sequences, structures, restraints and density map provided by the user

        inp.structures = set_next_complex(model)#opts.sequences, test_complex, restraints, con, dmap)
        trans.components = []
        get_input_data(inp, con, trans)
        
# ---------- create first complex --------------------------
        first_complex, scorelista = create_first_complex(trans.components, con, inp.traflfile)# "")
        density_map = trans.get_map(inp.saxsfile, inp.mapfile, con, first_complex)
		
        trans.get_interactions(inp.restraints, inp.symrestraints, trans.components, density_map)
	first_complex.interactions = trans.interactions
	#print "irrererre", inp.restraints
        cuboid, scorelist, taken_mapcells, col_list, inmap_atoms, outbox_atoms, outmap_atoms, restraints_l, pseudores, empty_cells = calculate_simulbox_statistics(first_complex, density_map, inp, trans, con)
        
        rank_complex = Ranking(model)
        rank_complex.set_scores(first_complex)
        complexes.append(rank_complex)
	
	rank=Rank_complex()
        
        rank.set_scores(model,scorelist[0],scorelist[1],scorelist[2],scorelist[3],scorelist[4],scorelist[5])
        
        complex_list.append(rank)
# ---------- save log messages -------------------------------------------     
        logfile.write_file()
        
        #if in_corcoe:
        #    rank_complex.calculate_cc(in_map, float(in_corcoe))
    return complexes, complex_list

#-----------CHIMERA EXTENSION-----------------CHIMERA EXTENSION--------------------#

class Rank_complex:
    def __init__(self):
        self.name=""
        self.score=0.0
        self.restr=0.0
        self.clash=0.0
        self.frees=0.0
        self.oubox=0.0
        self.densi=0.0
    def set_scores(self,name,score,restr,clash,frees,oubox,densi):
        self.name=name.replace(".tar","")
        self.score=float(score)
        self.restr=float(restr)
        self.clash=float(clash)
        self.frees=float(frees)
        self.oubox=float(oubox)
        self.densi=float(densi)

def run_king(sorting,in_rank_folder,in_sequences,in_restraints,in_map,in_config,in_output):
    
# ---- call main modules objects! -----------------------------------------    
    global con
    con   =    Config()

    logfile.set_filename("testpyry3.log")
    
    in_corcoe = None
    
    models = glob.glob(in_rank_folder+"/*.tar")
    
    
    sequences = assign_sequences(in_sequences)
    
    global dmap
    
    if in_restraints == "":
        restraints = None
    else: restraints = in_restraints
    
    if in_map == "":
        shape_descriptor = False
        dmap = None
    else:
        shape_descriptor = True
        density_map = assign_map(in_map)
        dmap = in_map
        
#-----------take simulation parameters or decide to use default values---------       
    con.parse_config_file(in_config, shape_descriptor)
    
    complexes = []
    global inp
    global trans
    
    
    inp   =    Input()  #represents data delivered by the user
    trans =    Trans()  #represents user data tranformed into Pyry objects
    
    inp.outname = in_output
    
    inp.sequences = sequences
    inp.mapfile = density_map
    if in_restraints != "":
	inp.restraints = assign_restraints(restraints) #set_new_restraints(restraints)
    else:
	inp.restraints = []
    
    outfolder.set_dirname(inp.outname)
    
    dir_files = os.listdir(in_rank_folder)
    
    test_data = []
    
    current_wd=in_output
    
    if not os.path.exists(current_wd):
        os.makedirs(current_wd)
    
    for i in dir_files:
	print i
        if i[-3:] == "tar":
	    print "jesttar"
            tar_name=i.split("/")[-1]
	    print "taki tar_name", tar_name
            test_data.append(tar_name)
            shutil.copyfile(in_rank_folder+"/"+i,current_wd+"/"+tar_name)
	 
    os.chdir(in_rank_folder)
    
    complexes, complex_list = rank_complexes(test_data,complexes)#models, complexes)     
        
    complexes = sorted(complexes, key=lambda cx: cx.score, reverse=True)
    
    def rank_window(newlist,sorting):
        
        if sorting=="Overall score":
            newlist = sorted(newlist, key=lambda x: x.score, reverse=True)
        if sorting=="Clashes":
            newlist = sorted(newlist, key=lambda x: x.clash, reverse=True)
        if sorting=="Restraints":
            newlist = sorted(newlist, key=lambda x: x.restr, reverse=True)
        if sorting=="Outbox":
            newlist = sorted(newlist, key=lambda x: x.oubox, reverse=True)
        if sorting=="Map freespace":
            newlist = sorted(newlist, key=lambda x: x.frees, reverse=True)
        if sorting=="Density":
            newlist = sorted(newlist, key=lambda x: x.densi, reverse=True)
    
        rankingwindow=Tkinter.Tk()
        rw=rankingwindow
        
        #sort_dict={"name":"complex name","score":"overall score","restr":"restraints score","clash":"clashes score","frees":"map free space score","oubox":"outbox score","densi":"density"}
        
        rw.title("Complexes ranked by "+sorting+":")
        
        rwf=Tkinter.Frame(rw,relief="ridge",bd=1,padx=5,pady=5)
        rwf.pack(fill="x")
        
        up_number=Tkinter.Label(rwf,text="No.");up_name=Tkinter.Label(rwf,text="Name")
        up_score=Tkinter.Label(rwf,text="Overall score");up_clashes=Tkinter.Label(rwf,text="Clashes")
        up_restraints=Tkinter.Label(rwf,text="Restraints");up_freespace=Tkinter.Label(rwf,text="Map freespace")
        up_outbox=Tkinter.Label(rwf,text="Outbox");up_density=Tkinter.Label(rwf,text="Density")
        
        uplist=[up_number,up_name,up_score,up_restraints,up_clashes,up_freespace,up_outbox,up_density]
        
        a=0
        for i in uplist:
            i.grid(row=0,column=a,sticky="nsew")
            i.configure(fg="blue")
            a=a+1
        
        color=0
        row=1
        
        for i in newlist:
            l_num=Tkinter.Label(rwf,text=str(color+1)+".")
            l_nam=Tkinter.Label(rwf,text=i.name)
            l_sco=Tkinter.Label(rwf,text=str(i.score))
            l_res=Tkinter.Label(rwf,text=str(i.restr))
            l_cla=Tkinter.Label(rwf,text=str(i.clash))
            l_emp=Tkinter.Label(rwf,text=str(i.frees))
            l_oub=Tkinter.Label(rwf,text=str(i.oubox))
            l_den=Tkinter.Label(rwf,text=str(i.densi))
            l_num.grid(row=row,column=0,sticky="nsew")
            l_nam.grid(row=row,column=1,sticky="nsw")
            l_sco.grid(row=row,column=2,sticky="nsew")
            l_res.grid(row=row,column=3,sticky="nsew")
            l_cla.grid(row=row,column=4,sticky="nsew")
            l_emp.grid(row=row,column=5,sticky="nsew")
            l_oub.grid(row=row,column=6,sticky="nsew")
            l_den.grid(row=row,column=7,sticky="nsew")
            l_list=[l_num,l_nam,l_sco,l_res,l_cla,l_emp,l_oub,l_den]
            if color%2 == 0:
                for i in l_list:
                    i.configure(bg="lightgrey")
            row=row+1
            color=color+1
        
        rwf2=Tkinter.Frame(rw,bd=1,relief="ridge",padx=5,pady=5)
        rwf2.pack(fill="x")
        
        def new_filtering(a):
            if sort_menu.getvalue()=="Overall score":
                sorting="Overall score"
            if sort_menu.getvalue()=="Clashes":
                sorting="Clashes"
            if sort_menu.getvalue()=="Restraints":
                sorting="Restraints"
            if sort_menu.getvalue()=="Outbox":
                sorting="Outbox"
            if sort_menu.getvalue()=="Map freespace":
                sorting="Map freespace"
            if sort_menu.getvalue()=="Density":
                sorting="Density"
            rank_window(newlist,sorting)
            
        def save_to_file(le_list,sorting,outfolder):
            outfile=outfolder+"/"+"Pyry3D ranking "+sorting+".txt"
            try:
                f=open(outfile,"w")
                count=1
                print >> f, "          Score          Clash          Restr          Outbo          Mapfs          Densi"
                for i in le_list:
                    score="%14.3f"%i.score ; restr="%14.3f"%i.restr ; clash="%14.3f"%i.clash
                    frees="%14.3f"%i.frees ; oubox="%14.3f"%i.oubox ; densi="%14.3f"%i.densi
                    name=i.name
                    print >> f, str(count)+". "+name
                    print >> f, score, clash, restr, frees, oubox, densi
                    count=count+1
                   # “(%6.2f)” % x
                f.close()
            except:
                pass
            
        def stfile():
            oufo=tkFileDialog.askdirectory(parent=rw,initialdir="/",title="Choose directory")
            save_to_file(newlist,sorting,oufo)
        
        close_button=Tkinter.Button(rwf2,text="Close",command=rw.destroy)
        close_button.pack(side="right")
        save_button=Tkinter.Button(rwf2,text="Save ranking to file...",command=stfile)
        save_button.pack(side="right")
        sort_menu=Pmw.OptionMenu(rwf2,labelpos="w",label_text="Sort results by:",initialitem="Overall score",
                                             items=["Overall score","Clashes","Restraints","Outbox","Map freespace","Density"],
                                             command=new_filtering)
        sort_menu.pack(side="right")
    
    rank_window(complex_list,sorting)
        
        



