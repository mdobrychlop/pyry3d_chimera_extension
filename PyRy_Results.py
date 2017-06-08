import Tkinter
import Pmw
import tkColorChooser
import chimera
import webbrowser
from chimera import runCommand
from Paths import Paths
from Dialogs import Display

Paths = Paths()


class Results_Window:

    def __init__(self):
        self.box_color = ((255, 255, 255), '#ffffff')
        self.grid_color = ((255, 255, 255), '#ffffff')
        self.disorder_color = ((255, 255, 255), '#ffffff')
        self.collided_color = ((255, 255, 255), '#ffffff')
        self.outbox_a_color = ((255, 255, 255), '#ffffff')
        self.inmap_a_color = ((255, 255, 255), '#ffffff')
        self.outmap_a_color = ((255, 255, 255), '#ffffff')
        self.outmap_r_color = ((255, 255, 255), '#ffffff')
        self.empty_color = ((255, 255, 255), '#ffffff')
        self.oneres_color = ((255, 255, 255), '#ffffff')
        self.box = ""
        self.grid_radius = ""
        self.col_list = []
        self.restraints = []
        self.scorelist = []
        self.inmap_boxes_list = []

    def fill_im_boxes_list(self):
        box = self.box

        x = box.xmin
        y = box.ymin
        z = box.zmin

        a = self.grid_radius
        penlist = self.taken_mapcells
        prev_colored_field = []
        while x < box.xmax:
            while y < box.ymax:
                while z < box.zmax:
                    for oczko in penlist:
                        if x + a > oczko[0] and y + \
                                a > oczko[1] and z + a > oczko[2]:
                            if x < oczko[0] and y < oczko[1] and z < oczko[2]:
                                colored_field = [x, y, z, x + a, y + a, z + a]
                                if colored_field != prev_colored_field:
                                    self.inmap_boxes_list.append(
                                            ".box " + str(x) + " " + str(y) +
                                            " " + str(z) + " " + str(x + a) +
                                            " " + str(y + a) + " " + str(z + a)
                                            )
                                    prev_colored_field = colored_field
                    z = z + a
                z = box.zmin
                y = y + a
            y = box.ymin
            x = x + a

    def modify_time(self, seconds):
        hours = int(float(seconds)) / 3600
        seconds -= 3600 * hours
        minutes = seconds / 60
        seconds -= 60 * minutes
        return "%02d:%02d:%02d" % (hours, minutes, seconds)

    def set_box_color(self, par, but):
        a = tkColorChooser.askcolor(parent=par)
        but.configure(bg=a[1])
        self.box_color = a

    def set_grid_color(self, par, but):
        a = tkColorChooser.askcolor(parent=par)
        but.configure(bg=a[1])
        self.grid_color = a

    def set_disorder_color(self, par, but):
        a = tkColorChooser.askcolor(parent=par)
        but.configure(bg=a[1])
        self.disorder_color = a

    def set_collided_color(self, par, but):
        a = tkColorChooser.askcolor(parent=par)
        but.configure(bg=a[1])
        self.collided_color = a

    def set_outbox_a_color(self, par, but):
        a = tkColorChooser.askcolor(parent=par)
        but.configure(bg=a[1])
        self.outbox_a_color = a

    def set_inmap_a_color(self, par, but):
        a = tkColorChooser.askcolor(parent=par)
        but.configure(bg=a[1])
        self.inmap_a_color = a

    def set_outmap_a_color(self, par, but):
        a = tkColorChooser.askcolor(parent=par)
        but.configure(bg=a[1])
        self.outmap_a_color = a

    def set_empty_color(self, par, but):
        a = tkColorChooser.askcolor(parent=par)
        but.configure(bg=a[1])
        self.empty_color = a

    def disp_collisions(self):
        dcd = Display()
        dcd.please_wait_window("Highlighting collisions...")
        color = self.collided_color[0]
        for i in self.col_list:
            command = "color " + str(color[0] / 255.0) + "," + str(
                color[1] / 255.0) + "," + str(color[2] / 255.0) + " " + i
            runCommand(command)
        dcd.please_wait.destroy()

    def disp_outbox(self):
        dod = Display()
        dod.please_wait_window("Highlighting outbox atoms...")
        color = self.outbox_a_color[0]
        for i in self.outbox_atoms:
            command = "color " + str(color[0] / 255.0) + "," + str(
                color[1] / 255.0) + "," + str(color[2] / 255.0) + " " + i
            runCommand(command)
        dod.please_wait.destroy()

    def disp_outmap(self):
        dod = Display()
        dod.please_wait_window("Highlighting outmap atoms...")
        color = self.outmap_a_color[0]
        for i in self.outmap_atoms:
            command = "color " + str(color[0] / 255.0) + "," + str(
                color[1] / 255.0) + "," + str(color[2] / 255.0) + " " + i
            runCommand(command)
        dod.please_wait.destroy()

    def disp_grid(self, box, rad):
        color = self.grid_color

        bildfile = open(Paths.pluginpath + "/grid.bild", "w")

        x = box.xmin
        y = box.ymin
        z = box.zmin

        a = rad

        print >> bildfile, ".transparency 0.7"
        print >> bildfile, ".color", color[0][
            0] / 255.0, color[0][1] / 255.0, color[0][2] / 255.0, "\n"
        while x < box.xmax:
            while y < box.ymax:
                while z < box.zmax:
                    print >> bildfile, ".cylinder ", x, y, z, x + a, y, z, "0.05"
                    print >> bildfile, ".cylinder ", x, y, z, x, y + a, z, "0.05"
                    print >> bildfile, ".cylinder ", x, y, z, x, y, z + a, "0.05"
                    z = z + a
                z = box.zmin
                y = y + a
            y = box.ymin
            x = x + a

        bildfile.close()

        runCommand("open " + Paths.pluginpath + "/grid.bild")

        self.grid_radius = rad
        self.in_g2_ch.configure(state="normal")
        self.ew_g2_ch.configure(state="normal")

    def grid_window(self):
        self.grid_window = Tkinter.Tk()
        gw = self.grid_window
        gw.title("Grid configuration")

        self.gwf1 = Tkinter.Frame(gw, relief="ridge", bd=1, pady=3, padx=3)
        self.gwf2 = Tkinter.Frame(gw, relief="ridge", bd=1, pady=3, padx=3)
        self.gwf1.pack(fill="x")
        self.gwf2.pack(fill="x")

        self.grad_label = Tkinter.Label(
            self.gwf1, text="Choose grid cell's size:")
        self.grad_label.grid(row=0, column=0, sticky="w")
        self.grad_scale = Tkinter.Scale(
            self.gwf1,
            from_=10,
            to=20,
            resolution=1,
            orient="horizontal")
        self.grad_scale.grid(row=0, column=1, sticky="w")

        self.gw_close_button = Tkinter.Button(
            self.gwf2, text="Close", command=gw.destroy)
        self.gw_close_button.pack(side="right")
        self.gw_draw_button = Tkinter.Button(
            self.gwf2, text="Display grid", command=lambda: self.disp_grid(
                self.box, self.grad_scale.get()))
        self.gw_draw_button.pack(side="right")

    def disp_inmap_window(self):

        self.inmap_window = Tkinter.Toplevel(self.rw)
        iw = self.inmap_window
        iw.title("Highlight inmap regions")

        self.inmap_v = Tkinter.IntVar(iw)
        self.inmap_v.set(1)

        self.iwf1 = Tkinter.Frame(iw, relief="ridge", bd=1, pady=3, padx=3)
        self.iwf2 = Tkinter.Frame(iw, relief="ridge", bd=1, pady=3, padx=3)
        self.iwf1.pack(fill="x")
        self.iwf2.pack(fill="x")

        self.in_at_ch = Tkinter.Radiobutton(
            self.iwf1,
            text="Color atoms",
            variable=self.inmap_v,
            value=0,
            command=lambda: self.inmap_v.set(0))
        self.in_g1_ch = Tkinter.Radiobutton(
            self.iwf1,
            text="Color grid cells (size from config)",
            variable=self.inmap_v,
            value=1,
            command=lambda: self.inmap_v.set(1))
        self.in_g2_ch = Tkinter.Radiobutton(
            self.iwf1,
            text="Color grid cells (displayed grid size)",
            variable=self.inmap_v,
            value=2,
            command=lambda: self.inmap_v.set(2))

        self.in_at_ch.grid(row=0, sticky="w")
        self.in_g1_ch.grid(row=1, sticky="w")
        self.in_g2_ch.grid(row=2, sticky="w")

        self.iw_close_button = Tkinter.Button(
            self.iwf2, text="Close", command=iw.withdraw)
        self.iw_close_button.pack(side="right")
        self.iw_draw_button = Tkinter.Button(
            self.iwf2,
            text="Highlight regions",
            command=self.display_inmap_regions)
        self.iw_draw_button.pack(side="right")

    def disp_empty_window(self):

        self.empty_window = Tkinter.Toplevel(self.rw)
        ew = self.empty_window
        ew.title("Highlight empty map regions")

        self.empty_v = Tkinter.IntVar(ew)
        self.empty_v.set(1)

        self.ewf1 = Tkinter.Frame(ew, relief="ridge", bd=1, pady=3, padx=3)
        self.ewf2 = Tkinter.Frame(ew, relief="ridge", bd=1, pady=3, padx=3)
        self.ewf1.pack(fill="x")
        self.ewf2.pack(fill="x")

        self.ew_g1_ch = Tkinter.Radiobutton(
            self.ewf1,
            text="Color grid cells (size from config)",
            variable=self.empty_v,
            value=1,
            command=lambda: self.empty_v.set(1))
        self.ew_g2_ch = Tkinter.Radiobutton(
            self.ewf1,
            text="Color grid cells (displayed grid size)",
            variable=self.empty_v,
            value=2,
            command=lambda: self.empty_v.set(2))

        self.ew_g1_ch.grid(row=0, sticky="w")
        self.ew_g2_ch.grid(row=1, sticky="w")

        self.ew_close_button = Tkinter.Button(
            self.ewf2, text="Close", command=ew.withdraw)
        self.ew_close_button.pack(side="right")
        self.ew_draw_button = Tkinter.Button(
            self.ewf2,
            text="Highlight regions",
            command=self.display_empty_regions)
        self.ew_draw_button.pack(side="right")

    def deic_inmap_window(self):
        self.inmap_window.deiconify()

    def deic_empty_window(self):
        self.empty_window.deiconify()

    def disp_disorder(self):
        bildfile = open(Paths.pluginpath + "/disorder_spheres.bild", "w")
        color = self.disorder_color

        print >> bildfile, ".color", color[0][
            0] / 255.0, color[0][1] / 255.0, color[0][2] / 255.0
        for i in self.pseudores:
            print >> bildfile, ".sphere", i[0], i[1], i[2], i[3]

        bildfile.close()
        runCommand("open " + Paths.pluginpath + "/disorder_spheres.bild")

    def display_inmap_regions(self):
        did = Display()
        did.please_wait_window("Highlighting inmap atoms...")
        if self.inmap_v.get() == 0:
            color = self.inmap_a_color[0]
            for i in self.inmap_atoms:
                command = "color " + str(color[0] / 255.0) + "," + str(
                    color[1] / 255.0) + "," + str(color[2] / 255.0) + " " + i
                runCommand(command)
        if self.inmap_v.get() == 1:
            a = self.cfg_radius
            bildfile = open(Paths.pluginpath + "/inmap_1.bild", "w")
            penlist = self.taken_mapcells
            color = self.inmap_a_color
            print >> bildfile, ".transparency 0.5"
            print >> bildfile, ".color", color[0][
                0] / 255.0, color[0][1] / 255.0, color[0][2] / 255.0
            for i in penlist:
                print >> bildfile, ".box ", i[
                    0] - a, i[1] - a, i[2] - a, i[0] + a, i[1] + a, i[2] + a
            bildfile.close()
            runCommand("open " + Paths.pluginpath + "/inmap_1.bild")
        if self.inmap_v.get() == 2:
            box = self.box
            x = box.xmin
            y = box.ymin
            z = box.zmin
            a = self.grid_radius
            color = self.inmap_a_color
            bildfile = open(Paths.pluginpath + "/inmap_2.bild", "w")
            penlist = self.taken_mapcells
            print >> bildfile, ".transparency 0.5"
            print>> bildfile, ".color", color[0][
                0] / 255.0, color[0][1] / 255.0, color[0][2] / 255.0
            prev_colored_field = []
            while x < box.xmax:
                while y < box.ymax:
                    while z < box.zmax:
                        for oczko in penlist:
                            if x + a > oczko[0] and y + \
                                    a > oczko[1] and z + a > oczko[2]:
                                if x < oczko[0] and y < oczko[
                                        1] and z < oczko[2]:
                                    colored_field = [
                                        x, y, z, x + a, y + a, z + a]
                                    if colored_field != prev_colored_field:
                                        print >> bildfile, ".box", x, y, z, x\
                                                             + a, y + a, z + a
                                        prev_colored_field = colored_field
                        z = z + a
                    z = box.zmin
                    y = y + a
                y = box.ymin
                x = x + a

            bildfile.close()

            runCommand("open " + Paths.pluginpath + "/inmap_2.bild")
        did.please_wait.destroy()

    def display_empty_regions(self):
        ded = Display()
        ded.please_wait_window("Highlighting empty map regions...")

        if self.inmap_boxes_list == []:
            if self.inmap_v.get() == 2:
                self.fill_im_boxes_list()

        if self.empty_v.get() == 1:
            a = self.cfg_radius
            bildfile = open(Paths.pluginpath + "/empty_1.bild", "w")
            penlist = self.empty_cells
            color = self.empty_color
            print >> bildfile, ".transparency 0.5"
            print >> bildfile, ".color", color[0][
                0] / 255.0, color[0][1] / 255.0, color[0][2] / 255.0
            for i in penlist:
                print >> bildfile, ".box ", i[
                    0] - a, i[1] - a, i[2] - a, i[0] + a, i[1] + a, i[2] + a
            bildfile.close()
            runCommand("open " + Paths.pluginpath + "/empty_1.bild")
        if self.inmap_v.get() == 2:
            box = self.box
            x = box.xmin
            y = box.ymin
            z = box.zmin
            a = self.grid_radius
            color = self.empty_color
            bildfile = open(Paths.pluginpath + "/empty_2.bild", "w")
            penlist = self.empty_cells
            print >> bildfile, ".transparency 0.5"
            print>> bildfile, ".color", color[0][
                0] / 255.0, color[0][1] / 255.0, color[0][2] / 255.0
            prev_colored_field = []
            while x < box.xmax:
                while y < box.ymax:
                    while z < box.zmax:
                        for oczko in penlist:
                            if x + a > oczko[0] and y + \
                                    a > oczko[1] and z + a > oczko[2]:
                                if x < oczko[0] and y < oczko[
                                        1] and z < oczko[2]:
                                    colored_field = [
                                        x, y, z, x + a, y + a, z + a]
                                    if colored_field != prev_colored_field:
                                        line = ".box " + str(x) + " " + str(y)\
                                                + " " + str(z) + " "\
                                                + str(x + a) + " "\
                                                + str(y + a) + " " + str(z + a)
                                        if line not in self.inmap_boxes_list:
                                            print >> bildfile, line
                                        prev_colored_field = colored_field
                        z = z + a
                    z = box.zmin
                    y = y + a
                y = box.ymin
                x = x + a

            bildfile.close()

            runCommand("open " + Paths.pluginpath + "/empty_2.bild")
        ded.please_wait.destroy()

    def disp_res_window(self):

        self.restraints_list = []
        self.res_string_list = []

        for restraint in self.restraints:

            desired_dist = restraint.restraint.dist

            residue_n1 = str(restraint.first.res1_num)
            residue_n2 = str(restraint.second.res1_num)

            res1_atom = restraint.first.atom_name
            res2_atom = restraint.second.atom_name

            chain1 = restraint.first.chain_id
            chain2 = restraint.second.chain_id

            command = "select :" + residue_n1 + "." + chain1 + "@" + \
                res1_atom + " :" + residue_n2 + "." + chain2 + "@" + res2_atom
            runCommand(command)

            a1 = chimera.selection.currentAtoms(ordered=True)[0]
            a2 = chimera.selection.currentAtoms(ordered=True)[1]

            d = a1.xformCoord().distance(a2.xformCoord())

            dist_difference = abs(d - desired_dist)

            res_attrs = [
                residue_n1,
                res1_atom,
                chain1,
                residue_n2,
                res2_atom,
                chain2,
                dist_difference]

            dispname = residue_n1 + \
                "(" + chain1 + ") <=> " + residue_n2 + "(" + chain2 + ")"
            self.res_string_list.append(dispname)
            self.restraints_list.append([dispname, res_attrs, "black"])

        self.restwin = Tkinter.Tk()
        self.restwin.title("Color restraints")

        self.restwf1 = Tkinter.Frame(
            self.restwin, relief="ridge", bd=1, pady=3, padx=3)
        self.restwf2 = Tkinter.LabelFrame(
            self.restwin,
            text="Restraints:",
            relief="ridge",
            bd=1,
            pady=3,
            padx=3)

        self.restwf1.pack(fill="x")
        self.restwf2.pack(fill="x")

        self.restraints_menu = Pmw.OptionMenu(
            self.restwf1,
            labelpos="w",
            label_text="Restraints: ",
            items=self.res_string_list)
        self.restraints_menu.grid(row=0, column=0)
        self.restraints_color_button = Tkinter.Button(
            self.restwf1, text="Color...",
            command=self.set_oneres_color, bg="white"
            )
        self.restraints_color_button.grid(row=0, column=1)

        self.r_labels_list = []
        roww = 0

        for i in self.restraints_list:
            labeltext = i[0] + " - difference: " + str(i[1][6])
            lab = Tkinter.Label(self.restwf2, text=labeltext, fg=i[2])
            lab.grid(row=roww, sticky="nsew")
            self.r_labels_list.append([i[0], lab])
            roww += 1

        self.restwf3 = Tkinter.Frame(
            self.restwin, relief="ridge", bd=1, pady=3, padx=3)
        self.restwf3.pack(fill="x")
        self.restwclosebutton = Tkinter.Button(
            self.restwf3, text="Close", command=self.restwin.destroy)
        self.restwclosebutton.pack(side="right")

    def set_oneres_color(self):
        self.oneres_color = tkColorChooser.askcolor(parent=self.restwin)
        restraint = self.restraints_menu.getvalue()

        if self.restraints_list != []:
            for i in self.restraints_list:
                if restraint == i[0]:
                    our_restraint = i[1]

            if our_restraint:
                self.color_restraint(our_restraint)

            color = self.oneres_color
            r = float(color[0][0]) / 255.0
            g = float(color[0][1]) / 255.0
            b = float(color[0][2]) / 255.0

            brightness = (r * 299 + g * 587 + b * 114) / 1000

            if brightness <= 0.5:
                bground = "white"
            else:
                bground = "black"

            for i in self.r_labels_list:
                if restraint == i[0]:
                    i[1].configure(fg=self.oneres_color[1], bg=bground)

    def color_restraint(self, restraint):
        color = self.oneres_color

        residue_n1 = restraint[0]
        residue_n2 = restraint[3]

        chain1 = restraint[2]
        chain2 = restraint[5]

        atom1 = restraint[1]
        atom2 = restraint[4]

        command = "display :" + residue_n1 + "." + \
            chain1 + " :" + residue_n2 + "." + chain2
        runCommand(command)

        command = "represent bs :" + residue_n1 + "." + \
            chain1 + " :" + residue_n2 + "." + chain2
        runCommand(command)

        command = "~ribbon :" + residue_n1 + "." + \
            chain1 + " :" + residue_n2 + "." + chain2
        runCommand(command)

        command = "select :" + residue_n1 + "." + chain1 + "@" + \
            atom1 + " :" + residue_n2 + "." + chain2 + "@" + atom2
        print "SELECTING", command
        runCommand(command)

        atoms = chimera.selection.currentAtoms(ordered=True)

        r = float(color[0][0]) / 255.0
        g = float(color[0][1]) / 255.0
        b = float(color[0][2]) / 255.0

        pg = chimera.misc.getPseudoBondGroup('p3dres')
        pb = pg.newPseudoBond(atoms[0], atoms[1])

        color2 = chimera.MaterialColor(r, g, b)

        pb.color = color2

        r = str(r)
        g = str(g)
        b = str(b)

        # TUBE
        # point1 = atoms[0].coord()
        # point2 = atoms[1].coord()
        # point3 = atoms[0].xformCoord()
        # point4 = atoms[1].xformCoord()
        # self.draw_restraint_tube(point1,point2,r,g,b)
        # self.draw_restraint_tube(point3,point4,r,g,b)

        command = "color " + r + "," + g + "," + b + \
            " :" + residue_n1 + "." + chain1 + "@CA"
        runCommand(command)
        command = "color " + r + "," + g + "," + b + \
            " :" + residue_n2 + "." + chain2 + "@CA"
        runCommand(command)

        runCommand("~select")

    def draw_restraint_tube(self, point1, point2, r, g, b):
        bildpath = Paths.pluginpath + "/restraints_tubes.bild"

        bildfile = open(bildpath, "w")

        print >> bildfile, ".color", r, g, b, "\n", ".cylinder", str(
            point1[0]), str(
            point1[1]), str(
            point1[2]), str(
                point2[0]), str(
                    point2[1]), str(
                        point2[2]), "0.1", "\n"

        bildfile.close()

        runCommand("open " + bildpath)

    def display_window(self, mode):
        self.rw = Tkinter.Tk()
        self.rw.title("Results display")

        self.rw.protocol("WM_DELETE_WINDOW", self.handler)

        if mode == "evaluate":

            self.rwfleft = Tkinter.Frame(
                self.rw, bd=1, relief="ridge", pady=5, padx=5)
            self.rwfleft.grid(row=0, column=0, sticky="n")

            self.rwf1 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf2 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf3 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf4 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf5 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf6 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf7 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf8 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf9 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf10 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf11 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf12 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            self.rwf13 = Tkinter.Frame(
                self.rwfleft, relief="ridge", bd=1, pady=3, padx=3)
            framelist = [
                self.rwf1,
                self.rwf2,
                self.rwf3,
                self.rwf4,
                self.rwf5,
                self.rwf6,
                self.rwf7,
                self.rwf8,
                self.rwf9,
                self.rwf10,
                self.rwf11,
                self.rwf12,
                self.rwf13]
            for i in framelist:
                i.pack(fill="x")

            self.sbox = Tkinter.Button(
                self.rwf1,
                text="Display simulation box",
                width=25,
                command=self.display_box)
            self.sbox.pack(side="left")
            self.sbox_c = Tkinter.Button(
                self.rwf1, text="     ", command=lambda: self.set_box_color(
                    self.rw, self.sbox_c), bg="white")
            self.sbox_c.pack(side="right")

            self.grid = Tkinter.Button(
                self.rwf2,
                text="Display simulation grid...",
                width=25,
                command=self.grid_window)
            self.grid.pack(side="left")
            self.grid_c = Tkinter.Button(
                self.rwf2, text="     ", command=lambda: self.set_grid_color(
                    self.rw, self.grid_c), bg="white")
            self.grid_c.pack(side="right")

            self.disorder = Tkinter.Button(
                self.rwf4,
                text="Highlight disordered regions",
                width=25,
                command=self.disp_disorder)
            self.disorder.pack(side="left")
            self.disorder_c = Tkinter.Button(
                    self.rwf4, text="     ",
                    command=lambda: self.set_disorder_color(
                                    self.rw, self.disorder_c
                                    ),
                    bg="white"
                    )
            self.disorder_c.pack(side="right")

            self.collisions = Tkinter.Button(
                self.rwf5,
                text="Highlight collided atoms",
                width=25,
                command=self.disp_collisions)
            self.collisions.pack(side="left")
            self.collisions_c = Tkinter.Button(
                    self.rwf5, text="     ",
                    command=lambda: self.set_collided_color(
                                    self.rw, self.collisions_c
                                    ),
                    bg="white"
                    )
            self.collisions_c.pack(side="right")

            self.outbox = Tkinter.Button(
                self.rwf6,
                text="Highlight outbox regions",
                width=25,
                command=self.disp_outbox)
            self.outbox.pack(side="left")
            self.outbox_c = Tkinter.Button(
                    self.rwf6, text="     ",
                    command=lambda: self.set_outbox_a_color(
                                        self.rw, self.outbox_c
                                        ),
                    bg="white"
                    )
            self.outbox_c.pack(side="right")

            self.inmap = Tkinter.Button(
                self.rwf8,
                text="Highlight regions in map...",
                width=25,
                command=self.deic_inmap_window)
            self.inmap.pack(side="left")
            self.inmap_c = Tkinter.Button(
                    self.rwf8, text="     ",
                    command=lambda: self.set_inmap_a_color(
                                        self.rw, self.inmap_c
                                        ),
                    bg="white"
                    )
            self.inmap_c.pack(side="right")

            self.empty = Tkinter.Button(
                self.rwf9,
                text="Highlight empty map regions...",
                width=25,
                command=self.deic_empty_window)
            self.empty.pack(side="left")
            self.empty_c = Tkinter.Button(
                    self.rwf9, text="     ",
                    command=lambda: self.set_empty_color(
                                    self.rw, self.empty_c
                                    ),
                    bg="white"
                    )
            self.empty_c.pack(side="right")

            self.outmap = Tkinter.Button(
                self.rwf10,
                text="Highlight outmap regions",
                width=25,
                command=self.disp_outmap)
            self.outmap.pack(side="left")
            self.outmap_c = Tkinter.Button(
                    self.rwf10, text="     ",
                    command=lambda: self.set_outmap_a_color(
                                    self.rw, self.outmap_c
                                    ),
                    bg="white"
                    )
            self.outmap_c.pack(side="right")

            self.rest = Tkinter.Button(
                self.rwf12,
                text="Display distance restraints...",
                width=25,
                command=self.disp_res_window)
            self.rest.pack(side="left")
            self.rest_c = Tkinter.Button(
                    self.rwf12, text="     ",
                    command=lambda: self.choose_color(
                                    self.rw, self.rest_c
                                    )
                    )
            self.rest_c.pack(side="right")
            self.rest_c.configure(state="disabled")

        # -------- RIGHT SIDE

        self.rwfright = Tkinter.Frame(
                            self.rw, bd=1, relief="ridge", pady=5, padx=5
                            )
        self.rwfright.grid(row=0, column=1, sticky="n")

        srf0 = Tkinter.Frame(
                self.rwfright, pady=3, padx=3, bd=1
                )
        srf0.pack(fill="x")

        Tkinter.Label(srf0, text="Scoring complete.").pack()

        if mode == "evaluate":
            Tkinter.Label(srf0, text="Elapsed time: -").pack()
        else:
            Tkinter.Label(
                srf0,
                text="Elapsed time: " +
                self.modify_time(
                    self.elapsed_time) +
                "s"
                ).pack()

        srf1 = Tkinter.Frame(
                self.rwfright,
                bd=1,
                relief="ridge",
                pady=3,
                padx=3
                )
        srf1.pack(fill="x")

        simscore_result = Pmw.EntryField(
                            srf1,
                            labelpos="w",
                            label_text="Overall score:",
                            entry_width=15,
                            entry_state="readonly"
                            )
        simscore_result.pack(fill="x")
        simscore_result.setvalue(self.scorelist[0])

        srf2 = Tkinter.Frame(
                self.rwfright,
                bd=1,
                relief="ridge",
                pady=3,
                padx=3
                )
        srf2.pack(fill="x")

        clashes_result = Pmw.EntryField(
                            srf2,
                            labelpos="w",
                            label_text="Restraints penalty:",
                            entry_width=15,
                            entry_state="readonly"
                            )
        clashes_result.grid(row=1, sticky="e")
        clashes_result.setvalue(self.scorelist[1])

        restraints_result = Pmw.EntryField(
                                srf2,
                                labelpos="w",
                                label_text="Clashes penalty:",
                                entry_width=15,
                                entry_state="readonly"
                                )
        restraints_result.grid(row=2, sticky="e")
        restraints_result.setvalue(self.scorelist[2])

        empty_score_result = Pmw.EntryField(
                                srf2,
                                labelpos="w",
                                label_text="Map freespace penalty:",
                                entry_width=15,
                                entry_state="readonly"
                                )
        empty_score_result.grid(row=3, sticky="e")
        empty_score_result.setvalue(self.scorelist[3])

        outbox_result = Pmw.EntryField(
                            srf2,
                            labelpos="w",
                            label_text="Outbox penalty:",
                            entry_width=15,
                            entry_state="readonly"
                            )
        outbox_result.grid(row=4, sticky="e")
        outbox_result.setvalue(self.scorelist[4])

        density_result = Pmw.EntryField(
                            srf2,
                            labelpos="w",
                            label_text="Density penalty:",
                            entry_width=15,
                            entry_state="readonly"
                            )
        density_result.grid(row=5, sticky="e")
        density_result.setvalue(self.scorelist[5])

        self.srf3 = Tkinter.Frame(self.rwfright, bd=1, pady=3, padx=3)
        self.srf3.pack(fill="x")

        self.disp_inmap_window()
        self.inmap_window.withdraw()

        self.disp_empty_window()
        self.empty_window.withdraw()

        self.in_g2_ch.configure(state="disabled")
        self.ew_g2_ch.configure(state="disabled")

        self.close = Tkinter.Button(
            self.srf3, text="Close", command=self.rw.destroy)
        self.close.pack(side="right")

        tutp3 = "http://genesilico.pl/pyry3d/pyry_tutorial/Tutorial_part3.pdf"
        self.help = Tkinter.Button(
                        self.srf3, text="Help",
                        command=lambda: webbrowser.open(tutp3)
                        )
        self.help.pack(side="right")

    def display_box(self):

        box = self.box
        color = self.box_color

        bildpath = Paths.pluginpath + "/box.bild"

        bildfile = open(bildpath, "w")

        print >> bildfile, ".color", color[0][0] / 255.0, color[0][1] / 255.0,\
                           color[0][2] / 255.0, "\n", \
                           ".cylinder", box.xmin, box.ymin, box.zmin, \
                           box.xmax, box.ymin, box.zmin, "0.4", "\n", \
                           ".cylinder", box.xmin, box.ymin, box.zmin, \
                           box.xmin, box.ymin, box.zmax, "0.4", "\n", \
                           ".cylinder", box.xmin, box.ymin, box.zmin, \
                           box.xmin, box.ymax, box.zmin, "0.4", "\n", \
                           ".cylinder", box.xmax, box.ymin, box.zmax, \
                           box.xmax, box.ymin, box.zmin, "0.4", "\n", \
                           ".cylinder", box.xmax, box.ymin, box.zmax, \
                           box.xmax, box.ymax, box.zmax, "0.4", "\n", \
                           ".cylinder", box.xmax, box.ymin, box.zmax, \
                           box.xmin, box.ymin, box.zmax, "0.4", "\n", \
                           ".cylinder", box.xmin, box.ymax, box.zmax, \
                           box.xmin, box.ymax, box.zmin, "0.4", "\n", \
                           ".cylinder", box.xmin, box.ymax, box.zmax, \
                           box.xmax, box.ymax, box.zmax, "0.4", "\n", \
                           ".cylinder", box.xmin, box.ymax, box.zmax, \
                           box.xmin, box.ymin, box.zmax, "0.4", "\n", \
                           ".cylinder", box.xmax, box.ymax, box.zmax, \
                           box.xmax, box.ymax, box.zmin, "0.4", "\n", \
                           ".cylinder", box.xmax, box.ymax, box.zmin, \
                           box.xmin, box.ymax, box.zmin, "0.4", "\n", \
                           ".cylinder", box.xmax, box.ymax, box.zmin, \
                           box.xmax, box.ymin, box.zmin, "0.4", "\n"

        bildfile.close()

        runCommand("open " + bildpath)

    def handler(self):
        pass
