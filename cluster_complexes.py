#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 
# www.genesilico.pl 
#

#creates ranked 3D models of macromoleular complexes 
#based on experimental restraints and a whole complex shape.


__author__ = "Joanna M. Kasprzak"
__copyright__ = "Copyright 2010, The PyRy3D Project"
__credits__ = ["Janusz Bujnicki"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Joanna Kasprzak"
__email__ = "jkasp@amu.edu.pl"
__status__ = "Prototype"

import sys, os, glob, shutil

#Internal imports
#BioPython
from Bio                    import PDB
from Bio.PDB                import PDBParser, PDBIO

from Bio.PDB.Atom           import Atom
from Bio.PDB.Residue        import Residue
from Bio.PDB.Chain          import Chain
from Bio.PDB.Model          import Model
from Bio.PDB.Structure      import Structure

from numpy import array, zeros
from math import sqrt

import optparse

from External_Applications.MinkoFit3D.EMmap import EMmap
from External_Applications.MinkoFit3D.AtomicStructure import AtomicStructure
from External_Applications.MinkoFit3D.corcoe import CorCoe
from External_Applications.MinkoFit3D.ccp4_reader import CCP4

class PyRy3D_IG_Error(Exception): pass




DISTANCES_LIST = [1.0, 2.0, 4.0,  8.0]


class Cluster():
    
    def __init(self):
        self.rmsd = 0.0
        self.gdt_ts = 0.0
        self.di  = 0.0
        
        self.val_matrix = None
        self.cluster_matrix = None
        
        self.best_scored = []
        
        
    def iterate_structures(self, structure_set, dist_type, cutoff, struct_nr, score_type, oligo_type):
        """
	calculates scores matices
        """
        if score_type == "pyry3d": structure_set = sorted(structure_set, key=lambda struct: struct.score, reverse=True)
        elif score_type == "ccc": structure_set = sorted(structure_set, key=lambda struct: struct.ccc, reverse=True)
        
        #cluster only struct_nr best scored complexes
        self.best_scored = structure_set[:struct_nr+1]        
        
        print "best scored ccc: ",len(self.best_scored), struct_nr, len(structure_set)
        
        size = len(self.best_scored)
        self.val_matrix = zeros((size, size))  
        self.cluster_matrix = zeros((size, size))
        
        print "number of structures: ", len(self.best_scored)
        
        for st1 in self.best_scored: #structure_set:
            for st2 in self.best_scored: #[index:]:
                #print "comparing", st1.filename, st2.filename
                value = self.calculate_distance(st1, st2, dist_type, oligo_type)
                self.val_matrix[self.best_scored.index(st1), self.best_scored.index(st2)] = value
                if value <= cutoff: self.cluster_matrix[self.best_scored.index(st1), self.best_scored.index(st2)] = 1.
                else: self.cluster_matrix[self.best_scored.index(st1), self.best_scored.index(st2)] = 0.
            
        #print "measure matrix: ", self.val_matrix
        #print "clust matrix: ",  self.cluster_matrix
            
    def cluster(self, cutoff, struct_nr, score_type):
	"""
	
	performs the clustering procedure, call appropriate methods
	
	"""
        print "CLUSTERS, %i best scored models, cut off %i A" %(struct_nr, cutoff)
        results = []
        clusters = []
        size = len(self.best_scored)
        while 1:
            biggest = []
        
            for a in self.cluster_matrix:
                licz = a.sum()
                biggest.append(licz)
        
            big_est = array(biggest)
            maxim = big_est.max()
            
            if maxim < 1: break
            ind = biggest.index(maxim)
            niez = self.cluster_matrix[ind,:]
            tozer = niez.nonzero()
            clusters.append(tozer[0])
            #
            clust = []
            line = "Clustered conformers number   "+str(len(tozer[0]))+"\n"
            results.append(line)
            print line
            for ze in tozer[0]:
			#for ze in tozer[0]:
                    clust.append(self.best_scored[ze])
                    nam = self.best_scored[ze]
                    if score_type == "pyry3d": line = nam.filename+"	"+"score\t"+str(self.best_scored[self.best_scored.index(nam)].score)+"\n"
                    else: line= nam.filename+"	\t"+"score"+str(self.best_scored[self.best_scored.index(nam)].ccc)+"\n"
                    print line
                    results.append(line)
            #
            self.cluster_matrix[:,tozer]= 0
        return results, clusters


    def calculate_distance(self, st1, st2, dist_type, option):
	"""
	calculates distanses: RMSD, GDT_TS, TMSCORE
	"""
        
        if dist_type.upper()   == "RMSD":    
            if option == "oligo":
			    return self.calculate_rmsd_oligo(st1, st2)
            else:
			    return self.calculate_rmsd(st1, st2)
        elif dist_type.upper() == "GDT_TS":  return self.calculate_gdt(st1, st2)
        elif dist_type.upper() == "TMSCORE": return self.calculate_TMScore(st1, st2)
        
	
    def calculate_rmsd_oligo(self, st1, st2):
	"""
	calculates rmsd for two structures
	"""
        similarity_map, total_rmsd = [], 0.0
        ref_list = list(st2.structure.get_chains())
        for chain in st1.structure.get_chains():
            min_distance = 0
            closest = None
            for refch in ref_list:
                if (len(chain.child_list) == len(list(refch.child_list))) :
                    distance = self.calculate_chain_rmsd_matrix(chain, refch, atomtype="CA")
                    if (min_distance == 0) or (distance < min_distance):
                        min_distance = distance
                        closest = refch
            if None != closest:
                similarity_map.append( [chain, closest] )
                ref_list.remove(closest)
                
        sum_dist, sum_length, pair_dist, pair_length = 0., 0., 0., 0.        
        for c1, c2 in similarity_map:
            pair_dist, pair_length = self.calculate_chain_rmsd_matrix(c1, c2, atomtype="CA")
            sum_dist += pair_dist
            sum_length += pair_length
            pair_rmsd = sqrt(pair_dist/pair_length)
            print "RMSD type", c1.id, c2.id, pair_rmsd, 
            
        self.rmsd = sqrt(sum_dist/sum_length)
        print "RMSDtotal", self.rmsd
        return self.rmsd
		
		
    def calculate_rmsd(self, st1, st2):
	"""
	calculates rms for regular complexes (not oligomers)
	"""
        
        coords1, coords2 = [], []
        atoms1 = list(st1.structure.get_atoms())
        atoms2 = list(st2.structure.get_atoms())
        
        for a in atoms1:
            coords1.append(a.coord)
            
        for at in atoms2:
            coords2.append(at.coord)
            
        coords1 = array(coords1)
        coords2 = array(coords2)
            
        rmsd = 0.0
        if len(atoms1) != len(atoms2):
            raise PyRy3D_IG_Error("Compared structures %s %s possess different number of atoms"%(st1.filename, st2.filename))
        rmsd_mat = coords1 - coords2
        rmsd_mat = rmsd_mat**2
        rmsd = sqrt(rmsd_mat.sum()/len(rmsd_mat))
        #print "RMSD", rmsd
        return rmsd
            
	    
    def calculate_chain_rmsd_matrix(self, st1, st2, atomtype):
	"""
	calculates rmsd for chains
	"""
        
        rmsd_total = 0
        rmsd_matrix = []
        st1_residues = st1.child_list
        st2_residues = st2.child_list
        
        resi_pairs = zip(st1_residues, st2_residues)
        
        for resi_pair in resi_pairs:
            rmsd_pair = self.calculate_rsmd_for_two_residues(resi_pair, atomtype)
            rmsd_matrix.append(rmsd_pair)
        
        return sum(rmsd_matrix), len(rmsd_matrix)  
    
    
    def calculate_rsmd_for_two_residues(self, resi_pair, atomtype):
	"""
	calculates rsmd for two residues
	"""
        
        pair_rmsd = 0.0
        resi1 = resi_pair[0]
        resi2 = resi_pair[1]
        resi2_atoms = resi2.child_list
        
        index = 0
        for at in resi1.child_list:
######
######
######
#for Calfas only
            if at.name == atomtype:
                pair_rmsd += self.calculate_rmsd_for_atoms(at, resi2_atoms[index])
            index += 1
            
        return pair_rmsd
    
    
    def calculate_rmsd_for_atoms(self, at1, at2):
	"""
	calculates rmsd for any two atoms
	"""
        
        rmsd_mat = at1 - at2
        rmsd_mat = rmsd_mat**2
        #rmsd = sqrt(rmsd_mat.sum()/len(rmsd_mat))
        return rmsd_mat #rmsd
    
    
    def calculate_TMScore(self, st1, st2):
        """
        Returns TM score.
        by M.Rother
        """
        st1_resi_nr = len(list(st1.structure.get_residues()))
        st2_resi_nr = len(list(st2.structure.get_residues()))
        
        resi_nr = min(st1_resi_nr, st2_resi_nr)
        
        if st1_resi_nr <15 or st2_resi_nr <15:
            print 'WARNING: cannot calculate TM score for structures containing less than 15 residues'
            return None
        #rmsd_calc = self.calculate_rmsd(st1, st2)
        rmsd_matrix = self.calculate_residue_rmsd_matrix(st1, st2)
        d0 = self.calculate_TMScore_normalization_factor(resi_nr)
        return sum([1.0/(1.0+(dist/d0)**2.0) for dist in rmsd_matrix])/resi_nr
    
    
    def calculate_residue_rmsd_matrix(self, st1, st2):
	"""
	rmsd matrix is created for all pairs of residues
	"""
        
        rmsd_matrix = []
        
        st1_residues = list(st1.structure.get_residues())
        st2_residues = list(st2.structure.get_residues())
        
        resi_pairs = zip(st1_residues, st2_residues)
        
        for resi_pair in resi_pairs:
            rmsd_pair = self.calculate_rsmd_for_two_residues(resi_pair)
            rmsd_matrix.append(rmsd_pair)
            
        rmsd_total = sqrt(sum(rmsd_matrix)/len(rmsd_matrix))    
        return rmsd_total #rmsd_matrix
        
        
    def calculate_TMScore_normalization_factor(self, resi_nr):
        """
        Calculates the factor that reduces the influence of structure length.
        """
        return 1.24 * (float(resi_nr)-15.0)**(1.0/3.0) - 1.8
        
	
    def calculate_gdt(self, st1, st2):
        """
        Calculates GDT_TS score by counting residues under 
        distances defined in DISTANCES_LIST.
        by T.Puton
        """
        
        resi_rmsd = self.calculate_residue_rmsd_matrix(st1, st2)
        resi_sum = 0.0
        for dist in DISTANCES_LIST:
            resi_sum += self.count_values_under_cutoff(resi_rmsd,  dist)
        gdt_ts = resi_sum/float(len(DISTANCES_LIST)*len(resi_rmsd))
        print "GDT_TS", gdt_ts
        return gdt_ts
    
    
    def count_values_under_cutoff(self, values_list, cutoff):
        """
        Counts how many value from given value list is lower or equal to given cutoff.
        """
        counter = 0
        for x in values_list:
            if x <= cutoff: counter += 1
        return counter
    
    
    def save_cluster_matrix(self, outfolder):
	"""
	clustering matrix is saved to a text file
	"""
        fh = open(str(outfolder)+"cluster_matrix.txt", "w")
        matrix = str(self.cluster_matrix) #.reshape(-1,).tolist())
        fh.write(matrix)
        fh.close()
    
    
    def save_measure_matrix(self, outfolder):
	"""
	RMSD matrix (or matrix containing other scores) is saved into a text file
	"""
        fh = open(str(outfolder)+"measure_matrix.txt", "w")
        matrix = str(self.val_matrix)
        fh.write(matrix)
        fh.close()

    def sort_to_files(self, threshold, clusters, outname, infolder):
	"""
	Clusters with number of elements above given threshold are saved in separate folders
	"""
        if threshold > len(clusters[0]):  #if all clusters are smaller than size given by user
	    print "There are no clusters with required number of members. The program will copy five largest clusters instead."
            if len(clusters) >= 5:
                clusters = clusters[0:5]
        self.copy_files_to_separate_folders(clusters, threshold, infolder, outname)
		
    def copy_files_to_separate_folders(self, clusters, threshold, infolder, outname):
	"""
	Copies files from particular clusters into separate subfolders
	"""
        count = 0
        for cluster in clusters:
            if len(cluster) >= threshold:
                count += 1
                dir = outname+"/cluster_" + str(len(cluster)) + "_number_" + str(count)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                for f in cluster:
                    nam = self.best_scored[f].filename
                    path_in = os.path.join(infolder,nam)
                    shutil.copy(path_in,dir)
            else: pass



class Cluster_Structure():
    
    def __init__(self, struct, filename, path, score=None):
        self.structure = struct
        self.filename = filename
        self.full_path = path
        self.score    = score
        self.ccc       = None
        self.dmap     = None
        
	
    def write_pdb(self,structure, filename):
        """
        Writting to the pdb_file, saving changed coordinated
        """
        fp=open(filename+"out.pdb", "w")
        io=PDBIO(1)
        io.set_structure(structure)
        io.save(fp)
        
	
    def set_density_map(self, dmap):
        self.dmap = dmap
        
	
    def calculate_ccc(self, map_threshold):
	"""
	calculates cross-correlation coefficience
	"""
                
        st = AtomicStructure()
        st.read(self.full_path)
        
        volume = EMmap(self.dmap, float(map_threshold))
        volume.read_volume_fast()
        
        corcoe = CorCoe(volume, st)
        self.ccc = corcoe.calculate_cc()
        print "corcoe--", self.ccc
        

def extract_structures(folder, scoretype, representation = "fa", density_map = None, map_threshold = None):
    """
	uses Bio.PDB to extract structure objects from pdb files
    """
    structures = []
    pdb_files = glob.glob(str(folder)+'/*.pdb')
    if len(pdb_files) == 0: raise PyRy3D_IG_Error("The files you provided are not pdb files")

    parser = PDBParser(PERMISSIVE=False, QUIET=True)
    
    for pdbfile in pdb_files:
        ffilename = os.path.split(pdbfile)[1]
        scorelist = ffilename.split("_")
        #score = float(scorelist[1])
	#print "##", len(scorelist), scorelist
        if len(scorelist) == 3:
            score = float(scorelist[0])
        elif len(scorelist) == 5:
            score = float(scorelist[2])
	elif len(scorelist) == 4:
            score = float(scorelist[1]) 
        elif len(scorelist) == 6:
            score = float(scorelist[3]) 
        else:
	    print "Input file names do not contain score on expected positions, program assigned 0.0 for all complexes"
	    score = 0.0 #float(scorelist[1])
        structure = parser.get_structure(str(pdbfile), pdbfile)
	####
	#check representation and change it if the need is
	if representation.lower() == "fa":
	    pass
	elif representation.lower() == "ca":
	    structure = retrieve_ca_model(structure)
	elif representation.lower() == "sphere":
	    structure = retrieve_sphere_model(structure) #, score)
	####
        struc = Cluster_Structure(structure,ffilename,pdbfile, score)
        if density_map: struc.set_density_map(density_map)
        if scoretype == "ccc":           
            struc.calculate_ccc(map_threshold)
        #print "SCORE", score
        if len(list(structure.get_residues())) == 0:
            raise PyRy3D_IG_Error("The file you provided for structure %s is not a valid pdb file"%(structure.id))
        structures.append(struc)
        del structure
    return structures
    

def retrieve_ca_model(structure):
    """
    chains are represented only by main chain atoms (Calfas or C4')
    """
    reduced_struct = Structure('clustering_model') 
    my_model = Model(0)
    reduced_struct.add(my_model)
    
    main_chain_atoms = []
    for ch in structure[0]:
	my_chain = Chain(ch.id)
	reduced_struct[0].add(my_chain)
	for resi in ch:
            for atom in resi:
		#print "----", resi.id, resi.get_segid(), ch.id
	        if atom.get_name() == "CA" or atom.get_name() == "C4'" or atom.get_name() == "C4*":
		    my_residue = Residue((' ',resi.id[1],' '),resi.get_resname(),' ')
	            atom = Atom('CA',atom.coord, 0, ' ', ' ',  'CA',atom.get_serial_number())
	            my_chain.add(my_residue)
	            my_residue.add(atom)

	            main_chain_atoms.append(atom)
		    
    return reduced_struct

def retrieve_sphere_model(structure): #, score):
    """
    each chain is here represented by centre of mass only
    """
    sphere_struct = Structure('clustering_model') 
    my_model = Model(0)
    sphere_struct.add(my_model)
    
    #bedzie zmieniona numeracja
    chain_mass_centres, index = [], 0
    for chain in structure.get_chains():
	my_chain = Chain(chain.id)
	sphere_struct[0].add(my_chain)
	
        coord = calculate_centre_of_complex(chain)
	chain_mass_centres.append(coord)
	my_residue = Residue((' ',index,' '),chain.id,' ')
	
	coords = array(coord,'f')
	atom = Atom('CA',coords, 0, 0, ' ', 'CA',1)

	my_chain.add(my_residue)
	my_residue.add(atom)
	
        index += 1
    del structure
    return sphere_struct

def write_structure(structure, filename):
        """
            Writting structure to the pdb_file, saving changed coordinated
        Parameters:
        -----------
            filename    :   final name of structure file        
        """
        out = PDBIO()
        out.set_structure(structure)
        out.save(filename)


def calculate_centre_of_complex(component):
        """
        calculates centre of mass for the whole complex
        """

        component_centre = [0.,0.,0.]

        total_mass = 0

        for atom in component.get_atoms():
            mass = assign_molweight(atom.get_name())
	    total_mass += mass
	    
            component_centre += atom.coord * mass

        component_centre /= total_mass
        return component_centre
    
    
def assign_molweight(atom_id):
        """
            assignes a molecular weight to each atom in a given structure
        Raises:
        -------
            Cmplx_ComponentsError if atom name is not known
        """
        #atom_name = self.get_name()[0]
	
	MOLWEIGHTS = {
             '?' : 0.0,     'H' :  1.00794,   'C' : 12.0107, 'N' : 14.0067,
             'O' : 15.9994, 'P' : 30.973761,  'S' : 32.065}
	
	#atom_id = self.get_name()
	for char in atom_id:
	    if char in MOLWEIGHTS.keys():
		atom_name = char
		break
		
        if atom_name in MOLWEIGHTS.keys(): 
            molweight = MOLWEIGHTS[atom_name]
            return molweight
        else: raise PyRyStructureError("Atom not known"+atom_name)



def start_clustering(infolder,score_type,density_map,density_map_threshold,\
						measure,threshold,struct_nr,representation,output,oligos, sort):
	
    structures  = extract_structures(infolder, score_type, representation, density_map, density_map_threshold)
    
    #print "structures extracted"
    
    c = Cluster()
    
    #print "cluster instance initiated"
    
    if struct_nr == 0:
	struct_nr = len(structures)
	
    #print "starting iterating"
    c.iterate_structures(structures, measure,int(threshold),int(struct_nr), score_type, oligos)
    
    #print "start clustering"
    res,clust = c.cluster(int(threshold),int(struct_nr), score_type)
    #print "clustering ended"
    
    #print "sorttofiles"

    if sort:
        c.sort_to_files(int(sort), clust, output, infolder)
	
    print "saving output"

    clustersfile = open(output+"/clusters.txt", "w")
    for el in res:
        clustersfile.write(el)
    clustersfile.close()
    
