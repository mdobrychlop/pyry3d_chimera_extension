import os
# 
directory, filename = os.path.split(__file__)
directory = directory.split("\\")
directory = "/".join(directory)


class Paths:
    def __init__(self):
        # ----- GENERAL -----
        # ----- PLUGIN DIRECTORY
        self.pluginpath = self.find_localisation()
        # ----- PYRY3D DIRECTORY
        self.pyrypath = ""
        # ----- MAP DISPLAYED ON THE SCREEN
        self.mappath = ""
        # ----- STRUCTURES DISPLAYED ON THE SCREEN (PDB FILES GO HERE RIGHT
        # ----- AFTER OPENING THEM USING THE FIRST PAGE)
        self.temppath = self.pluginpath+"/temp_pdb"
        # ----- INPUT FILES GENERATED BEFORE EVERY SIMULATION / SCORING
        self.simscoreinputpath = self.pluginpath+"/input"
        # ----- TEMPORARY SCORING AFTER SIMULATION
        self.temp_out_path = self.pluginpath+"/temp_out"
        # ----- INPUT CONFIGURATION FILE FOR SCORING / SIMULATION / RANKING
        self.configpath = ""
        # ---- INPUT GENERATOR OUTPUT DIRECTORY
        self.ig_outpath = ""
        # ---- INPUT GENERATOR RESTRAINTS FILE
        self.ig_respath = ""
        # ---- RANKING FILES [GIVEN BY THE USER]
        self.rankpath = ""
        # ---- OUTPUT DIR GENERATED BY SIM / SCORING
        self.ss_outpath = ""
        # ---- USER DETERMINED SEQUENCE PATH
        self.user_seqpath = ""

    def find_localisation(self):
        directory, filename = os.path.split(__file__)
        directory = directory.split("\\")
        directory = "/".join(directory)
        return directory
