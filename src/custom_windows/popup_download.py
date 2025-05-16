import customtkinter as ctk

class ProgressBarWindow(ctk.CTkToplevel):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grab_set()  # Focus and hijack
        self.title(title)
        self.rowconfigure(2)
        self.columnconfigure(2)

        self.total_count = 0  # This will save the total items to download
        self.current_count = 0  # This will save the amount of items downloaded
        self.download_counter = ctk.CTkLabel(self, text="0/0")
        self.download_counter.grid(row=0, column=0, padx=(20, 0), pady=20)

        self.download_speed = ctk.CTkLabel(self, text="0.0Mb/s")
        self.download_speed.grid(row=0, column=1, padx=(0, 20), pady=20)

        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate", width=400)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, columnspan=2)

        self.grab_set()

    def set_total(self, total):
        self.total_count = total
        self.progress_bar.update()

    def update_progress(self, new_count, current_speed):
        """
        Used to update the progress_bar using portablemc DownloadProgressEvent

        Updates currently downloaded item count and speed

        ex: Installing a vanilla version
        """

        # Updated each progress event (not every time a download is completed, rather a tick)
        self.download_counter.configure(text=f"{new_count}/{self.total_count}")  # update current count
        self.download_counter.update()
        self.download_speed.configure(text=f"{format(current_speed / 1000000, '.2f')}Mb/s")  # Update speed
        self.download_speed.update()

        if new_count != self.current_count:
            # Update only when an item dwonload has beeen completed
            self.current_count += 1
            self.progress_bar.set(self.current_count / self.total_count)
            self.progress_bar.update()

        self.update()  # So that windows doesn't complain that the window stopped working

    def update_from_wget(self, new_count, total, _width):
        """
        Similar to self.update_progress but adapted to wget.download's callback

        For single file downloads only:
        It uses self.current and self.total for the item's size and "dynamically" calculates the speed
        (speed is Mb/tick, not Mb/s, though)

        _width is passed by wget, but I won't use it

        ex: Downloading git installer
        """
        self.download_counter.configure(text=f"{format(new_count/1000000, '.2f')}/{format(total/1000000, '.2f')} Mb")
        # update both current and total
        self.progress_bar.set(new_count / total)
        self.download_speed.configure(text=f"{format(new_count/1000000 - self.current_count/1000000, '.2f')}Mb/tick")
        self.current_count = new_count
        self.download_speed.update()
        self.download_counter.update()
        self.progress_bar.update()
        self.update()  # So that windows doesn't complain that the window stopped working

    def update_speed_from_wget(self, new_count, total, _width):
        """
        Simpler version of self.update_from_wget that only updates the speed, but doesn't touch current or total

        Use when downloading several  (more than 1) items with wget

        In this case, since I don't have speed, I will use the speed counter as downloaded size counter

        _width is passed by wget but I won'r use it

        ex: when downloading mods for a modpack
        """
        self.download_speed.configure(text=f"{format(new_count/1000000, '.2f')} / {format(total/1000000, '.2f')} Mb")
        self.update()

    def finish(self):
        self.grab_release()
        self.destroy()