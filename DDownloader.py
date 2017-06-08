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

import sys, os, traceback, glob, tarfile
from shutil                                             import rmtree

#Internal imports
from Modules.Error.Errors                               import InputError, DensityMapError, FiltrestError
from External_Applications.filtrest3D.RestraintsParser  import *
from External_Applications.filtrest3D.RestraintsParser  import RestraintsParser
from External_Applications.filtrest3D.PModel            import PModel, EmptyStructure
#BioPython
from Bio                                                import PDB
from Bio.PDB                                            import PDBParser
from Bio                                                import SeqIO

from Modules.Error.Errors import SequenceError


class Sequences(object):
    """
       represents sequences given by the user
    """
    
    def __init__(self):
        self.sequences = []       #list gathering all sequences objects from fasta file
    
    def __str__(self):
        return "%s" % ( self.sequences)    
    
    def get_seqs_data(self, fastafile):
        """
            gather data from sequence input FASTA file and checks its format,
            correctnes and assigns data to proper objects
        Parameters:
        -----------
            fastafile      : a file with all sequences given by the user
        Returns:
        ---------
            self.sequences : all sequences as objects (Bio.Seq objects)
        Raises:
        -------
            SequenceError : if given file doesn't exist
        """
        try:
            handle = open(fastafile, "r")
        except: raise SequenceError("File"+str(fastafile)+"doesn't exist")
        
        for seq in SeqIO.parse(handle, "fasta"): self.sequences.append(seq)
        handle.close()
        if len(self.sequences) == 0: raise SequenceError("There are no sequences in fasta file, please check the data file format!")
        return self.sequences
    
    
class Structures(object):
    """
       represents structures coordinates given by the user
    """
    
    def __init__(self):
        self.structures = []
        #list gathering all structures as Bio.PDB objects
        self.pdb_files = []
        
    def __str__(self):
        pass
    
    def get_structures(self, packed_folder):
        """ gather data from structure input files and checks its format,
            correctness and assigns data to proper objects
        PUBLIC
        
        Parameters:
        -----------
            packed_folder   : folder name with tarred files
            
        Returns:
        --------
            untared folder  : with structures which is saved in current dir
            self.structures : all structures as PDB objects
        
        Raises:
        --------
            InputError if archive is wrong (not tar or tar.gz)
        """
        path = os.getcwd()
        folder_name = self.__untar_struct_folder(packed_folder)
        self.__extract_structures(folder_name) 
        os.chdir(path)
        return self.structures
    
    def __untar_struct_folder(self, packed_folder):
        """
            untars folder with structures    
        Parameters:
        -----------
            paced folder name  
        Returns:
        ---------
            unpaced folder
        Raises:
        --------
            InputError if archive is wrong (not tar or tar.gz)
        """
        arch_type = packed_folder[-3:]
        # ----remove Unpacked folder with structures if exist ---------
       # if os.path.exists(str(packed_folder[:-4])) == True:
       #     rmtree(str(packed_folder[:-4]))
        if arch_type == 'tar':
            try: tar = tarfile.open(packed_folder)
            except: raise InputError("Wrong archive with strucutres!")
            
        elif arch_type == 'tar.gz':
            try: tar = tarfile.open(packed_folder, "r:gz")
            except: raise InputError("Wrong archive with strucutres!")
        else: raise InputError("Please change folder file archive into tar or tar.gz format")
        
        #print "sciezka do folderu ze strukturami", packed_folder
        
        fpath = os.path.dirname(packed_folder) #"".join(packed_folder.split("\\")[:-1])
        #print "aktualna lokalizacja", fpath, packed_folder
        ffilename = os.path.split(packed_folder)
        #print "file with struct", ffilename

        tar.extractall(path=fpath)
        tar.close()
        if fpath == "": unpacked = ffilename[1].split(".")[0]
        else: unpacked = fpath+"/"+ffilename[1].split(".")[0] #packed_folder[:-4]
        #print "unpacked", unpacked
        return unpacked   
    
    def __extract_structures(self, folder_name):
        """ takes folder name and parses all files,
            returns self.structures - a list of Bio.PDB structure object
        Parameters:
        -----------
            unpacked folder name
        Returns:
        --------
            self.all_structures : list (containing all structures as PDB objts)
        """
        #folder_path = folder_name.split("/")

        #print "---folder name with structures", folder_name
        try:
            os.chdir(folder_name)
        except:
            raise InputError("PyRy3D cannot locate unpacked folder with structures. Please check whether the archive was prepared properly"%(structure.id))
        self.pdb_files = glob.glob('*.*') #pdb')
        self.pdb_files.sort()

        if len(self.pdb_files) == 0: print "There are no pdb files in the folder!!"
        for pdbfile in self.pdb_files:
            parser = PDBParser()
            try: structure = parser.get_structure(str(pdbfile), pdbfile)
            except: raise InputError("Something is wrong with PDB format in the following file"+pdbfile)
            if len(list(structure.get_residues())) == 0:
                raise InputError("The file you provided for structure %s is not a valid pdb file"%(structure.id))
            self.structures.append(structure)
        if len(self.structures) == 1: print "You are trying to build a complex \
                                            built of one component only!"
        #self.structures = sorted(self.structures, key=lambda st: st.get_chains().id, reverse=False)

class PyryRestraints(RestraintsParser, PModel):
    """
       represents restraints given by the user - in Filtrest3D format
    
    """
    def __init__(self):
        self.pmodels_list    = []    #list containing all input structures as PModel objects
        self.restraint_names = {}    #names of restraint from restraint file
        self.srestraint_names = {}   #the same but for symmetry restraints
        self.restraints      = None  #keep restrains info in filtrest3d model
        self.names           = None  #restraints names
        self.symrestraints   = None  #list of symmetry restraints (Distance Restraints with no specified distance value)
        
    def __str__(self):
        return "%s %s %s" % \
          ( self.pmodels_list, self.restraint_name, self.restraints) 


###############################################33       
    def get_restraints(self, restrfile): #, modelset): 
        """
            gather data from restraints input file and checks its format,
            correctnes and assigns data to proper objects
        Parameters:
        -----------
            restrfile : input file with restraints in Filtrest3D format
            modelset  :   
        Returns:
        --------
            self.restraints
        Raises:
        --------
            FiltrestError : if there are 2 restraints with the same name defined
        """
        self.__extract_restraints(restrfile)
#------------- Assert that restraint names are unique------------------
        fatal=False
        for restraint in self.restraints:
            if self.restraint_names.has_key(restraint.name()):
                raise FiltrestError(str(restraint.name())+\
                    " \n this restraint's name appears more than once!! \n") #+\
                fatal=True
            self.restraint_names[restraint.name()] = restraint
            
        return self.restraints
##################################################################3


    def __extract_restraints(self, restraint_file):
        """
            calls restraintsparser which eats restraints file and gets all data
        Parameters:
        -----------
            restraint_file : filename of restraints
        Raises:
        --------
            FiltrestError : if Filtrest restraints parser fails on input file
        """
        rp = RestraintsParser()
        rp.restrlist = []
####################################333
        try: 
            (self.names, self.restraints, symmetric_restraints) = rp.run(restraint_file)
            self.restraints += symmetric_restraints
############################################
        
        except: 
            raise FiltrestError('Restraint parser fails on '\
                            +restraint_file+'):'+str(traceback.format_exc()))
        
        #print "NAMES--", self.names
        #print "RESTR--", self.restraints
    
class ShapeDescriptor(object):
    """
       represents a density map file of a whole complex given by the user
    """
    def __init__(self):
        self.density_map = None               #EM data
        self.saxs_shape = None                #SAXS data
    
    def __str__(self):
        return "%s, %s" % \
          (self.density_map, self.saxs_shape)    
    
    def get_density_map(self, mapfile):
        """
            gather data from map input file 
        Parameters:
        -----------
            mapfile
        Raises:
        ------
            DensityMapError : if file doesn't exist
        """
        try:    handle = open(mapfile, "r")
        except: raise DensityMapError("File"+str(mapfile)+"doesn't exist")
        self.density_map = mapfile
        return self.density_map
    
    def get_saxs_shape(self, saxsfile):
        """
            gather data from map input file 
        Parameters:
        -----------
            mapfile
        Raises:
        ------
            DensityMapError : if file doesn't exist
        """
        try:    handle = open(saxsfile, "r")
        except: raise DensityMapError("File"+str(saxsfile)+"doesn't exist")
        self.saxs_shape = saxsfile
        return self.saxs_shape
