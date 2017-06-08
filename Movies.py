from chimera import runCommand
from exceptions import ValueError
import os


class Anim:

    def isReal(self, txt):
        try:
            float(txt)
            return True
        except ValueError:
            return False

    def get_paths(self):
        fl1 = os.listdir(self.dirpath)
        fl2 = []

        for i in fl1:
            print "fl1", i
            if i[-3:] == "pdb" or i[-3:] == "PDB":
                el = i.split("_")
                if el[-3] == "0.0":
                    pass
        else:
            if self.isReal(el[-3]) or el[-3] == "best":
                el = [el[0], el[1], self.dirpath+"/"+i]
                fl2.append(el)

        fl3 = sorted(fl2, key=lambda el: el[1])
        fl3 = list(reversed(fl3))

        return fl3

    def make_movie(self):
        command = "movie encode output "+self.output+" format "+self.format
        runCommand(command)

    def generate_alt(self):
        l = len(self.paths)
        i = 0
        licz = 1
        sss = 0

        while i < l:
            if i == 0 or i % int(self.step) == 0 or i == l-1:
                sss += 1
                if licz <= 10:
                    runCommand("open "+self.paths[i][2])
                    runCommand("~modeldisp #"+str(licz))
                    licz += 1
                else:
                    licz2 = 1
                    while licz2 <= 10:
                        runCommand("modeldisp #"+str(licz2))
                        runCommand("split #"+str(licz2))
                        runCommand("rainbow model #"+str(licz2))
                        if self.size_x != "" and self.size_y != "":
                            runCommand("movie record size "+self.size_x +
                                       ","+self.size_y+" directory " +
                                       self.img_outdir
                                       )
                        else:
                            runCommand("movie record directory " +
                                       self.img_outdir
                                       )
                        runCommand("wait "+str(self.wait))
                        runCommand("movie crossfade frames 4")
                        runCommand("movie stop")
                        runCommand("close "+str(licz2))
                        licz2 += 1
                    licz = 1

            i += 1

        runCommand("close 1-")
        runCommand("open "+self.paths[-1][2])
        runCommand("split #1")
        runCommand("rainbow model #1")
        runCommand("movie record")
        runCommand("wait 200")
        runCommand("roll y 0.5 720")
        runCommand("wait 500")
        runCommand("movie stop")
        runCommand("movie encode output "+self.output+"."+self.format)
