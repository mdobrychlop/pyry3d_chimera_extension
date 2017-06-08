import matplotlib.pyplot as plt
import re


class Log_Diagram:
    def draw_diagram(self, logfile):
        print "Preparing to draw a diagram..."

        self.overall, self.clashes, self.restraints,
        self.mapfreespace, self.outbox, self.density,
        self.symmetry, self.chi, self.rg = self.reverse_diagram(logfile)

        if self.overall != []:
            del self.overall[0]
        if self.clashes != []:
            del self.clashes[0]
        if self.restraints != []:
            del self.restraints[0]
        if self.mapfreespace != []:
            del self.mapfreespace[0]
        if self.outbox != []:
            del self.outbox[0]
        if self.density != []:
            del self.density[0]
        if self.symmetry != []:
                del self.symmetry[0]
        if self.chi != []:
                del self.chi[0]
        if self.rg != []:
                del self.rg[0]

        plt.plot(self.overall)
        plt.plot(self.clashes)
        plt.plot(self.restraints)
        plt.plot(self.mapfreespace)
        plt.plot(self.outbox)
        plt.plot(self.density)
        plt.plot(self.symmetry)

        plt.legend(("overall score", "clashes", "restraints",
                    "map free space", "out box", "density filling",
                    "symmetry"), loc=4)
        plt.ylabel("Simulation score")
        plt.xlabel("Iteration number")
        plt.show()

        print "Done."

    def reverse_diagram(self, logfile):
        (score, clashes, restraints,
         mapfreespace, outbox, density,
         symmetry, chi, rg) = self.prepare_values(logfile)

        s = []
        c = []
        r = []
        m = []
        o = []
        d = []
        sy = []
        ch = []
        rgs = []

        for i in score:
            # i=i*-1
            s.append(i)
        for i in clashes:
            # i=i*-1
            c.append(i)
        for i in restraints:
            # i=i*-1
            r.append(i)
        for i in mapfreespace:
            # i=i*-1
            m.append(i)
        for i in outbox:
            # i=i*-1
            o.append(i)
        for i in density:
            # i=i*-1
            d.append(i)
        for i in symmetry:
            # i=i*-1
            sy.append(i)
        for i in chi:
            # i=i*-1
            ch.append(i)
        for i in rg:
            # i=i*-1
            rgs.append(i)

        return s, c, r, m, o, d, sy, ch, rgs

    def prepare_values(self, logfile):
        file = open(logfile, "r")
        lines = file.readlines()
        if len(lines[-1].split(" ")) > 5:
            if (lines[-1].split(" ")[5].startswith("is") or
                    lines[-1].startswith("cx") is False):
                last_iteration = lines[-2].split(" ")[4]
            else:
                last_iteration = lines[-1].split(" ")[4]
        else:
            last_iteration = lines[-2].split(" ")[4]

        file = open(logfile, "r")

        o = 1
        slist = [0.0]*int(last_iteration)
        clist = [0.0]*int(last_iteration)
        rlist = [0.0]*int(last_iteration)
        elist = [0.0]*int(last_iteration)
        olist = [0.0]*int(last_iteration)
        dlist = [0.0]*int(last_iteration)
        sylist = [0.0]*int(last_iteration)
        chilist = [0.0]*int(last_iteration)
        rglist = [0.0]*int(last_iteration)

        skip_first = 0  # BARDZO NIEELEGANCKIE, POPRAWIC JAK BEDZIE DOBRZE SIE GENEROWAL LOG

        while o == 1:
            a = file.readline()
            if not a:
                o = o+1
            if re.search("^Number of rejected complexes.*", a):
                o = o+1
            if re.search("^cx score.*", a) is not None:
                b = a.split(" ")
                if b[5].startswith("is") is not False:
                    if skip_first == 1:
                        niter = int(b[4])
                        slist[niter-1] = float(b[5])
                        rlist[niter-1] = float(b[8])
                        clist[niter-1] = float(b[10])
                        elist[niter-1] = float(b[13])
                        olist[niter-1] = float(b[16])
                        dlist[niter-1] = float(b[19])
                        sylist[niter-1] = float(b[22])
                        chilist[niter-1] = float(b[25])
                        rglist[niter-1] = float(b[28])
                    else:
                        skip_first = 1

        list_list = [slist, clist, rlist,
                     elist, olist, dlist,
                     sylist, chilist, rglist]

        for l in list_list:
            i = 0
            while i < len(l):
                if i != 0 and l[i] == 0.0:
                    l[i] = l[i-1]
                i += 1

        return slist, clist, rlist, elist, olist, dlist, sylist, chilist, rglist


# (0, 'cx')
# (1, 'score')
# (2, 'for')
# (3, 'iteration')
# (4, '0')
# (5, '-215.978')
# (6, 'components:')
# (7, 'restraints:')
# (8, '-0')
# (9, 'collisions:')
# (10, '-1.4014')
# (11, 'map')
# (12, 'filling:')
# (13, '-0')
# (14, 'outbox')
# (15, 'atoms:')
# (16, '0')
# (17, 'density')
# (18, 'filling:')
# (19, '-205.868')
# (20, 'symmetry')
# (21, 'penalty:')
# (22, '-0')
# (23, 'chi2')
# (24, 'penalty:')
# (25, '0')
# (26, 'rg')
# (27, 'penalty:')
# (28, '0')

# old (python)
# cx score for iteration 86 is   -145.141    components: restraints: -0.0 collisions: -0.1 map filling: -68.378 outbox atoms: -1.301 density filling: -75.362 symmetry: -0.0 chi2: 0.0 rg: 0.0 

# new (cpp)
# cx score for iteration 0 -215.978 components: restraints: -0 collisions: -1.4014 map filling: -0 outbox atoms: 0 density filling: -205.868 symmetry penalty: -0 chi2 penalty: 0 rg penalty: 0
