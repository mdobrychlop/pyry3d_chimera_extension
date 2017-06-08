#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 
# www.genesilico.pl 
#

from numpy                          import array
from random                         import uniform
import shutil
from shutil                         import rmtree
import os
from copy                           import deepcopy

from Modules.Input.Input            import Input
from Modules.Config.Config          import Config
from Modules.Trans.Trans            import Trans
from Modules.Trans.Component        import Component
from Modules.Simul.Simul            import Simul
from Modules.Simul.Complex          import PyRyComplex
from Modules.Constans.Logfile       import logfile, trafl, movehist, outfolder
from Modules.Error.Errors           import InputError
from Modules.Input.DataDownloader   import *
from Modules.Trans.CCP4_reader      import CCP4

import sys, traceback
from optparse                                          import OptionParser
from External_Applications.filtrest3D.RestraintsParser import *
from External_Applications.filtrest3D.PModel           import PModel, EmptyStructure
from External_Applications.filtrest3D.ModelSet         import *

import Tkinter
import Pmw
import tkFileDialog
import tkColorChooser

from chimera import runCommand

from Dialogs import Display

from PyRy_Results import Results_Window

import time

import matplotlib.pyplot as plt
import matplotlib.axis as axi
import matplotlib.ticker as ticker


def arrange_components_in_map_center(components, density_map, direct="ahead"):
    """
        puts all components inside simulbox after rearangment all center of masses
        are localized inside a density map cuboid center(this centralization is
        for statistical purposes only; to calculate number of grid cells
        necesarry to describe each component)
    Parameters:
    ----------
        components  : list of all complex components
        density_map : density map object
    """
    for component in components:
        component.pyrystruct.calculate_centre_of_mass()
        vector = []
        if direct == "reverse":
            vec = component.trans_history
            component.translate(-array(vec[1]))
        elif direct == "ahead":
            vector = array(density_map.mapcuboid.center) - array(component.pyrystruct.center_of_mass)
            component.translate(vector)    
            
def arrange_components_inside_simulbox(fcomplex, density_map, trans, con):
    """
        puts all components inside the simulation box;
        after rearangment all centers of mass are randomly localized inside a density map
    Parameters:
    ----------
        components  : list of all complex components
        density_map : density map object
        trans and con are PyRy3D objects from Trans.py and Config.py modules
    """
    
    #print "PyRy3D arranged complex components randomly inside the SIMULATION BOX"
    
    #print "The PyRy3D score now is equal to\t:"
    
    sort_by_covbonds_nr(fcomplex)
    
    if con.start_orient == True:
        #pass
        for component in fcomplex.components:
            if len(component.disorders) != 0:
                for el in component.disorders:
                    if el.fragment_type == "simulated_volume":
                        #print "Component with unknown structure will be positioned randomly inside simulation box"
                        position_component(component)
                        component.is_positioned = True
    else:
        fcomplex.components.sort(key=lambda x:len(x.all_linked_components), reverse=True)
        for component in fcomplex.components:
            if component.moves.state == "fixed" or component.moves.limited == True:
                #do not move components randomly if the user provided any restraints on their moves eg fixed or move_state are provided
                pass
            elif len(component.covalent_bonds) != 0:
                #position this anchor component randomly in the space
                if component.is_positioned == False:
                    vec = position_component(component)
                    #position linked components by translating them by the exact the same vector
                    for covbond in component.covalent_bonds:
                        for comp_index in covbond.chains_indexes:
                            comp = fcomplex.components[comp_index]
                            comp.translate(vec)
                            comp.is_positioned = True
            else:
                if component.is_positioned == False:
                    position_component(component)
                    component.is_positioned = True
    
    fcomplex.calculate_simulation_score(trans.interactions, density_map, con, iteration="first_complex", mode="plugin")
    fcomplex.update_restraints_score(trans.interactions)
    fcomplex.save_pdb('inside_map')

def sort_by_covbonds_nr(fcomplex):
    """
    
    """
    for component in fcomplex.components:
        component.all_linked_components = []
        for covbond in component.covalent_bonds:
            for index in covbond.chains_indexes:
                component.all_linked_components.append(index)  
    
def position_component(component):
    """
    Method translates a component from start orientation (as provided in .pdb file)
    into random orientation inside a density map
    """
    component.pyrystruct.calculate_centre_of_mass()
    random_vector = calculate_translation_vector(density_map)
    vector = array(random_vector) - array(component.pyrystruct.center_of_mass)
    component.translate(vector)
    return vector
            
def calculate_translation_vector(density_map):
    """
        calculates how to translate particular component in order
        to locate it inside the mapcuboid new position is chosen randomly
    Parameters:
    ----------
        density_map :   density map Complex_map object
    Returns:
    --------
        random_vector   : randomly chosen [x,y,z] coordinates inside mapcuboid
    """
    random_x = uniform(density_map.mapcuboid.xmin, density_map.mapcuboid.xmax)
    random_y = uniform(density_map.mapcuboid.ymin, density_map.mapcuboid.ymax)
    random_z = uniform(density_map.mapcuboid.zmin, density_map.mapcuboid.zmax)
    random_vector = [random_x, random_y, random_z]
    return random_vector
            
def calculate_simulbox_statistics(fcomplex, density_map,inp, trans, con):
    """
    if program works with complex shape a function puts components into its center in order to calculate
    scoring function statistics; in next step components are randomly oriented in simulation box
    """
    fcomplex.save_pdb('original_structure')
      
    if inp.mapfile or inp.saxsfile:
        arrange_components_in_map_center(fcomplex.components, density_map)
        fcomplex.save_pdb('incenter')
        fcomplex.get_simboxcells(density_map)
        fcomplex.save_pdb('simboxcells')
        arrange_components_in_map_center(fcomplex.components, density_map, "reverse")
        fcomplex.save_pdb('reversed')
        
    ds=trans.interactions.sd_interactions
    
    #print "EDEDEDDDDDDDDDDDDDDDDDEES", ds
    
    #print dir(ds[0])
    
    #print "tu restraint", dir(ds[0].restraint)
    
    fcomplex.mode="plugin"

    fcomplex.calculate_simulation_score(trans.interactions, density_map, con, iteration="first_complex", mode="plugin")

    
    taken_mapcells=fcomplex.taken_mapcells_coords
    #ds=fcomplex.diffscores
    plugin_scorelist=[str(round(fcomplex.simulation_score,3)),
      str(round(fcomplex.restraints,3) * con.restraints_penalty[0]),
      str(round(fcomplex.clashes,3)    * con.clashes_penalty[0]),
      str(round(fcomplex.freespace,3)* con.freespace_penalty[0]),
      str(round(fcomplex.outbox,3)     * con.outbox_penalty[0]),
      str(round(fcomplex.density,3)  * con.density_penalty[0])]
        
    inmapatoms=[]
        
    inmap_atoms=[]
    outbox_atoms=[]
    outmap_atoms=[]
    empty_cells=[]
    
    #print "ALLTHEMAPCELLSCOORDS", len(fcomplex.allthe_mapcells_coords)
    
    for i in fcomplex.allthe_mapcells_coords:
        #print "NOT EMPTY MAP CELL"
        if i not in taken_mapcells:
	    #print "EMPTY MAP CELL", i
            empty_cells.append(i)
            fcomplex.allthe_mapcells_coords.remove(i)

    for component in fcomplex.components:
        for i in component.inmap_atoms:
            iat=":."+component.pyrystruct.chain+"@/serialNumber="+str(i)
            inmap_atoms.append(iat)
        for j in component.outbox_atoms_li:
            obat=":."+component.pyrystruct.chain+"@/serialNumber="+str(j)
            outbox_atoms.append(obat)
        for k in component.pyrystruct.struct.get_atoms():
            if k.serial_number not in component.inmap_atoms:
                if k.serial_number not in component.outbox_atoms_li:
                    omat=":."+component.pyrystruct.chain+"@/serialNumber="+str(k.serial_number)
                    outmap_atoms.append(omat)
                    
    #print "EMPTY CELLS", len(empty_cells)
    #print "TAKEN MAPCELLS", len(taken_mapcells)
    
    col_dict={}
    
    iter=0    
    for comp in fcomplex.components:
        col_dict[iter]=comp.pyrystruct.chain
        iter+=1
    
    col_list=[]    
    for pair in fcomplex.pairs:
        for i in pair.struct1_collided_atoms:
            col_chain=col_dict[pair.pair[0]]
            col_atid=i
            col_at=":."+col_chain+"@/serialNumber="+str(col_atid)
            col_list.append(col_at)
        for i in pair.struct2_collided_atoms:
            col_chain=col_dict[pair.pair[1]]
            col_atid=i
            col_at=":."+col_chain+"@/serialNumber="+str(col_atid)
            col_list.append(col_at)
    
    pseudores_to_draw=[]
    
    for component in fcomplex.components:
        for i in component.disorders:
            for j in i.pseudoresidues:
                pr=[]
                for k in j.child_list[0].get_coord():
                    pr.append(k)
                pr.append(i.radius)
                pseudores_to_draw.append(pr)
    
    return density_map.simulbox, plugin_scorelist, taken_mapcells, col_list, inmap_atoms, outbox_atoms, outmap_atoms, ds, pseudores_to_draw, empty_cells
    

def check_corretness_of_covalent_bonds(con):
    """
    check whether all chains defined in covalent bonds exist in provided structures
    here all components chains names must exist in pdb files provided
    if some components do not have covalent bonds defined they are treated as independent and are mutated alone.
    """
    for chain in con.linked_components.keys():
        if chain not in con.components_indexes.keys():
            raise InputError("chain %s does not occur in structures you provided. please correct covalent bonds list in configuration file"%(chain))
        for el in con.linked_components[chain]:
            for e in el.chains:
                if e not in con.components_indexes.keys():
                    raise InputError("!!chain %s does not occur in structures you provided. please correct covalent bonds list in configuration file"%(e))

def create_first_complex(components, con, traflfile):
    """
        Sets the initial structure components start_anntemp :
        starting simulation temperature
    Parameters:
        components  : structures in the complex
        con         : PyRy3D object from Config.py
        traflfile   : output file object storing simulation trajectory
    """
#@TODO: clean this function!!!

#----- call first complex, assign components and start temperature ---------
    pc = PyRyComplex (components, None)
    
    
    pc.set_annealing_temp(con.anntemp)
    pc.set_penalties_weights(con.clashes_penalty[0],\
                             con.restraints_penalty[0],\
                             con.freespace_penalty[0],\
                             con.outbox_penalty[0], \
                             con.density_penalty[0],\
                             con.symmetry_penalty[0],\
                             con.chi2_penalty[0],\
                             con.rg_penalty[0]) 
    
# -------------------- add first complex to outfiles ----------------------    
    logfile.write_message("cx score for iteration 0 is\t"+str(round(pc.simulation_score,3))+"\tcomponents: "+\
                         "restraints: "+str(round(pc.restraints,3) * con.restraints_penalty[0])+" "+\
                         "collisions: "+str(round(pc.clashes,3)    * con.clashes_penalty[0])+" "+\
                         "map filling: "+str(round(pc.freespace,3)* con.freespace_penalty[0])+" "+\
                         "outbox atoms: "+str(round(pc.outbox,3)     * con.outbox_penalty[0])+" "+\
                         "density filling: "+str(round(pc.density,3)  * con.density_penalty[0])+\
                         "symmetry: "+str(round(pc.symmetry,3)  * con.symmetry_penalty[0])+\
                         "chi2: "+str(round(pc.chi2,3)  * con.chi2_penalty[0])+\
                         "RGE: "+str(round(pc.rg,3)  * con.rg_penalty[0])+\
                          "\tACTUAL WEIGHTS are respectively: "+str(con.restraints_penalty[0])+", "+\
                         str(con.clashes_penalty[0])+", "+str(con.freespace_penalty[0])+", "+\
                        str(con.outbox_penalty[0])+", "+str(con.density_penalty[0])+", "+str(con.symmetry_penalty)+", "+\
                        str(con.chi2_penalty)+", "+str(con.rg_penalty))
# -------------------------------------------------------------------------

#---- set complex properties before first simulation run -------
    
    for component in pc.components:
        component.clear_pyryatoms()
        component.simulate_disorder(component.pyrystruct.struct)
        component.add_covalent_bonds(con,pc)
       
#@TODO:##these might be combined into one function in Complex class
        pc.add_simul_change(component)
        
        pc.add_movable_component(component)
       
        pc.get_alfa_atoms(component)
       
        pc.add_complex_atoms(len(list(component.pyrystruct.struct.get_atoms())))
        
        pc.add_complex_alfa_atoms(len(component.alfa_atoms))
    pc.calculate_complex_volume ()
    pc.generate_comp_pairs()
    pc.clean_vollist()
    pc.diffscores = []
    
    plugin_scorelist=[str(round(pc.simulation_score,3)),
          str(round(pc.restraints,3) * con.restraints_penalty[0]),
          str(round(pc.clashes,3)    * con.clashes_penalty[0]),
          str(round(pc.freespace,3)* con.freespace_penalty[0]),
          str(round(pc.outbox,3)     * con.outbox_penalty[0]),
          str(round(pc.density,3)  * con.density_penalty[0])]
    
    
    return pc, plugin_scorelist
    
def draw_scores_plot(plot_name, sim):
    """
    method enables to draw energy plots for all complexes generated during simulation process;
    As an output it returns two plots:
    scoreelems.plot : with all scoring function elements values
    simscores.plot  : just with general (total) score values
    Parametrs:
       plot_name : name of the output plot
       sim       : Simul.py object
    """
    saved_complexes = sim.get_plot_values()
    
    scores, clashes, restraints, outbox, mapfill, densities, symmetries, steps = [],[],[],[],[],[],[], []
    for cx in saved_complexes:
        scores.append(cx.sim_score)
        clashes.append(cx.clashes)
        restraints.append(cx.restraints)
        #print "appending restraints", cx.restraints
        outbox.append(cx.outbox)
        mapfill.append(cx.mapfill)
        densities.append(cx.densities)
        symmetries.append(cx.symmetry)
        steps.append(cx.step_nr)
        
        
    #print "Scores", scores
    #Rysowanie wtkresu
    fig = plt.figure()
    xlabel("Steps", fontsize='x-large')
    ylabel("Scores", fontsize='x-large')
    #plot(steps, scores, color ='black', marker = '.', ms=8)
    plot(steps, clashes, color ='green', marker = '.', ms=8)
    plot(steps, restraints, color ='blue', marker = '.', ms=8)
    plot(steps, outbox, color ='red', marker = '.', ms=8)
    plot(steps, mapfill, color ='cyan', marker = '.', ms=8)
    plot(steps, densities, color ='pink', marker = '.', ms=8)
    plot(steps, symmetries, color ='yellow', marker = '.', ms=8)
    plt.legend(("clashes","restraints","outbox", "density map filling","density filling", "symmetry"))
    #show()
    fig.savefig(str(plot_name)+"_scoreelems.plot", dpi = 500, format = 'png', transparent = False)
    
    fig2 = plt.figure()
    xlabel("Steps", fontsize='x-large')
    ylabel("Scores", fontsize='x-large')
    plot(steps, scores, color ='black', marker = '.', ms=8)
    fig2.savefig(str(plot_name)+"_simscores.plot", dpi = 500, format = 'png', transparent = False)

def arrange_first_complex(complex):    
    
    complex.save_pdb('original_structure')
    original_structure = deepcopy(complex)
    arrange_components_in_map_center(complex.components, density_map)
    complex.get_simboxcells(density_map)
    arrange_components_inside_simulbox(complex.components, density_map)
    complex.calculate_simulation_score(trans.interactions, density_map, con, mode="plugin")
    taken_mapcells=complex.taken_mapcells_coords
    ds=complex.diffscores
    plugin_scorelist=[str(round(complex.simulation_score,3)),
      str(round(complex.restraints,3) * con.restraints_penalty[0]),
      str(round(complex.clashes,3)    * con.clashes_penalty[0]),
      str(round(complex.freespace,3)* con.freespace_penalty[0]),
      str(round(complex.outbox,3)     * con.outbox_penalty[0]),
      str(round(complex.density,3)  * con.density_penalty[0])]
        
    inmapatoms=[]
        
    inmap_atoms=[]
    outbox_atoms=[]
    outmap_atoms=[]
        
    for component in complex.components:
        for i in component.inmap_atoms:
            iat=":."+component.pyrystruct.chain+"@/serialNumber="+str(i)
            inmap_atoms.append(iat)
        for j in component.outbox_atoms_li:
            obat=":."+component.pyrystruct.chain+"@/serialNumber="+str(j)
            outbox_atoms.append(obat)
        for k in component.pyrystruct.struct.get_atoms():
            if k.serial_number not in component.inmap_atoms:
                if k.serial_number not in component.outbox_atoms_li:
                    omat=":."+component.pyrystruct.chain+"@/serialNumber="+str(k.serial_number)
                    outmap_atoms.append(omat)
    
    col_dict={}
    
    kantare=0    
    for comp in complex.components:
        col_dict[kantare]=comp.pyrystruct.chain
        kantare+=1
    
    col_list=[]    
    for pair in complex.pairs:
        for i in pair.struct1_collided_atoms:
            col_chain=col_dict[pair.pair[0]]
            col_atid=i
            col_at=":."+col_chain+"@/serialNumber="+str(col_atid)
            col_list.append(col_at)
        for i in pair.struct2_collided_atoms:
            col_chain=col_dict[pair.pair[1]]
            col_atid=i
            col_at=":."+col_chain+"@/serialNumber="+str(col_atid)
            col_list.append(col_at)
    
    complex.save_pdb('inside_map')
    
    pseudores_to_draw=[]
    
    for component in complex.components:
        for i in component.disorders:
            for j in i.pseudoresidues:
                pr=[]
                for k in j.child_list[0].get_coord():
                    pr.append(k)
                pr.append(i.radius)
                pseudores_to_draw.append(pr)

    return original_structure, density_map.simulbox, plugin_scorelist, taken_mapcells, col_list, inmap_atoms, outbox_atoms, outmap_atoms, ds, pseudores_to_draw
   
def get_input_data(inp, con, trans):
    """
        calls Input Module methods to get data delivered by the user i.e:
            restraints_file  :   file with distance restraints in Filtrest3D format
            structures_files :   tar archive with all pdb structures;
                                 ATTENTION! one file can store one chain only
            config_file      :   file with simulation parameters defined by the user
            sequence_file    :   plain fasta file with sequences of all components
        needs Config.py and Trans.py objects
        
    """
    
#@TODO: clean this function; here user should be able to easily convert pdb files into complex or check components correctness!!!

    inp.check_fastanames_duplications()
    
    #if no shape descriptor is provided do not calculate shape fill!!
    if inp.mapfile == None and inp.saxsfile == None:
        con.freespace_penalty = [0.,0.]
        con.density_penalty = [0., 0.]
    index, components_index = 0, {}
    for struct in inp.structures:
        pyrystruct, fasta_seq = inp.check_input(struct)
        #generate subunits objects
        component = trans.get_component(pyrystruct, fasta_seq, con)
        components_index[component.pyrystruct.chain] = index
        index += 1
        
    ##set componenent with no structure as Pyry3D components    
    components_no_struct = inp.get_seq_with_no_struct()
    for seq_no_struct in components_no_struct:
        fasta_seq = seq_no_struct.seq
        seq_name = seq_no_struct.name
        pyrystruct = inp.check_seq_no_struct_input(seq_no_struct)
        trans.get_component_no_struct(seq_no_struct, pyrystruct, con)
        components_index[seq_no_struct.name.split("_")[0]] = index
    #not used yet, will be implemented in next generation of PyRy3D
    con.components_indexes = components_index

    #check whether all chains defined in covalent bonds exist in provided structures
    if len(con.linked_components) != 0: check_corretness_of_covalent_bonds(con)
    
def initialize():
    """
       checks if there are any old ouputs in out_structures folder; if so, it
       deletes them if a user do not have out_structures folder a program creates it
    """
    
    # ----remove decoys from previous PyRy run ---------

    
    #------ set log, trafl, outfolder names ----------
    logfile.set_filename(inp.outname+"/pyry.log")
    if inp.traflfile != None:
        trafl.set_filename(inp.outname+"/"+inp.traflfile+".trafl")
        
    #if inp.movehistory_file:
        #movehist.set_filename(inp.outname+"/"+inp.movehistory_file)
        
    outfolder.set_dirname(inp.outname)

def run_simulation(first_complex, simul_params, interactions, density_map, traflfile):
    """
        calls MC simulation for complex building
    Parameters:
    -----------
        first_complex       : PyRycomplex object
        interactions        : object of interaction class
        simul_params        : simulation parameters (number of steps,
                              number of out complexes etc.)
        density_map         : map object
        traflfile           : name of traflfile if requested by the user
    Returns:
    ----------
        complexes           : list of PyRyComplexes after simulation
    """
#-----------perform simulation!-------------------------------------------------
    #decide which mutations are available for the system
   
    if len(first_complex.movable) == 0: raise InputError("There are no components to mutate. I have northing to do!")
    
    set_available_mutations(first_complex, simul_params)
    
    
    sim = Simul(simul_params)
    sim.setSimulationMethod (simul_params.simmethod)   #@todo Load configuration value
    if simul_params.simmethod == "Genetic": #genetic
        sim.setReductionMethod (simul_params.reductmethod)
        sim.setMaximumPoolSize (100)
    elif simul_params.simmethod == "SimulatedAnnealing" or \
         simul_params.simmethod == "ReplicaExchange":
        sim.setTemperature (simul_params.anntemp)
    if simul_params.simmethod == "ReplicaExchange":
        sim.setReplicaExchangeSteps(simul_params.replica_exchange_freq)
        sim.setReplicaTemperatures(simul_params.replica_temps)
    
    sim.setParameterScalingBoundries(simul_params.param_scaling_ranges)
    
    sim.setParameterScalingValues([ \
    simul_params.param_scaling_range1, simul_params.param_scaling_range2, \
    simul_params.param_scaling_range3 ])
       
    sim.setMutationFrequencies(simul_params.rotation_freq, simul_params.rotation_cov_freq, simul_params.translation_freq, \
                          simul_params.exchange_freq, simul_params.exchangeandsample_freq,  simul_params.simul_dd_freq, simul_params.translation_all_freq,\
                          simul_params.rotation_all_freq, simul_params.rotation_whole_freq)
    
    sim.setReheatingParams(simul_params.reheat, simul_params.reheat_rejections)

    sim.setScalingOption (simul_params.param_scaling)
    sim.setStartingComplex (first_complex)
    sim.setIterationCount (simul_params.simul_steps)
    sim.setIndicators(simul_params)
    sim.setResultCount (simul_params.struct_nr)
    sim.setInteractions (interactions)
    sim.setDensityMap (density_map)
    sim.setStepsToSave(simul_params.niter)
    sim.setTraflfile(traflfile)
    inp.optimized = True

    sim.setServer(inp.optimized)
    sim.setScoresPlot()

    sim.simul_params.movehistory = "x" 
    
    #sim.server = None # zakomentowac jak wersja C++ bedzie OK

    sim.start()
    
    sim.simul_params.movehistory = None
    
    best_complex = sim.lBestScoreComplex
    last_complex = sim.mPool[0]

    return best_complex, last_complex, sim


def save_fullatom_bestmodel(best_complex):
    """
    takes original complex provided by the user and applies all moves performed
    during simulation to it in order to receive best complex (highest scored)
    in full atom representation
    """

    best_complex.save_pdb("best_simulation_complex.pdb")
    trans2 = Trans()
    components_names = []
    for orig_comp in inp.structures:
	print "XXXXXX", orig_comp.fasta_seq
        pyrystruct, fasta_seq = inp.check_input(orig_comp)
        trans2.get_component(pyrystruct, fasta_seq, con, "fullatom")
        
    for seq_no_struct in inp.components_no_struct:
        fasta_seq = seq_no_struct.seq
        seq_name = seq_no_struct.name
        pyrystruct = inp.check_seq_no_struct_input(seq_no_struct)
        trans2.get_component_no_struct(seq_no_struct, pyrystruct, con)
        
    original_complex = PyRyComplex(trans2.components)
    original_complex.save_pdb('original_structure_fullatom.pdb')
    
    
    index = 0

    #print "TTTTTTTTTTTTT", best_complex.components[0].rot_history
    #print "RRRRRRRRRRRRR", best_complex.components[0].trans_history
    for component in original_complex.components:      
        component.simulate_disorder(component.pyrystruct.struct)
        original_complex.get_alfa_atoms(component)
        original_complex.add_complex_atoms(len(list(component.pyrystruct.struct.get_atoms())))
        original_complex.add_complex_alfa_atoms(len(component.alfa_atoms))
        
        rothist = deepcopy(best_complex.components[index].rot_history)
        translations = deepcopy(best_complex.components[index].trans_history)
        for rot in rothist:
            if   rot[0][0] != 0.: component.rotate("", rot[0][0], "X")
            elif rot[0][1] != 0.: component.rotate("", rot[0][1], "Y")
            elif rot[0][2] != 0.: component.rotate("", rot[0][2], "Z")
            elif rot[1][0] != 0.: component.rotate_around_covalent_bond(rot[1][0][0])

        for trans in translations:
            if trans[0] != 0 and trans[1] != 0 and trans[2] != 0 :
                component.translate(trans)

        index += 1
    original_complex.save_pdb(1, inp.fullatom_file)
    
def set_available_mutations(first_complex, simul_params):
    """
       method to check whether all mutations are properly assigned to both
       complex and individual complex components
    """
    if len(first_complex.free) < 2:
        for index in first_complex.movable:
            if "exchange" in first_complex.components[index].moves.allowed_transform:
                first_complex.components[index].moves.allowed_transform.remove("exchange")
   
    for component in first_complex.components:
        if len(simul_params.disabled_mutations) > 0:
            for dis_mut in simul_params.disabled_mutations:
                if dis_mut in component.moves.allowed_transform: component.moves.allowed_transform.remove(dis_mut)
        if len(first_complex.with_disorders) == 0:
            if "SimulateDisorder" in component.moves.allowed_transform:
                component.moves.allowed_transform.remove("SimulateDisorder")

def assign_files(str_path=None,map_path=None,res_path=None,seq_path=None,
                 con_path=None,out_path=None,trafl_path=None,history_path=None,fullatom=None,sax_path=None):
    
    
    global inp
    global trans
    global con
    
    inp   =    Input()  #represents data delivered by the user
    trans =    Trans()  #represents user data tranformed into Pyry objects
    con   =    Config() #represents user defined simulation parameters
    
    #modelsets = []

#---------------get sequences-------------------------------------
    if seq_path != None:
        seqs = Sequences()
        inp.sequences = seqs.get_seqs_data(seq_path)
    if seq_path == None:   
        raise InputError("No sequence file given, I have nothing to do!")

#---------------get structures-------------------------------------
    if str_path != None:
        structs = Structures()
        inp.structures = structs.get_structures(str_path)
        #modelsets.append(PDBDirfile(str_path, structs.pdb_files))
        #modelset=CompositeModelSet(modelsets)
    if str_path == None:   
        inp.structures = []
        #raise InputError("No structure folder given, I have nothing to do!")
        
#---------------get restraints-------------------------------------
    if res_path != None:
        restrs = PyryRestraints()
        #inp.restraints, inp.symrestraints = restrs.get_restraints(res_path)#, modelset)
	inp.restraints = restrs.get_restraints(res_path)#, modelset)
    else:
        restraints = []       
    if res_path == None:
        inp.restraints = []
        
#---------------get density map or saxs shape----------------------------------
    if map_path=="":
        map_path=None
        
    if map_path != None:   
        map = ShapeDescriptor()
        inp.mapfile = map.get_density_map(map_path)
    if sax_path != None:
        saxs = ShapeDescriptor()
        inp.saxsfile = saxs.get_saxs_shape(sax_path)
    
#---------------get config file name-------------------------------------
    if con_path != None:   
        inp.config = con_path
    elif con_path == None:
        con_path = ""
        
#---------------get output name-------------------------------------
    if out_path != None:   
        inp.outname = out_path
    elif out_path == None:
        inp.outname = "pyryresults"
        
    if not os.path.exists(inp.outname):
        os.makedirs(inp.outname)
    else:
        shutil.rmtree(inp.outname)
        os.makedirs(inp.outname)
        
#------------write trajectory file -----------------------------------
    if trafl_path != None:   
        inp.traflfile = trafl_path
    elif trafl_path == None:
        pass
        
#------------fullatom file -----------------------------------
    if fullatom != None:   
        inp.fullatom_file = fullatom
    elif fullatom == None:
        inp.fullatom_file = ""
        
#------------save history of moves to output file-------------------------
    #if history_path != None:   
        #inp.movehistory_file = history_path
    #elif history_path == None:
    inp.movehistory_file = ""
        
def save_movehistory(best_complex, movehist):
        
        for comp in best_complex.components:
            movehist.write_message("COMPONENT\t"+comp.pyrystruct.chain)
            movehist.write_message("TRANSLATIONS\t"+str(comp.trans_history))
            movehist.write_message("ROTATIONS\t"+str(comp.rot_history))
        movehist.write_file()

def calculate_threshold(draw_cub=1,mode="simulate",str_path=None,map_path=None,res_path=None,seq_path=None,con_path=None,out_path=None,trafl_path=None,history_path=None,fullatom=None,sax_path=None,last_elapsed="0.0"):
    
    start = time.time()

# ---- call main modules objects! -----------------------------------------    

    global density_map
    global shape_descriptor
    
    global inp
    global trans
    global con
    
    inp   =    Input()  #represents data delivered by the user
    trans =    Trans()  #represents user data tranformed into Pyry objects
    con   =    Config() #represents user defined simulation parameters
    
    import cProfile
    
#--------------------------- upload user files ----------------------------

    assign_files(str_path,map_path,res_path,seq_path,con_path,out_path,trafl_path,history_path,fullatom,sax_path)
    
#-----------set outfolder, logfile and trafl file -----------------------------
    initialize()
    
#-----------take simulation parameters or decide to use default values---------
    if inp.mapfile == None and inp.saxsfile == None:
        shape_descriptor = False
    else:
        if inp.mapfile: shape_descriptor = "map"
        else: shape_descriptor = "saxs"
        
    con.parse_config_file(inp.config, shape_descriptor)

    con.set_movehistory_file(inp.movehistory_file)
    
    if inp.movehistory_file:
        con.movehistory = inp.movehistory_file
    
#---geting sequences, structures, restraints and density map provided by the user
    get_input_data(inp,con,trans)
   
    
# ---------- create first complex --------------------------
    first_complex, scorelist = create_first_complex(trans.components, con, inp.traflfile)

    ccp4 = CCP4(map_path)

    ccp4.read_simulated_volume_fast(1.0, first_complex)

    return ccp4.threshold

        

def run(draw_cub=1,mode="simulate",str_path=None,map_path=None,res_path=None,seq_path=None,con_path=None,out_path=None,trafl_path=None,history_path=None,fullatom=None,sax_path=None,last_elapsed="0.0"):
    
    start = time.time()

# ---- call main modules objects! -----------------------------------------    

    global density_map
    global shape_descriptor
    
    global inp
    global trans
    global con
    
    inp   =    Input()  #represents data delivered by the user
    trans =    Trans()  #represents user data tranformed into Pyry objects
    con   =    Config() #represents user defined simulation parameters
    
    import cProfile
    
#--------------------------- upload user files ----------------------------

    assign_files(str_path,map_path,res_path,seq_path,con_path,out_path,trafl_path,history_path,fullatom,sax_path)
    
#-----------set outfolder, logfile and trafl file -----------------------------
    initialize()
    
#-----------take simulation parameters or decide to use default values---------
    if inp.mapfile == None and inp.saxsfile == None:
        shape_descriptor = False
    else:
        if inp.mapfile: shape_descriptor = "map"
        else: shape_descriptor = "saxs"
        
    con.parse_config_file(inp.config, shape_descriptor)

    #con.set_movehistory_file(inp.movehistory_file) #pazdzie
    
    if inp.movehistory_file:
        con.movehistory = inp.movehistory_file
    
#---geting sequences, structures, restraints and density map provided by the user
    get_input_data(inp,con,trans)
   
    
# ---------- create first complex --------------------------
    first_complex, scorelist = create_first_complex(trans.components, con, inp.traflfile)

#------------generate interactions between complex components
    density_map = trans.get_map(inp.saxsfile, inp.mapfile, con, first_complex)
    

    trans.get_interactions(inp.restraints, inp.symrestraints, trans.components, density_map)
    #first_complex.interactions = trans.interactions
    
#------------locate components randomly inside the density map----------
    
    cuboid, scorelist, taken_mapcells, col_list, inmap_atoms, outbox_atoms, outmap_atoms, restraints_l, pseudores, empty_cells = calculate_simulbox_statistics(first_complex, density_map, inp, trans, con)
    
    print "RESTRAINTS_LIST", restraints_l
    
    arrange_components_inside_simulbox(first_complex, density_map, trans, con)

    
#------------perform simulation!-----------------------------------------------
    if mode == "simulate":


	best_complex, last_complex, sim = run_simulation(first_complex, con, trans.interactions, density_map, inp.traflfile)
	
	

	if inp.fullatom_file:
		pass
		#save_fullatom_bestmodel(best_complex)

	# ---------- save log messages -------------------------------------------     
	logfile.write_file()
	if inp.movehistory_file: save_movehistory(best_complex, movehist) #movehist.write_file()

    elapsed = (time.time() - start)
    
    if mode == "evaluate":
    
        rz_win=Results_Window()
        rz_win.elapsed_time=last_elapsed
        rz_win.scorelist=scorelist
        rz_win.box=cuboid
        rz_win.col_list=col_list
        rz_win.inmap_atoms=inmap_atoms
        rz_win.outmap_atoms=outmap_atoms
        rz_win.outbox_atoms=outbox_atoms
        rz_win.taken_mapcells=taken_mapcells
        rz_win.cfg_radius=con.simboxradius
        rz_win.restraints=restraints_l
        print "rz_win rerrr", restraints_l
        rz_win.pseudores=pseudores
        rz_win.empty_cells=empty_cells
        rz_win.display_window(mode)

    if mode == "simulate":
	#draw_scores_plot("Simulation plot", sim)
	return inp.outname, inp.outname+"/pyry.log", elapsed
    else:
	return inp.outname, inp.outname+"/pyry.log"
    
