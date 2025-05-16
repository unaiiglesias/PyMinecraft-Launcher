from subprocess import call
import customtkinter as ctk
from wget import download
from src.custom_windows.popup_download import ProgressBarWindow
import os


class InstallGitPrompt(ctk.CTkToplevel):
    """
    Reusable window with a message box and 2 buttons
    """

    def __init__(self, title, text, but1, but2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grab_set()
        self.title(title)
        self.rowconfigure(3)
        self.columnconfigure(1)

        """ Textbox stuff """
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.grid(row=0, column=0, sticky="nswe", padx=20, pady=10)
        self.textbox = ctk.CTkTextbox(self.text_frame, width=500, height=100)
        self.textbox.insert("0.0", text)
        self.textbox.configure(state="disabled")
        self.textbox.grid()

        """ The two buttons"""
        # One will return True on press and the other one False, both will close the window
        self.confirm_but = ctk.CTkButton(self, text=but1, width=60, height=30, command=self.confirm)
        self.confirm_but.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="nswe")
        self.refuse_but = ctk.CTkButton(self, text=but2, width=60, height=30, command=self.refuse)
        self.refuse_but.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="nswe")

        self.selection = False  # default value

    def close(self):
        self.grab_release()
        self.destroy()

    def confirm(self):
        self.selection = True
        self.close()

    def refuse(self):
        self.selection = False
        self.close()

    def show(self):
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.close)
        self.wait_window()
        return self.selection


def is_git_installed():
    """
    Return true if git is installed and false instead
    """
    try:
        call("git --version")
        return True
    except FileNotFoundError:
        return False


def ensure_git(app, launch_data):
    """
    Checks wether git is installed or not:
     - if git is inastalled, returns true
     - if git is not installed pops up toplevel window to help the user install git
      - If the user doesnt want to install git, returns false
      - If the user wants to install git, it downloads the installer and runs it
    """

    if is_git_installed():
        # In this case, we dont need to do anything else
        return True

    msg = InstallGitPrompt(app.translations["git_not_found_title"], app.translations["git_not_found_text"],
                           app.translations["git_install_button"], app.translations["git_dont_install_button"])

    install = msg.show()

    if not install:
        # The user has chosen not to install git, this will abort the modpack launch
        return False

    # The user has chosen to install git, download the installer, I'll use a hard-coded release
    # (we don't need the latest and it's more comfortable this way)

    git_link = "https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe"
    download_path = launch_data.path + "/git_for_calvonetta.exe"

    print("DOWNLOADING GIT")

    progress_bar = ProgressBarWindow("git")
    progress_bar.set_total(1)

    download(git_link, out=download_path, bar=progress_bar.update_from_wget)
    progress_bar.finish()

    # At this point, we should have git_for_calvonetta.exe downloaded

    os.system(download_path + " /SILENT")  # This will automatically install git automatically :D
    # (will trigger UAC prompt, though)
    os.remove(download_path)  # Remove the executable

    return is_git_installed()  # In case the user stopped the installation