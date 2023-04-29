import hashlib
import customtkinter as ctk
from utils.vault_window import VaultWindow


class EnterPasswordDialog(ctk.CTkToplevel):
    pwd_error = False
    vault_window = None
    win_height = 150
    win_width = 400

    def __init__(self, db_file: str, vault: tuple, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Call base constructor

        # Set up the dialog window
        self.title("Enter Password")
        self.geometry(f"{self.win_width}x{self.win_height}")

        # Create the "Enter Password" label and entry box
        self.enter_pwd_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.enter_pwd_frame.rowconfigure(0, weight=1)
        self.enter_pwd_frame.columnconfigure(0, weight=1)
        self.enter_pwd_frame.columnconfigure(1, weight=3)
        self.enter_pwd_frame.pack(expand=True, fill="x")

        self.enter_pwd_label = ctk.CTkLabel(
            self.enter_pwd_frame, text="Type Vault Password:"
        )
        self.enter_pwd_label.cget("font").configure(size=16)
        self.enter_pwd_label.grid(row=0, column=0, sticky="nsew")

        self.enter_pwd_entry = ctk.CTkEntry(self.enter_pwd_frame, show="●")
        self.enter_pwd_entry.grid(row=0, column=1, padx=10, sticky="nsew")

        # Create the "Open Vault" and "Cancel" buttons
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.rowconfigure(0, weight=1)
        self.buttons_frame.columnconfigure((0, 1), weight=1)
        self.buttons_frame.pack(expand=True, fill="x")

        self.open_vault_button = ctk.CTkButton(
            self.buttons_frame,
            text="Open Vault",
            command=lambda: self.check_pwd(db_file, vault),
        )
        self.open_vault_button.grid(row=0, column=0, padx=10)

        self.cancel_button = ctk.CTkButton(
            self.buttons_frame, text="Cancel", command=self.destroy
        )
        self.cancel_button.grid(row=0, column=1, padx=10)

    def check_pwd(self, db_file: str, vault: tuple) -> None:
        """
        Check if the entered password matches the hash stored in the database.
        If the password is incorrect, display an error message. Otherwise,
        create a new VaultWindow instance and open the vault.
        """
        emp = self.enter_pwd_entry.get()
        hmp = hashlib.sha256((emp + vault[3]).encode()).hexdigest()

        if hmp != vault[2]:
            # Display error message if the password is incorrect
            if not self.pwd_error:
                self.win_height += 50
                self.pwd_error = True
                self.pwd_err_frame = ctk.CTkFrame(
                    self, fg_color="#141212", corner_radius=10
                )
                self.pwd_err_frame.pack(expand=True, fill="x", padx=10)
                self.pwd_err_label = ctk.CTkLabel(
                    self.pwd_err_frame,
                    text="Incorrect Password!",
                    text_color="#ff5050",
                    wraplength=350,
                    justify="left",
                )
                self.pwd_err_label.pack(expand=True, ipadx=10, ipady=10)
        else:
            # Open the vault if the password is correct
            self.pwd_error = False
            self.destroy()
            if self.vault_window is None or not self.vault_window.winfo_exists():
                self.vault_window = VaultWindow(db_file, vault, emp)
            else:
                self.vault_window.focus()
