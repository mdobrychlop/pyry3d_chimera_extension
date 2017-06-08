import Tkinter


class Display:

    def please_wait_window(self, reason):
        """
        Get rid of this thing ASAP.
        """
        self.please_wait = Tkinter.Tk()
        self.please_wait.title("Please wait")
        please_wait = self.please_wait

        wait_frame = Tkinter.Frame(
                      please_wait,
                      bd=1,
                      relief="ridge",
                      pady=5,
                      padx=5
                      )
        wait_frame.pack(fill="x")

        please_wait_label = Tkinter.Label(
                             wait_frame,
                             text="Please wait. "+str(reason)
                             )
        please_wait_label.pack()
