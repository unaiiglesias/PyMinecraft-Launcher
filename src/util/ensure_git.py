from subprocess import call
import customtkinter as ctk
from app_utils.launch_data_manager import LaunchData
from custom_toplevels.popup_download import download_stuff
import os
from custom_toplevels.popup_wait import popup_wait_for_task


class InstallGitPopup(ctk.CTkToplevel):
    """
    Modpack functionality requires git, we don't want the user manually installing git. This popup will inform the user
    that git needs to be installed and do it for them.

    We'll give them 2 choices: Regular or Portable installation. Of course the user can refuse to install git, in which
    case we'll abort the launch.
    """

    def __init__(self, app, launch_data : LaunchData, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grab_set()
        self.launch_data = launch_data
        self.app = app
        self.title(app.translations["git_not_found_title"])
        self.rowconfigure(3)
        self.columnconfigure(1)

        """ Textbox informing that git must be installed and explaining the choices"""
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.grid(row=0, column=0, sticky="nswe", padx=20, pady=10)
        self.textbox = ctk.CTkTextbox(self.text_frame, width=500, height=155)
        self.textbox.configure(wrap="word")  # If EOL, dont cut the word in half
        self.textbox.insert("0.0", app.translations["git_not_found_text"])
        self.textbox.configure(state="disabled")
        self.textbox.grid()

        """ The three buttons"""
        # One will return True on press and the other one False, both will close the window
        self.regular_installation_button = ctk.CTkButton(self, text=app.translations["git_regular_install_button"], width=60, height=30, command=self.perform_regular_installation)
        self.regular_installation_button.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="nswe")
        self.regular_installation_button = ctk.CTkButton(self, text=app.translations["git_portable_install_button"], width=60, height=30, command=self.perform_portable_installation)
        self.regular_installation_button.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="nswe")
        self.refuse_but = ctk.CTkButton(self, text=app.translations["git_dont_install_button"], width=60, height=30, command=self.refuse)
        self.refuse_but.grid(row=3, column=0, padx=5, pady=(0, 10), sticky="nswe")

        self.choice = False  # Has the user chosen to install git? True : install, False : Don't install

    def perform_regular_installation(self):
        # The user has chosen to install git the regular way
        # Download the executable and install it

        git_link = "https://github.com/git-for-windows/git/releases/download/v2.49.0.windows.1/Git-2.49.0-64-bit.exe"
        # Using a hard coded link is not the best idea. It would be better to fetch the latest version from GitHub, but we don't really need the latest version for this, just a working one.
        # Plus, this makes the installation faster

        res = download_stuff(".", {"git_for_calvonetta.exe": git_link}, "git")
        # TODO: Log download failed properly
        if len(res) > 0:  # This means the download of the installer failed
            print("ERROR: Git installer download failed")
            self.choice = False
            return

        # This is where the downloaded file is now
        download_path = os.getcwd() + "\\git_for_calvonetta.exe"

        # At this point, we should have git_for_calvonetta.exe downloaded

        os.system(f"'{download_path}' /SILENT")  # This will automatically install git :D
        # (will trigger UAC prompt, though)
        os.remove(f"'{download_path}'")  # Remove the executable
        # Close the pop-up
        self.choice = True
        self.destroy()

        # TODO: Shouldn't we close the launcher completely and re-open it so that it can detect the git installation?

    def perform_portable_installation(self):
        # The user has chosen to install the portable version of git
        # Download the compressed file and extract it in /portable-git

        git_link = "https://github.com/git-for-windows/git/releases/download/v2.49.0.windows.1/PortableGit-2.49.0-64-bit.7z.exe"
        # Using a hard coded link is not the best idea. It would be better to fetch the latest version from GitHub, but we don't really need the latest version for this, just a working one.
        # Plus, this makes the installation faster

        res = download_stuff(".", {"portable_git_for_calvonetta.7z.exe": git_link}, "git")
        # TODO: Log download failed properly
        if len(res) > 0:  # This means the download of the installer failed
            print("ERROR: Portable Git installer download failed")
            self.choice = False
            return

        # This is where the downloaded file is now
        download_path = os.getcwd() + "\\portable_git_for_calvonetta.7z.exe"
        extract_to = os.getcwd() + "\\portable-git"

        # At this point, we should have portable_git_for_calvonetta.7z.exe downloaded
        popup_wait_for_task(self.app, self.app.translations["git_portable_extracting_text"], lambda : os.system(f"'{download_path}' -o '{extract_to}' -y"))

        # (will trigger UAC prompt, though)
        os.remove(f"'{download_path}'")  # Remove the executable
        # Close the pop-up
        self.choice = True
        self.destroy()

    def refuse(self):
        self.choice = False # Default value, but anyway :D
        self.destroy()

    def get_choice(self):
        return self.choice


def is_git_installed():
    """
    Return true if git is installed and false otherwise
    """

    #return False # DEBUG

    # Check if portable git installation present
    try:
        portable_git_path = os.getcwd() + "/portable-git"
        call(f"{portable_git_path}/cmd/git --version") # If this works, portable git installed
        os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = fr'{portable_git_path}\cmd\git.exe' # Tell GitPython to use that git
        return True
    except FileNotFoundError:
        pass

    # Check if regular git installation present
    try:
        call("git --version")
        return True
    except FileNotFoundError:
        pass

    return False


def ensure_git(app, launch_data):
    """
    Checks whether git is installed or not:
     - if git is installed, returns true
     - if git is not installed pops up toplevel window to help the user install git
      - If the user doesn't want to install git, returns false
      - If the user wants to install git, it aids it with InstallGitPopup and recursively calls itself
    """

    if is_git_installed():
        # In this case, we don't need to do anything else
        return True

    msg = InstallGitPopup(app, launch_data)
    msg.wait_window()

    git_installed = msg.get_choice() # Did the user choose to install git

    if not git_installed:
        # The user has chosen not to install git, this will abort the modpack launch
        return False

    return is_git_installed()  # In case the user stopped the installation (or it failed)