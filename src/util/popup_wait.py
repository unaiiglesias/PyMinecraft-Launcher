from concurrent.futures import ThreadPoolExecutor, Future
import customtkinter as ctk
from time import sleep
import src.main

def popup_wait_for_task(master : src.main.App, message : str, function, *args):
    """
    Displays a popup loading screen with the given message while it executes the given function on the background
    Finally, returns the result of the function execution

    Args:
        master: Main GUI window, used to hijack execution
        message: Message to be displayed in waiting window. Should describe the task being performed
        function: Function to be run in the background
        *args: Arguments to function call (positional only, not named)

    Returns:
        Result of function execution with given positional arguments
    """

    with ThreadPoolExecutor() as executor:
        # Launch task in the background
        future = executor.submit(function, *args)

        # Start loading screen
        modal = TaskPopup(master = master, message = message, future = future)
        if modal.winfo_exists(): # If execution is too fast, this might fail
            modal.grab_set()
            modal.wait_window()

        # By this point future already finished
        return future.result()


class TaskPopup(ctk.CTkToplevel):

    """
        Some of the tassk that PyMinecraft launcher has to perform take a bit of time and block the main thread.
        To prevent the GUI from getting stuck we want to run said tasks on a separate Thread. However, we usually
        don't want to allow the user to use the interface but just don't want the GUI it to hang.
        Instead, TaskPopup displays a "loading screen" so that the user has some feedback while we run stuff in the
        background.

        Do not use this class directly. Instead, launch it with popup_wait_for_task function.

        This class displays a loading slider and a given message and hijacks main thread execution while it waits
        for thread to finish. Once thread is done, it just disposes itself.
    """

    WIDTH = 400
    HEIGHT = 300

    def __init__(self, master : src.main.App, message : str, future : Future):
        super().__init__()
        #self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.title(master.translations["popup_wait_title"])

        self.future = future
        master.grab_set()

        # Responsiveness
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=5)

        self.title = ctk.CTkLabel(self, text=message)
        self.title.grid(row=0, sticky="nswe", pady=20)

        self.loading_bar = ctk.CTkProgressBar(self, mode="indeterminate", width = 400)
        self.loading_bar.grid(row=1)
        self.loading_bar.start()

        # Wait for thread to end
        self.wait()

    def wait(self):
        if not self.future.done():
            self.after(100, self.wait)
            return
        self.destroy()


def main():
    """
    This function is only for debugging purpouses
    """
    app = ctk.CTk()
    app.translations = {"popup_wait_title" : "Please wait..."}

    print("TAREA 1")
    popup_wait_for_task(app, "Haciendo un print", print, "Pa ti mi cola")

    # NOTE: Leaves test.txt file that has to be removed manually
    print("TAREA 2")
    with open("test.txt", "w") as file:
        popup_wait_for_task(app,"Escribiendo en archivo", file.write, "Pa ti mi cola")

    print("TAREA 3")
    res = popup_wait_for_task(app, "Sumando", sum, (1, 2, 3, 4))
    print(f"Resultado de la suma: {res}")

    print("TAREA 4")
    popup_wait_for_task(app,"Esperando 10 segundos...", sleep,10)

    app.mainloop()


if __name__ == "__main__":
    main()