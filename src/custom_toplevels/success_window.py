import customtkinter as ctk

class SuccessWindow(ctk.CTkToplevel):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grab_set()  # Focus and hijack
        self.title(app.translations["status_success"])
        self.rowconfigure(3)
        self.columnconfigure(1)

        self.header = ctk.CTkLabel(self, text=app.translations["status_success"])
        self.header.grid(row=0, column=0, pady=(10, 0))

        self.disclaimer_frame = ctk.CTkFrame(self)
        self.disclaimer_frame.grid(row=1, column=0, sticky="nswe", padx=10, pady=20)
        self.textbox = ctk.CTkTextbox(self.disclaimer_frame, width=500, height=100)
        self.textbox.insert("0.0", app.translations["launched_notice"])
        self.textbox.configure(state="disabled")
        self.textbox.grid()

        self.OK = ctk.CTkButton(self, text="OK", width=60, height=30, command=self.close)
        self.OK.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="nswe")

    def close(self):
        self.grab_release()
        self.destroy()