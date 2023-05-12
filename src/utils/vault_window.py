import sqlite3
import tkinter as tk
import customtkinter as ctk
from utils.misc import decrypt, get_data
from utils.add_entry_dialog import AddEntryDialog


class VaultWindow(ctk.CTkToplevel):
    """A custom TopLevel window that displays a password vault.

    Attributes:
        add_entry_dialog (AddRecordDialog): The add record dialog.
        win_height (int): The window height.
        win_width (int): The window width.
    """

    add_entry_dialog = None
    win_height = 580
    win_width = 1100

    def __init__(self, db_file: str, vault: tuple, vmp: str, *args, **kwargs):
        """Initializes the window.

        Args:
            db_file (str): The path to the database file.
            vault (tuple): The vault information.
            vmp (str): The vault master password.
            *args: Arguments to be passed to the parent constructor.
            **kwargs: Keyword arguments to be passed to the parent constructor.
        """
        super().__init__(*args, **kwargs)  # call base constructor
        vid = vault[0]
        vname = vault[1]

        # Set window props
        self.title(f"{vname}")  # title
        self.geometry(f"{self.win_width}x{self.win_height}")  # dimensions
        self.configure(fg_color="#141212")  # bg color
        self.rowconfigure(1, weight=1)  # enable horizontal scaling on resize
        self.columnconfigure(0, weight=1)  # enable vertical scaling on resize

        # Build the UI
        self.build_ui(db_file, vmp, vname, vid)

    def build_ui(self, db_file: str, vmp: str, vname: str, vid: int):
        """Builds the user interface.

        Args:
            db_file (str): The path to the database file.
            vmp (str): The vault master password.
            vname (str): The vault name.
            vid (int): The vault ID.
        """
        # Header UI
        self.header = ctk.CTkFrame(self, fg_color="#212121", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="new")
        self.header.label = ctk.CTkLabel(self.header, text=vname)
        self.header.label.cget("font").configure(size=20, weight="bold")
        self.header.label.pack(side="left", padx=20, pady=10)

        # Add Entry Button
        self.header.add_entry_button = ctk.CTkButton(
            self.header,
            text="Add Password",
            command=lambda: self.init_add_entry_dialog(db_file, vmp, vname, vid),
        )
        self.header.add_entry_button.pack(side="right", padx=20, pady=10)

        # Entry Table UI
        available_entries = get_data(db_file, f"SELECT * FROM entries WHERE vid={vid};")

        # Create scrollable frame for the table
        self.table_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_frame.grid(row=1, column=0, sticky="nsew")

        # Create frame for column names
        self.colname_frame = ctk.CTkFrame(
            self.table_frame, fg_color="#212121", corner_radius=5
        )
        self.colname_frame.rowconfigure(0, weight=1)
        self.colname_frame.columnconfigure(0, weight=3)
        self.colname_frame.columnconfigure(1, weight=2)
        self.colname_frame.pack(expand=True, fill="x", padx=10, pady=10, ipady=10)

        # Create label for "Site :: Password" column
        self.colname_splabel = ctk.CTkLabel(self.colname_frame, text="Site :: Password")
        self.colname_splabel.cget("font").configure(size=18, weight="bold")
        self.colname_splabel.grid(row=0, column=0)

        # Create label for "Options" column
        self.colname_olabel = ctk.CTkLabel(self.colname_frame, text="Options")
        self.colname_olabel.cget("font").configure(size=18, weight="bold")
        self.colname_olabel.grid(row=0, column=1)

        # Create UI elements for each password entry
        for i, entry in enumerate(available_entries):
            # Create frame for password entry
            tmpe_frame = ctk.CTkFrame(
                self.table_frame, fg_color="#212121", corner_radius=5
            )
            tmpe_frame.rowconfigure(0, weight=1)
            tmpe_frame.columnconfigure(0, weight=5)
            tmpe_frame.columnconfigure(1, weight=1)
            tmpe_frame.pack(expand=True, fill="x", padx=10, pady=5, ipady=5)

            # Get the site and password for the current entry
            site = entry[2]
            pwd = decrypt(key=vmp, ciphertext=entry[3])
            tmpe_label = ctk.CTkLabel(tmpe_frame, text=f"{site} :: {pwd}")
            tmpe_label.cget("font").configure(size=16)
            tmpe_label.grid(row=0, column=0)
            tmpe_buttons_frame = ctk.CTkFrame(tmpe_frame, fg_color="transparent")
            tmpe_buttons_frame.grid(row=0, column=1, pady=5)

            # Create copy button for the current entry
            tmpe_copy_button = ctk.CTkButton(
                tmpe_buttons_frame,
                text="Copy",
                command=lambda: self.copy_to_clipboard(vmp, entry[3]),
            )
            tmpe_copy_button.pack(side="left")

            # Create delete button for the current entry
            tmpe_del_button = ctk.CTkButton(
                tmpe_buttons_frame,
                text="Delete",
                command=lambda pid=entry[0]: self.delete_entry(
                    db_file, vmp, vname, vid, pid
                ),
            )
            tmpe_del_button.pack(after=tmpe_copy_button, padx=10)

    def delete_entry(self, db_file, vmp, vname, vid, pid) -> None:
        """Delete a record from the database with a given pid (primary ID).

        Args:
            db_file (str): path to the database file
            vmp (bytes): the master password used to decrypt the database
            vname (str): the name of the vault to which the record belongs
            vid (int): the ID of the vault to which the record belongs
            pid (int): the primary ID of the record to delete

        Returns: None
        """
        with sqlite3.connect(db_file) as conn:
            conn.cursor().execute(f"DELETE FROM entries WHERE pid={pid};")
            conn.commit()
        self.build_ui(db_file, vmp, vname, vid)

    def init_add_entry_dialog(self, db_file, vmp, vname, vid) -> None:
        """Initializes the Add Entry Dialog if it doesn't exist already.

        Args:
            db_file (str): path to the database file
            vmp (bytes): the master password used to decrypt the database
            vname (str): the name of the vault to which the record belongs
            vid (int): the ID of the vault to which the record belongs

        Returns: None
        """
        # Check if the AddEntryDialog has already been created and exists on the screen
        if self.add_entry_dialog is not None and self.add_entry_dialog.winfo_exists():
            # If it does, give focus to the dialog and return
            self.add_entry_dialog.focus()
            return

        # If the dialog does not exist, create a new instance of AddEntryDialog
        self.add_entry_dialog = AddEntryDialog(db_file, vmp, vname, vid, self)

    def copy_to_clipboard(self, vmp, esp) -> None:
        """Copies a password to the system clipboard.

        Args:
            pwd: str, the password to copy

        Returns: None
        """
        pwd = decrypt(vmp, esp)
        self.clipboard_append(pwd)
        self.update()
