"""
		welcome to

 ▄████▄   ██▀███ ▓██   ██▓ ██▓███  ▄▄▄█████▓ ██▓ ▄████▄   ▄▄▄       ██▓    
▒██▀ ▀█  ▓██ ▒ ██▒▒██  ██▒▓██░  ██▒▓  ██▒ ▓▒▓██▒▒██▀ ▀█  ▒████▄    ▓██▒    
▒▓█    ▄ ▓██ ░▄█ ▒ ▒██ ██░▓██░ ██▓▒▒ ▓██░ ▒░▒██▒▒▓█    ▄ ▒██  ▀█▄  ▒██░    
▒▓▓▄ ▄██▒▒██▀▀█▄   ░ ▐██▓░▒██▄█▓▒ ▒░ ▓██▓ ░ ░██░▒▓▓▄ ▄██▒░██▄▄▄▄██ ▒██░    
▒ ▓███▀ ░░██▓ ▒██▒ ░ ██▒▓░▒██▒ ░  ░  ▒██▒ ░ ░██░▒ ▓███▀ ░ ▓█   ▓██▒░██████▒
░ ░▒ ▒  ░░ ▒▓ ░▒▓░  ██▒▒▒ ▒▓▒░ ░  ░  ▒ ░░   ░▓  ░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░▓  ░
  ░  ▒     ░▒ ░ ▒░▓██ ░▒░ ░▒ ░         ░     ▒ ░  ░  ▒     ▒   ▒▒ ░░ ░ ▒  ░
░          ░░   ░ ▒ ▒ ░░  ░░         ░       ▒ ░░          ░   ▒     ░ ░   
░ ░         ░     ░ ░                        ░  ░ ░            ░  ░    ░  ░
░                 ░ ░                           ░                          
"""

from PIL.Image import open
import customtkinter as ctk
from tkinter import PhotoImage
from utils.misc import setup_db, get_data
from utils.add_vault_dialog import AddVaultDialog
from utils.delete_vault_dialog import DeleteVaultDialog
from utils.enter_password_dialog import EnterPasswordDialog

DB_FILE = "db.sqlite"
ICON_PNG = "assets/icon.png"
VAULT_IMG_PATH = "assets/lock.png"
DEFAULT_WINDOW_WIDTH = 1100
DEFAULT_WINDOW_HEIGHT = 580
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Cryptical(ctk.CTk):
    """The main class, representing the application itself."""

    # Used later to detect whether these dialogs exist already or not.
    del_vault_dialog = add_vault_dialog = enter_pwd_dialog = None

    def __init__(self) -> None:
        """Initializes the app and its components."""

        super().__init__()  # call base constructor

        # Set default window props
        self.title("Cryptical")  # title
        self.wm_iconphoto(False, PhotoImage(file=ICON_PNG))  # icon
        self.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")  # dimensions
        self.configure(fg_color="#141212")  # bg color
        self.rowconfigure(1, weight=1)  # enable horizontal scaling on resize
        self.columnconfigure(0, weight=1)  # enable vertical scaling on resize

        # setup application database
        setup_db(DB_FILE)

        # setup application ui
        self.build_ui(DB_FILE)

    def build_ui(self, db_file: str) -> None:
        """Creates the necessary widgets for the app UI.

        Args:
         - db_file: filename of the database to use.

        Returns: None
        """

        # HEADER UI
        # header main frame
        self.header = ctk.CTkFrame(self, fg_color="#212121", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="new")

        # header 'CRYPTICAL' label
        self.header.label = ctk.CTkLabel(self.header, text="Cryptical")
        self.header.label.cget("font").configure(size=20, weight="bold")
        self.header.label.pack(side="left", padx=20, pady=10)

        # header 'add vaults' button
        self.header.button_add_vaults = ctk.CTkButton(
            self.header,
            text="Add Vaults",
            command=lambda db=db_file: self.init_add_vault_dialog(db_file),
        )
        self.header.button_add_vaults.pack(side="right", padx=0, pady=10)

        # header 'delete vaults' button
        self.header.button_del_vaults = ctk.CTkButton(
            self.header,
            text="Delete Vaults",
            command=lambda: self.init_delete_vault_dialog(db_file),
        )
        self.header.button_del_vaults.pack(
            side="right", padx=20, pady=10, before=self.header.button_add_vaults
        )

        # VAULT UI
        VAULTS_PER_ROW = 5
        available_vaults = get_data(db_file, "SELECT * FROM vaults;")

        # vault container
        self.vault_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.vault_container.grid(row=1, column=0, sticky="nsew")

        # setup vault container's grid
        rows = (len(available_vaults) // VAULTS_PER_ROW) + 1
        for i in range(rows):
            self.vault_container.rowconfigure(i, weight=1)
        for i in range(VAULTS_PER_ROW):
            self.vault_container.columnconfigure(i, weight=1)

        for i, vault in enumerate(available_vaults):
            # Temporary vault frame
            tmpv_frame = ctk.CTkFrame(
                self.vault_container, fg_color="#212121", corner_radius=15
            )
            r = (i) // VAULTS_PER_ROW
            c = (i) % VAULTS_PER_ROW
            tmpv_frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

            # temporary vault image
            tmpv_img = ctk.CTkImage(
                light_image=open(VAULT_IMG_PATH),
                dark_image=open(VAULT_IMG_PATH),
                size=(50, 60),
            )
            tmpv_img_frame = ctk.CTkLabel(tmpv_frame, text="", image=tmpv_img)
            tmpv_img_frame.pack(expand=True, fill="x", ipady=10, padx=40, pady=10)

            # temporary vault label
            tmpv_label = ctk.CTkLabel(tmpv_frame, text=vault[1], justify="center")
            tmpv_label.cget("font").configure(size=18, weight="bold")
            tmpv_label.pack(expand=True, padx=20)

            # temporary vault button
            tmpv_button = ctk.CTkButton(
                tmpv_frame,
                text="Enter Vault",
                command=lambda vid=vault[0]: self.init_enter_pwd_dialog(vid, db_file),
            )
            tmpv_button.pack(expand=True, pady=15, padx=20)

    def init_add_vault_dialog(self, db_file: str) -> None:
        """Initializes the Add Vault Dialog if it does not already exist.

        Args:
            db_file (str): The filename of the database to use.

        Returns:
            None
        """

        # Check if the AddVaultDialog has already been created and exists on the screen
        if self.add_vault_dialog is not None and self.add_vault_dialog.winfo_exists():
            # If it does, give focus to the dialog and return
            self.add_vault_dialog.focus()
            return

        # If the dialog does not exist, create a new instance of AddVaultDialog
        self.add_vault_dialog = AddVaultDialog(db_file, self)

    def init_delete_vault_dialog(self, db_file: str) -> None:
        """Initializes the Delete Vault Dialog if it does not already exist.

        Args:
            db_file (str): The filename of the database to use.

        Returns:
            None
        """

        # Check if the DeleteVaultDialog has already been created and exists on the screen
        if self.del_vault_dialog is not None and self.del_vault_dialog.winfo_exists():
            # If it does, give focus to the dialog and return
            self.del_vault_dialog.focus()
            return

        # If the dialog does not exist, create a new instance of AddVaultDialog
        self.del_vault_dialog = DeleteVaultDialog(db_file, self)

    def init_enter_pwd_dialog(self, vid: int, db_file: str) -> None:
        """Initializes the Enter Password Dialog if it does not already exist.

        Args:
         - vid (int): The ID of the vault to open.
         - db_file (str): The filename of the database to use.

        Returns: None
        """

        # Get the available vaults from the database
        available_vaults = get_data(db_file, "SELECT * FROM vaults;")

        # Find the vault with the specified ID
        for vault in available_vaults:
            if vid == vault[0]:
                selected_vault = vault
                break
        else:
            raise ValueError(f"No vault found with ID {vid}")

        # Create or focus the Enter Password Dialog
        if self.enter_pwd_dialog is None or not self.enter_pwd_dialog.winfo_exists():
            self.enter_pwd_dialog = EnterPasswordDialog(db_file, selected_vault)
        else:
            self.enter_pwd_dialog.focus()


def main():
    app = Cryptical()
    app.mainloop()


main()
