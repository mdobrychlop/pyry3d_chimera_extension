#! /usr/bin/python
import sys, os, os.path
from optparse import OptionParser

import re

aaAtoms = {
		  'ALA' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB '], 
		  'ARG' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'CD ', 'NE ', 'CZ ', 'NH1', 'NH2'], 
		  'ASN' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'OD1', 'ND2'], 
		  'ASP' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'OD1', 'OD2'], 
		  'CYS' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'SG '],
		  'GLU' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'CD ', 'OE1', 'OE2'], 
		  'GLN' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'CD ', 'OE1', 'OE2'], 
		  'GLY' : ['N  ', 'CA ', 'C  ', 'O  '], 
		  'HIS' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'ND1', 'CD2', 'CE1', 'NE2'], 
		  'ILE' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG1', 'CG2', 'CD1'],
		  'LEU' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'CD1', 'CD2'], 
		  'LYS' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'CD ', 'CE ', 'NZ '], 
		  'MET' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'SD ', 'CE '], 
		  'PHE' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ'], 
		  'PRO' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'CD '], 
		  'SER' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'OG '], 
		  'THR' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'OG1', 'CG2'], 
		  'TRP' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2'], 
		  'TYR' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG ', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ ', 'OH '], 
		  'VAL' : ['N  ', 'CA ', 'C  ', 'O  ', 'CB ', 'CG1', 'CG2']
		  }

hetatmDict = {	'SHP' : 'GLY', 'MEU' : 'GLY', 'IYG' : 'GLY', 'GHP' : 'GLY', 'IPG' : 'GLY', 
				'DMG' : 'GLY', 'MCG' : 'GLY', 'LVG' : 'GLY', 'CHP' : 'GLY', 'GLY' : 'GLY', 
				'GSC' : 'GLY', 'NMC' : 'GLY', 'MPQ' : 'GLY', 'LPG' : 'GLY', 'MGY' : 'GLY', 
				'PLG' : 'GLY', 'TBG' : 'GLY', 'PGY' : 'GLY',
				'1PA' : 'ALA', 'NAM' : 'ALA', 'FLA' : 'ALA', 'TIH' : 'ALA', '3GA' : 'ALA', 
				'BAL' : 'ALA', 'HV5' : 'ALA', 'DAL' : 'ALA', 'DAM' : 'ALA', 'APH' : 'ALA',
				'SEG' : 'ALA', 'HMA' : 'ALA', 'TYY' : 'ALA', 'ALN' : 'ALA', 'CLD' : 'ALA',
				'CSD' : 'ALA', 'AYA' : 'ALA', 'CLB' : 'ALA', 'NXA' : 'ALA', 'PDD' : 'ALA',
				'LAL' : 'ALA', 'MAA' : 'ALA', 'INN' : 'ALA', 'PDL' : 'ALA', 'SBL' : 'ALA',
				'SBD' : 'ALA', 'APM' : 'ALA', 'PYA' : 'ALA', 'NCB' : 'ALA', 'DNP' : 'ALA',
				'HAV' : 'VAL', 'MVA' : 'VAL', 'DVA' : 'VAL', 'MNV' : 'VAL',
				'GPL' : 'LYS', 'LLY' : 'LYS', 'MCL' : 'LYS', 'LLP' : 'LYS', 'LYX' : 'LYS',
				'MIK' : 'LYS', 'LCX' : 'LYS', 'DLS' : 'LYS',
				'M3L' : 'LYS', 'LYZ' : 'LYS', 'ALY' : 'LYS', 'MLZ' : 'LYS', 'LYM' : 'LYS',
				'DLY' : 'LYS', 'MLY' : 'LYS', 'TRG' : 'LYS', 'KCX' : 'LYS',
				'CNT' : 'TYR', 'MTY' : 'TYR', 'TYI' : 'TYR', 'PTH' : 'TYR', 'YOF' : 'TYR',
				'PTM' : 'TYR', 'FLT' : 'TYR', 'DBY' : 'TYR', 'DTY' : 'TYR', 'NIY' : 'TYR',
				'STY' : 'TYR', 'TYS' : 'TYR', 'PTR' : 'TYR', 'TYQ' : 'TYR',
				'2MR' : 'ARG', 'OPR' : 'ARG', 'HRG' : 'ARG', 'DP1' : 'ARG', 'ARV' : 'ARG', 
				'HMR' : 'ARG', 'CMA' : 'ARG', 'ACL' : 'ARG', 'DP9' : 'ARG', 'DAR' : 'ARG',
				'AAR' : 'ARG', '3AR' : 'ARG', 'HAR' : 'ARG', 'ARM' : 'ARG', 'ARO' : 'ARG',
				'L34' : 'GLU', 'GPB' : 'GLU', 'L37' : 'GLU', '354' : 'GLU', 'DGL' : 'GLU',
				'138' : 'GLU', 'L24' : 'GLU',
				'AHB' : 'ASN', 'DMH' : 'ASN', 'MEN' : 'ASN', 'AFA' : 'ASN',
				'LTR' : 'TRP', 'FTR' : 'TRP', 'PAT' : 'TRP', 'TRO' : 'TRP', 'BTR' : 'TRP',
				'4HT' : 'TRP', 'TRF' : 'TRP', 'TRX' : 'TRP', '4IN' : 'TRP', 'PLT' : 'TRP',
				'HTR' : 'TRP', 'DTR' : 'TRP', '4FW' : 'TRP', 'ITR' : 'TRP', 'LTN' : 'TRP',
				'RDF' : 'TRP',
				'DLE' : 'LEU', 'MLE' : 'LEU', 'CLE' : 'LEU', 'FLE' : 'LEU', 'LEF' : 'LEU',
				'MHL' : 'LEU', 'HLU' : 'LEU',
				'ALO' : 'THR', 'DTH' : 'THR', 'TPO' : 'THR', 'THC' : 'THR', '4TP' : 'THR',
				'THO' : 'THR', 'TMB' : 'THR', 'TBM' : 'THR', 'BMT' : 'THR', 'AEI' : 'THR',
				'SNC' : 'CYS', 'CAS' : 'CYS', 'CME' : 'CYS', 'CSZ' : 'CYS', 'CY1' : 'CYS',
				'CCS' : 'CYS', 'OCY' : 'CYS', 'BCX' : 'CYS', 'OCS' : 'CYS', 'CMT' : 'CYS',
				'SMC' : 'CYS', 'CAF' : 'CYS', 'PEC' : 'CYS', 'S2C' : 'CYS', 'SCH' : 'CYS',
				'CEA' : 'CYS', 'FCY' : 'CYS', 'SCY' : 'CYS', 'DCY' : 'CYS', 'GT9' : 'CYS',
				'BCS' : 'CYS', 'C6C' : 'CYS', 'CYM' : 'CYS', 'CZZ' : 'CYS', 'CSO' : 'CYS',
				'143' : 'CYS', 'CSA' : 'CYS', 'CSX' : 'CYS', 'PR3' : 'CYS', 'PBB' : 'CYS',
				'CSU' : 'CYS', 'BUC' : 'CYS', 'CSW' : 'CYS', 'EFC' : 'CYS', 'CSP' : 'CYS',
				'CSS' : 'CYS', 'CSR' : 'CYS', 'PYX' : 'CYS', 'NCY' : 'CYS', 'NPH' : 'CYS',
				'TNB' : 'CYS', 'C5C' : 'CYS', 'BTC' : 'CYS', 'SCS' : 'CYS',
				'PLV' : 'SER', 'SET' : 'SER', 'PLS' : 'SER', 'SEP' : 'SER', 'SAC' : 'SER',
				'NC1' : 'SER', 'SVA' : 'SER', 'DSN' : 'SER', 'S1H' : 'SER', 'OAS' : 'SER',
				'SEB' : 'SER', 'PG1' : 'SER', 'BSE' : 'SER', 'MIS' : 'SER', 'DSE' : 'SER',
				'MC1' : 'SER',
				'MED' : 'MET', 'SAM' : 'MET', 'MHO' : 'MET', 'AME' : 'MET', 'SMM' : 'MET', 
				'OMT' : 'MET', 'MME' : 'MET', 'FME' : 'MET', 'CXM' : 'MET',
				'HYP' : 'PRO', 'POM' : 'PRO', 'DPR' : 'PRO', 'PCC' : 'PRO', 'H5M' : 'PRO', 
				'DPL' : 'PRO', 'DP9' : 'PRO', 'TPR' : 'PRO',
				'HIP' : 'HIS', 'HIC' : 'HIS', 'DHI' : 'HIS', 'NEM' : 'HIS', 'PVH' : 'HIS', 
				'NEP' : 'HIS', 'MHS' : 'HIS',
				'DOH' : 'ASP', 'IAD' : 'ASP', 'BHD' : 'ASP', 'DSP' : 'ASP', 'ASB' : 'ASP', 
				'CBA' : 'ASP', '2AS' : 'ASP', 'DAS' : 'ASP', 'ASK' : 'ASP', '3MD' : 'ASP', 
				'ASL' : 'ASP'
				}
				
hetAtmOther = { 'SLZ' : 'LYS', 'PRR' : 'ALA',
				'DHN' : 'VAL', 'NVA' : 'VAL', 'PPJ' : 'VAL', 'DIV' : 'VAL', 'RON' : 'VAL',
				'FTY' : 'TYR', 'TYN' : 'TYR', 'IYR' : 'TYR',
				'AGM' : 'ARG', 'NNH' : 'ARG',
				'GAM' : 'GLU', '5HP' : 'GLU', 'GGL' : 'GLU', 'CGU' : 'GLU',
				'TRN' : 'TRP',
				'DNE' : 'LEU', 'DNG' : 'LEU', 'DNM' : 'LEU', 'MNL' : 'LEU', 'DDO' : 'LEU',
				'ONL' : 'LEU', 'LDO' : 'LEU', 'NLE' : 'LEU', 'BTA' : 'LEU', '2ML' : 'LEU',
				'NLN' : 'LEU', 'NLO' : 'LEU',
				'SHT' : 'THR', 'GTH' : 'THR', 'IYT' : 'THR', 'TP7' : 'THR', 'TMD' : 'THR',
				'CAY' : 'CYS', 'SAI' : 'CYS', 'SAH' : 'CYS', 'CSE' : 'CYS', 'SOC' : 'CYS',
				'2FM' : 'CYS',
				'HSL' : 'SER',
				'GLH' : 'GLN', 'GHG' : 'GLN', 'MEQ' : 'GLN', 'GLN' : 'GLN', 'DGN' : 'GLN',
				'MGN' : 'GLN', 'HGA' : 'GLN', 'MSO' : 'MET', 'SME' : 'MET', 'MSE' : 'MET',
				'PAQ' : 'PHE', 'PHI' : 'PHE', 'NFA' : 'PHE', 'EHP' : 'PHE', 'DAH' : 'PHE',
				'PPN' : 'PHE', 'PHE' : 'PHE', 'LHY' : 'PHE', 'PBF' : 'PHE', 'BNN' : 'PHE',
				'SMF' : 'PHE', 'DPN' : 'PHE', 'INF' : 'PHE', 'ING' : 'PHE', 'FCL' : 'PHE',
				'APD' : 'PHE', 'HPE' : 'PHE', 'PRS' : 'PRO', 'DMK' : 'ASP',
				'HSO' : 'HIS', '3AH' : 'HIS',
				'GL3' : 'GLY', 
				'ASA' : 'ASP', 
				'5CS' : 'CYS', 'CYD' : 'CYS', 'CY4' : 'CYS', 'AR2' : 'ARG',
				'PCA' : 'GLU', 'ILX' : 'ILE', 'PHA' : 'PHE', 'HTI' : 'SER', 'BLY' : 'LYS', 
				'PFF' : 'PHE', 'IIL' : 'ILE', 'PN2' : 'GLY', 'ORN' : 'GLY', 'EYS' : 'CYS', 
				'CUC' : 'GLY', 'PAS' : 'GLY', 'DCL' : 'GLY', 'FGP' : 'GLY', 'FGL' : 'GLY', 
				'SEC' : 'GLY', 'BFD' : 'GLY', '32T' : 'GLY', 'YCM' : 'GLY', 'AR4' : 'GLY',
				'ASQ' : 'GLY', 'DAB' : 'GLY', 'CYG' : 'GLY', 'CYF' : 'GLY', 'LYN' : 'GLY',
				'FOL' : 'GLY', 'ABA' : 'GLY', 'GMA' : 'GLY', 'CYQ' : 'GLY', '32S' : 'GLY', 
				'ABU' : 'GLY', 'TPQ' : 'GLY', 'TRQ' : 'GLY', 'TRW' : 'GLY', 'SDP' : 'GLY',
				'H2P' : 'HIS', 'PHD' : 'ASP', 'OXX' : 'ASP', 'TYT' : 'TYR'
				}
hetAtmDel = ['ACE', 'NH2', 'ILG', 'BOC', 'ODS', 'CH2', 'CH3', 'PVL', '1LU', 'IAS', 'BRO',
			 'TFA', 'EOX', 'HOA', 'ETO', 'FOR', 'OHE', '2LU', 'CBZ', 'CBX', 'ETA', 'MBH', 
			 'EPO', 'OME', 'HPG', ' CU', 'MMC', ' HG', 'PO4', ' CA', ' ZN', ' CL', 'SO4',
			 ' MG', 'SCN', 'ISO', 'AHO', '2PP', 'RET', 'GLZ', 'NDP', 'SIN', 'GLM', 'QTR',
			 'TFH', 'CGN', 'MYR', 'SEO', 'TYA', 'MP3', '3PA', '4BA', 'TML', 'HEM', 'MCB',
			 'AMS', 'OWQ', 'PTP', 'CY3', 'HOH', 'VAL', 'TRP', 'HDZ', 'FMN', 'DFR', ' MN',
			 'GDP', 'AEA', 'XLS', 'FBP', 'CYO', 'APR', 'PHB', 'MPT', 'CLG', 'CLH', 'ANP',
			 'PNL', 'RTL', 'SO1', 'SO2'
			 ]		

nuclList = ['A', 'C', 'T', 'G', 'U']
nuclHetList = ['CAR', '5PC', 'C2S', 'OMC', 'CCC', 'I5C', 'CBR', '5MC', 'DOC', '5CM', '5NC', 'DCZ', 'DNR', '5IC', 'CH', 
			   'CMR', 'MCY', 'PDU', '125', '127', '5BU', '5MU', 'SSU', 'PSU', 'U8U', 'S4U', 'BRU', '4SU', 'UMP', '5IU', 
			   'FHU', 'DHU', '126', '8OG', 'BGM', 'P',   'MRG', 'G2S', 'OMG', '7MG', 'GTP', 'GMS', 'GDP', '2MG', '8MG', 
			   '1MG', 'PGP', 'IG',  'GN7', 'IGU', 'LGP', 'THM', '64T', 'TSP', 'ATD', '2DT', '5IT', '5AT', 'TAF', 'TLC', 
			   '6MC', 'A23', 'APR', 'AMP', 'SRA', 'NDP', 'PTP',
			   'SIN', 'MYR', 'SEO']		


class Options(object):
    def __init__(self):
        self.proteinchains = False
        self.allchains = False
        self.chainlength = 15
        self.renumber = True
        self.renumberAt = True
        self.rename = None
        self.seqres = True
        self.verbose = True
        self.chainname = ""

    def change_proteinchains(self, new_value):
        self.proteinchains = new_value
    def change_allchains(self, new_value):
        self.allchains = new_value
    def change_chainlength(self, new_value):
        self.chainlength = new_value
    def change_renumber(self, new_value):
        self.renumber = new_value
    def change_renumberAt(self, new_value):
        self.renumberAt = new_value
    def change_rename(self, new_value):
        self.rename = new_value
    def change_seqres(self, new_value):
        self.seqres = new_value
    def change_verbose(self, new_value):
        self.verbose = new_value
    def change_chainname(self, new_value):
        self.chainname = new_value

options = Options()

class NoHeaderInPDBFileException(Exception):

    def __init__(self):
        pass

    def __str__(self):
        return "There is no HEADER in the pdb file."

class AllPDB:
    name = ''
    minChainLength = 15
    header = []
    trailer = []
    atom = {}
    chains = []
    chainsLen = []
    proteinChains = []
    
    def __init__(self): 
        self.name = '' #nazwa pdb
        self.minChainLength = 15 #minimalna dlugosc czyszczonego lancucha
        self.header = [] #linie przed pierwsza linia ATOM/HETATM
        self.trailer = [] #linie po ostatnimATOM/HETATM
        self.atom = {} #nazwaLancucha : linie lancucha
        self.chains = [] #lista nazw lancuchow, kolejnosc taka jak w pdb
        self.chainsLen = [] #lista dlugosci lancuchow
        self.proteinChains = [] #lista nazw lancuchow uznanych za bialkowe
        self.seqres = []
    
    def getName(self):
        return self.name
        
    def getHeader(self):
        return self.header
        
    def getAtom(self):
        return self.atom
        
    def getTrailer(self):	
        return self.trailer
        
    def getChains(self):
        return self.chains
    
    def getChainsLength(self):
        return self.chainsLen		
        
    def getProteinChains(self):
        return self.proteinChains
       
    def changeSeqres(self, changeLog, l):
        """ 
        dla pliku pdb - powinna modyfikowac odpowiednie aminokwasy w liniach SEQRES
        dodatkowo powinna zamieniac nazwy lancuchow w liniach seqres
        """
        pass   

    def renameChain(self, chainLines, fromChainName = '', toChainName = ' '):
        assert len(toChainName) == 1
        if fromChainName == '': 
            fromChainName = self.proteinChains[0]
        renamedChainLines = []
        for line in chainLines:
            match=re.match(r"(ATOM  .{15})(.)(.*)$", line)
            if match != None:
                line = match.expand(r"\1%s\3\n" % toChainName)
            renamedChainLines.append(line)
        return renamedChainLines
        
    def getChain(self, chainName = ''):
        '''
            funkcja ustala ktory lancuch bedzie czyszczony:
            - jezeli nazwa byla podana przez usera to sprawdza czy taki lancuch nialkkowy istnieje w tym pdb
                jezeli istnieje to zwraca jego nazwe
                jezeli nie istanieje to informuje o tym i zwraca pierwszy bialkowy
            - jezeli nazwa nie byla podana, zwraca pierwszy biakowy
        '''	
        if chainName == '': 
            chainName = self.proteinChains[0]
        elif chainName not in self.proteinChains:
            if options.verbose:
                print self.name + ": There is no chain named " + chainName + " or it is not a protein chian.\n Taking first chain named " + self.proteinChains[0] + ".\n"
            chainName = self.proteinChains[0]
        return chainName
        
    def changeHetatoms(self, chainLines):
        '''
        W podanych liniach pliku pdb zamienia\usuwa wszystkie HETATM
        Korzysta z list i slownikow: hetatmDict, hetAtmOther, hetAtmDel
        Zaklada ze TER jest na koncu, zaklada, ze to co dostal jest poprawnycm lancuchem bialkowym.
        Dodatkowo zwraca slownik zamienionych hetatomow tym lancuchu: {hetatom : [pozycja, na_jaki_aminokwas]}, 
        na_jaki_aminokwas = UNK jezeli nie zamienil bo nie rozpoznal hetatomu
        '''
        noHetLines = []
        changeDict = {}
        changeInfo = []
        currResNum = 0 # numer residuum zczytany z linii pdb
        seqResNum = 1 # kolejny numer aminokwasu w sekwencji
        changeFlag = 1 # flaga, zapewniajaca ze do slownika zminionych residuow dodam tylko raz
        currResNum = chainLines[0][22:26]
        for l in chainLines:
            if l[22:26] != currResNum:
                #update informacji do slownika zmienionych hetatomow
                currResNum = l[22:26]
                seqResNum += 1
                changeFlag = 1
            if l[:6] == 'HETATM':
                name = l[17:20]
                if name == 'MSE':
                    if l[13:16] in aaAtoms[hetAtmOther[name]][0:]:
                        l = 'ATOM  ' + l[6:17] + hetAtmOther[name] + l[20:]
                        if changeFlag == 1:
                            #dodaje info do zmienionych residuow
                            changeInfo = ['MSE', hetAtmOther[name]]
                            changeDict.update({seqResNum : changeInfo})
                            changeFlag = 0
                        noHetLines.append(l)
                    elif l[12:16] == 'SE  ':
                        #w zaleznosci od tego czy na koncu mamy jeszcze kolumne z litera atomu
                        if l[66:].strip() == 'SE':
                            atomLetter = l[66:].replace('SE', ' S')
                            l = 'ATOM  ' + l[6:12] + ' SD  ' + hetAtmOther[name] + l[20:66] + atomLetter
                        else:
                            l = 'ATOM  ' + l[6:12] + ' SD  ' + hetAtmOther[name] + l[20:]
                        noHetLines.append(l)
                elif name in hetatmDict.keys():
                    if l[13:16] in aaAtoms[hetatmDict[name]][0:]:
                        l = 'ATOM  ' + l[6:17] + hetatmDict[name] + l[20:]
                        if changeFlag == 1:
                            #dodaje info do zmienionych residuow
                            changeInfo = [name, hetatmDict[name]]
                            changeDict.update({seqResNum : changeInfo})
                            changeFlag = 0
                        noHetLines.append(l)
                elif name in hetAtmOther.keys():
                    if l[13:16] in aaAtoms[hetAtmOther[name]][0:]:
                        l = 'ATOM  ' + l[6:17] + hetAtmOther[name] + l[20:]
                        if changeFlag == 1:
                            #dodaje info do zmienionych residuow
                            changeInfo = [name, hetAtmOther[name]]
                            changeDict.update({seqResNum : changeInfo})
                            changeFlag = 0
                        noHetLines.append(l)	
                elif name in hetAtmDel:
                    if changeFlag == 1:
                        #dodaje info do zmienionych residuow
                        changeInfo = [name, 'DEL']
                        changeDict.update({seqResNum : changeInfo})
                        changeFlag = 0
                    if options.verbose:
                        print 'Delting ' + name + '.'	
                    #pass		
                else:		
                    print 'Unknown ' + name + ', I left it as it was.'
                    if changeFlag == 1:
                        #dodaje info do zmienionych residuow
                        changeInfo = [name, 'UNK']
                        changeDict.update({seqResNum : changeInfo})
                        changeFlag = 0
                    noHetLines.append(l)
            else: #wszystkie pozostale linie czyli ATOM i TER dodaje do noHetLines, changeDict sie nie zmienia
                noHetLines.append(l)
        return (noHetLines, changeDict)		


    def cleanResidues(self, chainLines):
        '''
            Usuwa zdublowane residua, pozostawia pierwsze
        '''
        noDubResidues = []
        i = 0
        while i < len(chainLines): 
            if chainLines[i][16:17] != ' ':
                rotName = chainLines[i][16:17]
                resName = chainLines[i][22:26]
                while i < len(chainLines) and chainLines[i][22:26] == resName:
                    if chainLines[i][16:17] == rotName:
                        noDubResidues.append(chainLines[i][:16] + ' ' + chainLines[i][17:])
                    i += 1
            else:
                noDubResidues.append(chainLines[i])
                i += 1
        return noDubResidues	
    
    def renumberResidues(self, chainLines):
        '''
        Przenumerowuje residua rozpoczynajac od 1, 
        jezeli po numerze residuum jest litera to zostanie usunieta
        '''	
        #UWAGA!!! mozliwe kombinacje:
        # - zmienia sie nazwa i nie zmienia sie numer residuum
        # - zmienia sie numer a nie zmienia sie nazwa
        # - przypadek beznadziejny - nie zmienia sie zadne z powyzszych
        #   -- jedyny ratunek dla przypadku beznadziejnego - zmienia sie nazwa lancucha
        # tu poki co brany jest pod uwage (czestszy i jak najbardziej naturalny) przypadek - zmienia sie numer a nie nazwa
        # w pozostalych przypadkach trzeba cos recznie zmienic w pdb i dopiero puscic cleanPDB
        renumbered = []
        i = 0
        resNum = 1
        #resName = chainLines[0][17:20]
        while i < len(chainLines):
            #resName = chainLines[i][17:20]
            resName = chainLines[i][22:27]
            while i < len(chainLines) and chainLines[i][22:27] == resName:
                newLine = chainLines[i][:22] + str(resNum).rjust(4) + ' ' + chainLines[i][27:]
                renumbered.append(newLine)
                i += 1	
            resNum += 1	
        return renumbered	

    def renumberAtoms(self, chainLines):
        '''
        Przenumerowuje atomy rozpoczynajac od 1
        '''	
        renumbered = []
        i = 0
        print(len(chainLines))
        while i < len(chainLines):
            newLine = chainLines[i][:6] + str(i+1).rjust(5) + chainLines[i][11:]
            renumbered.append(newLine)
            i += 1	
        return renumbered    
        
    def cleanProteinChains(self):
        '''
            Dla kazdego biakowego lancucha wywoluje changeHetatoms, cleanResidues i cleanSeqres
        '''
        cleanAtom = {}
        cleanSeqres = {}
        changeLog = {}
        for l in self.proteinChains:
            noHetLines, changeLog = self.changeHetatoms(self.atom[l])
            linesToClean = self.cleanResidues(noHetLines)
            if options.renumberAt:
                linesToClean = self.renumberAtoms(linesToClean)
            if options.renumber:
                linesToClean = self.renumberResidues(linesToClean)
            if options.rename != None:
                linesToClean = self.renameChain(linesToClean, l, options.rename)
            cleanAtom.update({l : linesToClean})
            if options.seqres and self.seqres != []:
                cleanSeqres.update({l : self.changeSeqres(changeLog, l)}) 
        return cleanAtom, cleanSeqres

class PDBFile(AllPDB):
    nmr = 0
    models = 0
    
    def __init__(self, headerStart, seqres, headerEnd, atom, trailer, chains, chainsLen, minChainLength, name = '', nmr = 0, models = 0):
        self.headerStart = headerStart
        self.seqres = seqres
        self.headerEnd = headerEnd
        self.atom = atom
        self.trailer = trailer
        self.chains = chains
        self.chainsLen = chainsLen
        self.name = name
        self.minChainLength = int(minChainLength)
        self.nmr = nmr
        self.models = models
        self.proteinChains = []
        #ustawiamy lanchchy bialkowe
        for i in range(len(self.chains)):
            flag = 0
            for l in self.atom[chains[i]]:
                if l[:4] == 'ATOM' and l[17:20] in aaAtoms.keys():
                    flag = 1 		
            if flag and self.chainsLen[i] > self.minChainLength:		
                self.proteinChains.append(chains[i])
        
    def getNmr(self):
        return self.nmr
        
    def getModels(self):
        return self.models
       
    def getHeader(self):
        return self.headerStart
        
    def getHeaderEnd(self):
        return self.headerEnd
        
    def getSeqresLines(self):
        return self.seqres
        
    def getSeqresList(self):
        """ zwraca slownik list sekwencji z linii seqres, klucze - nazwy lancuchow """
        seqresDict = {}
        chainSeq = []
        if len(self.seqres) > 0: #tak na wszelki wypadek jakby nie bylo linii SEQRES w pliku
            key = self.seqres[0][11:12] #nazwa pierwszego lancucha
            for line in self.seqres:
                if key == line[11:12]:
                    #zczytujemy kolejna linie tego samego lancucha
                    chainSeq = chainSeq + line[19:].split()
                else:
                    #zaczyna sie nowy lancuch, tamten trzeba zapisac do slownika i zamienic klucz i wyczyscic tablice
                    seqresDict.update({key:chainSeq})
                    key = line[11:12]
                    chainSeq = []
                    chainSeq = chainSeq + line[19:].split()
            #jeszcze ostatni (jedyny) lancuch dodajemy do slownika
            seqresDict.update({key:chainSeq})
        return seqresDict    
        
    def changeSeqres(self, changeDict, chain):
        """ 
        zakladam, ze w sekwencji z koordynat jest nie wiecej aminokwasow niz w sekwencji seqres =>
        pozycja w seqres bedzie >= pozycji w koordynatach
        """
        seqresDict = self.getSeqresList()
        przesuniecia = []
        for pos in changeDict.keys():
            if seqresDict[chain][pos-1] == changeDict[pos][0]: #seqres i sekwencja w atomline odpowiadaja sobie
                seqresDict[chain][pos-1] = changeDict[pos][1] #podmieniamy w seqres na to co jest w tym miejscu w atomline
            else: #szukamy tego hetatomu dalej w seqres
                i = 1 #przesuniecie w sekres w stosunku do koordynat
                while pos + i < len(seqresDict[chain]) and seqresDict[chain][pos+i] != changeDict[pos][0]:
                    i += 1
                przesuniecia.append(i)
                if pos + i < len(seqresDict[chain]) and seqresDict[chain][pos+i] == changeDict[pos][0]:
                    seqresDict[chain][pos+i] = changeDict[pos][1]
        return seqresDict[chain]


class SPDBFile(AllPDB):
    alignment = []	
    
    def __init__(self, header, atom, alignment, trailer, chains, chainsLen, minChainLength, name = ''):
        self.header = header
        self.atom = atom
        self.alignment = alignment
        self.trailer = trailer
        self.chains = chains
        self.chainsLen = chainsLen
        self.name = name
        self.minChainLength = minChainLength
        self.proteinChains = []
        self.seqres = []
        #ustawiamy lanchchy bialkowe
        for i in range(len(self.chains)):
            flag = 0
            for l in self.atom[chains[i]]:
                if l[:4] == 'ATOM' and l[17:20] in aaAtoms.keys():
                    flag = 1 		
            if flag and self.chainsLen[i] > self.minChainLength:		
                self.proteinChains.append(chains[i])

    def getAlignment(self):
        return self.alignment
        
    def getSeqresLines(self):
        return []        

"""-----------------------------------------------------------------------------
	Podzial plikow PDB i SPDB na podpliki zawierajace linie pojedynczego bialka
-----------------------------------------------------------------------------"""		
		
def splitPDB(PDBLines): 
	'''
	Dostaje liste linii pliku multiPDB, zwraca slownik postaci
	nazwa_bialka : lista_odpowiadajacych mu linii
	'''
	PDBDict = {}
	proteinKeyList = []
	for line in PDBLines:
		if line[:6] == 'HEADER':
			lineList = []	#znalezlismy HEADER - czyscimy liste linii
			protein_name = line[62:66]
			protein_name = protein_name[:protein_name.find(" ")].lower()
			lineList.append(line)
			proteinKeyList.append(protein_name)	
		elif line[:3] == 'END':
			try:
				lineList.append(line)	#znalezlismy END - dodajemy te linie do listy linii
			except UnboundLocalError:
				raise NoHeaderInPDBFileException()	
			
			PDBDict.update({protein_name : lineList})	#i nowy wpis do slownika
		else:
			try:
				lineList.append(line)	#wpp po prostu dopisujemy linie do listy
			except UnboundLocalError:
				raise NoHeaderInPDBFileException()	
			
	return proteinKeyList, PDBDict
		
def splitSPDBV(SPDBVLines):
    '''
    Dostaje na wejsciu liste linii projektu SPDBV, zwraca slownik postaci
    nazwa_bialka : lista_odpowiadajacych_mu_linii
    i liste kluczy dla zachowania kolejnosci
    '''
    SPDBVDict = {}
    proteinKeyList = []
    lineList = []
    for line in SPDBVLines:
        if line[:6] == 'SPDBVn':
            lineList.append(line)
            lineList.append('END\n')
            name = line[10:].replace('\n', '').lower()
            proteinKeyList.append(name)
            SPDBVDict.update({name : lineList})#dodaje liste linii i nazwe bialka jako nowa pozycje do slownika
            lineList = []#czyszcze liste linii
        elif line[0:6] == 'SPDBVE' or line[0:3] == 'END':
            pass #pomijam
        else:#czyli kazda inna linie
            lineList.append(line)
    if lineList != []:
        #print "Nie bylo nazwy bialka w pliku! Musze zalozyc, ze w pliku jest tylko jedna struktura bez nazwy."
        print "No protein name in a given file! I assume that there is only one structure in this file."
        name = 'protein'
        lineList.append('END\n')
        proteinKeyList.append(name)
        SPDBVDict.update({name : lineList})
    return proteinKeyList, SPDBVDict		
                    
            
def makePDBobjects(pdbLines, minChainLength):
    '''
        Dostaje liste linii pojedynczego pliku pdb i minimalna dlugosc lancucha, ktory ma uznac za bialkowy.
        Zwraca obiekt PDBFile lub SPDBFile w zaleznosci od tego czy pierwsza linia pliku to HEADER czy nie
        !!!Wyjatki jezeli nie istnieja potrzebne linie w pliku!!!
    '''
    pdbHeaderStart = [] #lista przechowujaca linie do pierwszego SEQRES, caly HEADER dla spdbv
    seqres = [] #lista przechowujaca linie SEQRES
    pdbHeaderEnd = [] #lista przechowujaca linie do pierwszego ATOM/HETATM
    pdbTrailer = [] #lista przechowujaca linie po ostanim ATOM/HETATM
    swissFlag = 1 #czy mamy do czynienia z projektem Swissa
    nmrFlag = 0 #czy plik zawiera wiele modeli - struktura NMR
    chains = [] #lista lancuchow w kolejnosci ich pojawiania sie w pdb
    chainsLen = [] #dlugosc lancuchow, kolejnosc taka jak w chains
    chainsDictLen = {} #???
    chainsDict = {} #slownik nazwaLancucha : linie lancucha
    name = ''
    model = 0 #liczba modeli
    modelList = {} #lista modeli (?)
    pdbAlignment = [] #lista na linie SPDBVa (powtorzone w trailerze!!!)
    
    i = 0
    while pdbLines[i][:6] != 'SEQRES' and pdbLines[i][:4] != 'ATOM' and pdbLines[i][:6] != 'HETATM' and pdbLines[i][:5] != 'MODEL':
        if pdbLines[i][:6] == 'HEADER': 
            swissFlag = 0
            name = (pdbLines[i][62:]).strip()
        pdbHeaderStart.append(pdbLines[i])
        i += 1
    while pdbLines[i][:6] == 'SEQRES':
        seqres.append(pdbLines[i])
        i += 1
    while pdbLines[i][:4] != 'ATOM' and pdbLines[i][:6] != 'HETATM' and pdbLines[i][:5] != 'MODEL':
        pdbHeaderEnd.append(pdbLines[i])
        i += 1
        
    if pdbLines[i][:5] == 'MODEL': 
        nmrFlag = 1
        model = 1
        pdbHeaderEnd.append(pdbLines[i])#MODEL dopisujemy do headera
        i += 1		
        
    currChain = '' #pamietamy nazwe lancucha, zeby wylapywac zmiany bo TER czesto nie ma...
    currRes = '' #pamietamy biezaca nazwe aminokwasow zeby liczyc dlugosc lancucha
    firstRes = 0 #do obliczania dlugosci lancucha
    lastRes = 0 #do obliczania dlugosci lancucha
    chlen = 0 #dlugosc biezacego lancucha 
    tmp = '' #pdb 1ctl ma pusty pierwszy model, trzeba to potem wylapywac...

    while pdbLines[i][:6] != 'ENDMDL':#jezeli byl MODEL to przejde tylko pierwszy
        while pdbLines[i][:4] == 'ATOM' or pdbLines[i][:6] == 'ANISOU' or pdbLines[i][:6] == 'HETATM' or pdbLines[i][:3] == 'TER':
            if pdbLines[i][:6] == 'ANISOU': i += 1
            elif currChain == '': 
                #to znaczy, ze jestem na poczatku lancucha
                tmp = []
                chlen = 0
                currChain = pdbLines[i][21:22]
                currRes = pdbLines[i][22:26]
                chains.append(currChain)
                tmp.append(pdbLines[i])
                i += 1			 
            elif pdbLines[i][:3] == 'TER': #napotkalismy koniec lancucha, sprawdzamy czy w nastepnej linii zmienia sie nazwa lancucha
                tmp.append(pdbLines[i])	
                i += 1
                chainsLen.append(chlen+1)
                if chainsDict.has_key( currChain ):
                    if options.verbose:
                        print "Broken chain "+ currChain
                    ogonek = 1
                    while chainsDict.has_key( currChain + '_' + str(ogonek)): ogonek += 1
                    chainsDict.update({currChain + '_' + str(ogonek) : tmp})
                    chains.pop()
                    chains.append(currChain + '_' + str(ogonek)) 
                else:
                    chainsDict.update({currChain : tmp}) 	
                currChain = ''
            elif pdbLines[i][21:22] != currChain: #nie bylo TER a zmienila sie nazwa lancucha
                if chainsDict.has_key( currChain ):
                    if options.verbose:
                        print "Broken chain "+ currChain 
                    ogonek = 1
                    while chainsDict.has_key( currChain + '_' + str(ogonek)): ogonek += 1
                    chainsDict.update({currChain + '_' + str(ogonek) : tmp})
                    chains.pop()
                    chains.append(currChain + '_' + str(ogonek)) 
                else:
                    #poprzedni lancuch dodajemy do slownika
                    chainsDict.update({currChain : tmp})
                chainsLen.append(chlen+1)
                #tu chyba gubie pierwsza linijke kolejnego lancucha
                #currChain = ''
                currChain = pdbLines[i][21:22]
                currRes = pdbLines[i][22:26]
                chains.append(currChain)
                tmp = [] #zerujemy tablice linii lancucha
                tmp.append(pdbLines[i])	#dodajemy od razu pierwsza linie
                chlen = 1
                i += 1
            else:	
                if pdbLines[i][22:26] != currRes:
                    currRes = pdbLines[i][22:26]
                    chlen += 1 	
                tmp.append(pdbLines[i])	
                i += 1
        if chainsDict.has_key( currChain ):
            if options.verbose:
                print "Broken chain "+ currChain
            ogonek = 1
            while chainsDict.has_key( currChain + '_' + str(ogonek)): ogonek += 1
            chainsDict.update({currChain + '_' + str(ogonek) : tmp}) 
            chains.pop()
            chains.append(currChain + '_' + str(ogonek)) 
        else:
            chainsDict.update({currChain : tmp})		
        chainsLen.append(chlen+1)
        break		
    while i < len(pdbLines):
        if pdbLines[i][:6] == 'SPDBVa':
            pdbAlignment.append(pdbLines[i])
            pdbTrailer.append(pdbLines[i])#!!!dodaje jednoczesnie do alignmentu i tarilera!!!
            i = i + 1
        elif pdbLines[i][:6] == 'SPDBVn':
            name = (pdbLines[i][10:]).strip()
            pdbTrailer.append(pdbLines[i])
            i = i + 1
        elif pdbLines[i][:6] == 'ENDMDL':
            pdbTrailer.append(pdbLines[i]) 	
            i = i + 1
        elif pdbLines[i][:5] == 'MODEL':#pomijam wszystkie poza pierwszym, ktory juz lyknelam
            model += 1
            while i < len(pdbLines) and pdbLines[i][:6] != 'ENDMDL':
                i = i + 1
            if i < len(pdbLines) and pdbLines[i][:6] == 'ENDMDL': #dodalam pierwszy warunek
                i = i + 1	 
        else:		
            pdbTrailer.append(pdbLines[i])	
            i = i + 1
    
    if swissFlag == 0:
        pdbFileData = PDBFile(pdbHeaderStart, seqres, pdbHeaderEnd, chainsDict, pdbTrailer, chains, chainsLen, minChainLength, name, nmrFlag, model)
    else:
        pdbFileData = SPDBFile(pdbHeaderStart, chainsDict, pdbAlignment, pdbTrailer, chains, chainsLen, minChainLength, name)	
    return pdbFileData, swissFlag
    
def run_cleanPDB(file_in, file_out):
    fh1 = open(file_in, 'r')
    fileAllLines = fh1.readlines()
    fh1.close()
    #if options.output:
    fh2 = open(file_out, 'w')
    swiss = 0
    if fileAllLines[0][:6] == 'HEADER':
        fileKeys, fileDict = splitPDB(fileAllLines)
    else:
        fileKeys, fileDict = splitSPDBV(fileAllLines)
        swiss = 1    
    for key in fileKeys:
        pdbData, swissFlag = makePDBobjects(fileDict[key], options.chainlength)
        #if options.output:
        #przepisujemy do pliku heder (spdbv - caly, pdb - do seqres)
        for l in pdbData.getHeader():
            fh2.write(l)
        #zamieniamy hetatomy w lancuchach i w seqres (o ile takie linie byly w pliku)    
        cleanChains, cleanSeqres = pdbData.cleanProteinChains()
        #if options.output:
        if len(pdbData.getSeqresLines()) > 0:
            # !!! tylko dla pliku pdb z niepustym seqres
            if options.allchains or options.proteinchains:
                #wypisujemy do pliku wszystkie linie seqres 
                cc = pdbData.getSeqresLines()[0][11:12]
                l = 0
                #tylko te ktore sa w pdbData.proteinChains sa w cleanSeqres, pozostale zywcem przepisujemy
                for line in pdbData.getSeqresLines():
                    if cc == line[11:12]:
                        if cc in pdbData.proteinChains:
                            new_line = line[:19] + ' '.join(cleanSeqres[cc][l:l+13]) + '\n'
                        else:
                            new_line = line
                        fh2.write(new_line)
                        l += 13
                    else:    
                        cc = line[11:12]
                        l = 0
                        if cc in pdbData.proteinChains:
                            new_line = line[:19] + ' '.join(cleanSeqres[cc][l:l+13]) + '\n'
                        else:
                            new_line = line
                        #new_line = line[:19] + ' '.join(cleanSeqres[cc][l:l+13]) + '\n'
                        fh2.write(new_line)
                        l += 13
                for l in pdbData.getHeaderEnd():
                    fh2.write(l)        
        if options.allchains: 
            #wypisujemy do pliku wszystko
            for chain in pdbData.getChains():
                if chain in cleanChains:
                    for l in cleanChains[chain]: fh2.write(l)
                else:
                    for l in pdbData.getAtom()[chain]: fh2.write(l)	
        elif options.proteinchains:
            #wypisujemy do pliku wszystkie lancuchy bialkowe
            for chain in pdbData.getChains():
                if chain in cleanChains:
                    for l in cleanChains[chain]: fh2.write(l)		
        else:
            chain = pdbData.getChain(options.chainname)
            if len(pdbData.getSeqresLines()) > 0:
                # !!! tylko dla pliku pdb z niepustym seqres
                #wypisujemy tylko seqres odpowiadajace jednemu lancuchowi
                l = 0
                for line in pdbData.getSeqresLines():
                    if chain == line[11:12]:
                        new_line = line[:19] + ' '.join(cleanSeqres[chain][l:l+13]) + '\n'
                        fh2.write(new_line)
                        l += 13
                for l in pdbData.getHeaderEnd():
                    fh2.write(l)          
            #wypisujemy do pliku tylko jeden lancuch bialkowy
            for l in cleanChains[chain]: fh2.write(l)	
        for l in pdbData.getTrailer(): 
            fh2.write(l)	
        fh2.close()	

    
if __name__ == '__main__':
    run_cleanPDB(infile, outfile)

