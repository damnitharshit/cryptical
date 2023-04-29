import sqlite3, hashlib
import customtkinter as ctk
from utils.misc import get_data


class DeleteVaultDialog(ctk.CTkToplevel):
    pwd_error = False
    win_height = 200
    win_width = 400

    def __init__(self, db_file: str, parent: ctk.CTk, *args, **kwargs):
        """Initialize the Delete Vault Dialog."""

        super().__init__(*args, **kwargs)  # call base constructor

        # Set default window props
        self.title("Delete Vaults")
        self.geometry(f"{self.win_width}x{self.win_height}")

        # setup inteface
        self.build_ui(db_file, parent)

    def build_ui(self, db_file: str, parent: ctk.CTk) -> None:
        """
        Sets up the user interface for the application. Creates the necessary
        frames, labels, entries, and buttons for the user to interact with.
        Args:
            db_file (str): The path to the database file.
            parent (tk.Tk): The parent window of the dialog.
        """

        # Connect to the database and retrieve available vaults
        available_vaults = get_data(db_file, "SELECT * FROM vaults;")

        # Helper function for creating a frame with a label and either an entry or option menu
        def create_frame(master, label_text, entry_show=None):
            """
            Creates a frame with a label and either an entry or option menu.
            Args:
                master (tk.Widget): The parent widget.
                label_text (str): The text to display in the label.
                entry_show (str): The character to display instead of the actual input.
                    Defaults to None if an option menu should be created instead.
            Returns:
                tk.Widget: Either a CTkEntry or CTkOptionMenu widget.
            """
            # Create the frame and configure it
            frame = ctk.CTkFrame(master, fg_color="transparent")
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=3)
            frame.pack(expand=True, fill="x")

            # Create the label and configure it
            label = ctk.CTkLabel(frame, text=label_text)
            label.cget("font").configure(size=16)
            label.grid(row=0, column=0, sticky="nsew")

            # Create either an entry or option menu and configure it
            entry = ctk.CTkEntry(frame, show=entry_show) if entry_show else None
            if entry:
                entry.grid(row=0, column=1, padx=10, sticky="nsew")
            else:
                optionmenu = ctk.CTkOptionMenu(
                    frame, values=[vault[1] for vault in available_vaults]
                )
                optionmenu.grid(row=0, column=1, padx=10, sticky="nsew")
            return entry or optionmenu

        # Create the Select Vault option menu and Enter Vault Password entry
        self.select_vault_optionmenu = create_frame(self, "Select Vault:")
        self.enter_mp_entry = create_frame(self, "Enter Vault Password:", "●")

        # Create the Delete Vault and Cancel buttons
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.rowconfigure(0, weight=1)
        self.buttons_frame.columnconfigure((0, 1), weight=1)
        self.buttons_frame.pack(expand=True, fill="x")
        self.delete_button = ctk.CTkButton(
            self.buttons_frame,
            text="Delete Vault",
            command=lambda: self.on_click_delete_vault(db_file, parent),
        )
        self.delete_button.grid(row=0, column=0, padx=10)
        self.cancel_button = ctk.CTkButton(
            self.buttons_frame, text="Cancel", command=self.destroy
        )
        self.cancel_button.grid(row=0, column=1, padx=10)

    def on_click_delete_vault(self, db_file: str, parent: ctk.CTk) -> None:
        """
        Handles the "Delete Vault" button click event.

        Args:
            db_file (str): The path to the database file.
            parent (ctk.CTk): The parent widget.

        Returns: None
        """
        # Get the available vaults from the database.
        available_vaults = get_data(db_file, "SELECT * FROM vaults;")

        # Get the name of the selected vault.
        name = self.select_vault_optionmenu.get()

        # Find the selected vault in the list of available vaults.
        vault = [_ for _ in available_vaults if name == _[1]][0]

        # Get the password entered by the user and hash it with the vault's salt.
        pwd = self.enter_mp_entry.get()
        hpwd = hashlib.sha256((pwd + vault[3]).encode()).hexdigest()

        # Check if the entered password matches the password for the selected vault.
        if hpwd != vault[2]:
            # If the password is incorrect, display an error message.
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
            # If the password is correct, remove the error message (if it exists).
            if self.pwd_error:
                self.win_height -= 50
                self.pwd_err_frame.destroy()
                self.pwd_error = False

        # Resize the window to fit the contents.
        self.geometry(f"{self.win_width}x{self.win_height}")

        # If there are no password errors, delete the selected vault from the database.
        if not self.pwd_error:
            with sqlite3.connect(db_file) as conn:
                conn.cursor().execute(f"DELETE FROM vaults WHERE vid={vault[0]};")
                conn.commit()

            # Rebuild the parent UI to update the list of vaults.
            parent.build_ui(db_file)

            # Close the current window.
            self.destroy()
