import customtkinter as ctk
from utils.misc import add_entry_to_db, get_data


class AddEntryDialog(ctk.CTkToplevel):
    name_error = False
    noname_error = False
    usedname_error = False
    pwd_error = False
    nopwd_error = False
    diffpwds_error = False
    win_height = 200
    win_width = 400
    PROHIBITED_NAME_CHARS = " \"'(),/:;<>?[\]`{|}~"
    PROHIBITED_PWD_CHARS = " \"'(),/:;<>?[\]`{|}"

    def __init__(self, db_file, vmp, vname, vid, parent, *args, **kwargs):
        """Initialize the Add Entry Dialog."""

        super().__init__(*args, **kwargs)  # call base constructor

        # Set default window props
        self.title("Add Entry")  # title
        self.geometry(f"{self.win_width}x{self.win_height}")  # dimensions

        # Setup dialog UI
        self.build_ui(db_file, vmp, vname, vid, parent)

    def build_ui(self, db_file, vmp, vname, vid, parent) -> None:
        """Initialize the widgets necessary for functioning of the add entry dialog.

        Args:
            db_file (str): The database file name.
            vmp (str): The vault master password.
            vname (str): The vault name.
            vid (int): The vault id.
            parent (ctk.CTk): The parent widget for the add vault dialog.

        Returns:
            None
        """

        def create_entry(parent: ctk.CTkToplevel, label_text: str, for_pwd=False):
            """Create a label-entry pair for the add vault dialog.

            Args:
                parent (ctk.CTk): The parent widget for the label-entry pair.
                label_text (str): The text for the label.
                for_pwd (bool, optional): A flag indicating if the entry is for a password.
                    Defaults to False.

            Returns:
                tuple: A tuple containing the frame, label, and entry widgets.
            """

            frame = ctk.CTkFrame(parent, fg_color="transparent")
            label = ctk.CTkLabel(frame, text=label_text)
            entry = ctk.CTkEntry(frame, show="●") if for_pwd else ctk.CTkEntry(frame)
            label.cget("font").configure(size=16)
            label.grid(row=0, column=0, sticky="nsew")
            entry.grid(row=0, column=1, padx=10, sticky="nsew")
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure((0, 1), weight=1)
            frame.pack(expand=True, fill="x")
            return frame, label, entry

        # For Site Name
        self.sname_frame, self.sname_label, self.sname_entry = create_entry(
            self, "Type Site Name: "
        )
        self.sname_entry.focus_set()

        # For Site Password
        self.spwd_frame, self.spwd_label, self.spwd_entry = create_entry(
            self, "Type Site Password:", for_pwd=True
        )

        # For Re-Typed Password
        self.srpwd_frame, self.srpwd_label, self.srpwd_entry = create_entry(
            self, "Re-Type Password:", for_pwd=True
        )

        # For Vault Buttons
        self.ebtn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.ebtn_create_entry = ctk.CTkButton(
            self.ebtn_frame,
            text="Create Entry",
            command=lambda: self.on_click_create_entry(
                db_file, vmp, vid, vname, parent
            ),
        )
        self.ebtn_create_entry.grid(row=0, column=0, padx=10)

        self.ebtn_cancel = ctk.CTkButton(
            self.ebtn_frame, text="Cancel", command=self.destroy
        )
        self.ebtn_cancel.grid(row=0, column=1, padx=10)
        self.ebtn_frame.rowconfigure(0, weight=1)
        self.ebtn_frame.columnconfigure((0, 1), weight=1)
        self.ebtn_frame.pack(expand=True, fill="x")

    def on_click_create_entry(self, db_file, vmp, vid, vname, parent) -> None:
        """
        Handles the creation of a new entry.

        Args:
            self: The instance of the class that this method is bound to.
            db_file (str): The path to the database file where the vault information will be stored.
            vmp (str): The vault master password.
            vname (str): The vault name.
            vid (int): The vault id.
            parent (ctk.CTk): The parent widget for the GUI-based application.

        Returns: None
        """
        # Get the values entered in the name, password, and retype password fields
        sname = self.sname_entry.get()
        pwd = self.spwd_entry.get()
        rpwd = self.srpwd_entry.get()

        # Define a helper function to show an error message
        def show_error(parent: ctk.CTkToplevel, text: str):
            """
            Displays an error message in a new window.

            Args:
                parent (ctk.CTkToplevel): The parent widget for the error message window.
                text (str): The text to display in the error message.

            Returns:
                tuple: A tuple containing a Tkinter Frame and Label widget for the error message.
            """
            frame = ctk.CTkFrame(parent, fg_color="#141212", corner_radius=10)
            frame.pack(expand=True, fill="x", padx=10)
            label = ctk.CTkLabel(
                frame, text=text, text_color="#ff5050", wraplength=350, justify="left"
            )
            label.pack(expand=True, ipadx=10, ipady=10)
            return frame, label

        # Check if the vault name contains prohibited characters
        if any(ch in self.PROHIBITED_NAME_CHARS for ch in sname):
            # Show an error message if the name contains prohibited characters
            if not self.name_error:
                self.win_height += 50
                self.name_error = True
                self.name_err_frame, self.name_err_label = show_error(
                    self,
                    f"Invalid Site Name: site names cannot contain spaces or special characters like {self.PROHIBITED_NAME_CHARS}",
                )
        else:
            # Remove the error message if it was previously shown and the name is valid
            if self.name_error:
                self.win_height -= 50
                self.name_err_frame.destroy()
                self.name_error = False

        # Check if the site name is empty
        if sname == "":
            # Show an error message if the name is empty
            if not self.noname_error:
                self.win_height += 50
                self.noname_error = True
                self.noname_err_frame, self.noname_err_label = show_error(
                    self, f"No Site Name: vault names cannot be left empty!"
                )
        else:
            # Remove the error message if it was previously shown and the name is not empty
            if self.noname_error:
                self.win_height -= 50
                self.noname_err_frame.destroy()
                self.noname_error = False

        # Check if the site name is already in use
        used_names = get_data(db_file, "SELECT site FROM entries;")
        if (sname,) in used_names:
            # Show an error message if the name is already in use
            if not self.usedname_err:
                self.win_height += 50
                self.usedname_error = True
                self.usedname_err_frame, self.usedname_err_label = show_error(
                    self,
                    "Repeated Name Error: Site Name already in use by another entry!",
                )
        else:
            # Remove the error message if it was previously shown and the name is unique
            if self.usedname_error:
                self.win_height -= 50
                self.usedname_err_frame.destroy()
                self.usedname_error = False

        # Check if the password contains prohibited characters
        if any(ch in self.PROHIBITED_PWD_CHARS for ch in pwd):
            # Show an error message if the password contains prohibited characters
            if not self.pwd_error:
                self.win_height += 50
                self.pwd_error = True
                self.pwd_err_frame, self.pwd_err_label = show_error(
                    self,
                    f"Invalid Site Password: site passwords cannot contain spaces or special characters like {self.PROHIBITED_PWD_CHARS}",
                )
        else:
            # Remove the error message if it was previously shown and the password is valid
            if self.pwd_error:
                self.win_height -= 50
                self.pwd_err_frame.destroy()
                self.pwd_error = False

        # Check if the password is empty
        if pwd == "":
            # Show an error message if the password is empty
            if not self.nopwd_error:
                self.win_height += 50
                self.nopwd_error = True
                self.nopwd_err_frame, self.nopwd_err_label = show_error(
                    self,
                    f"No Site Password: site passwords cannot be left empty!",
                )
        else:
            # Remove the error message if it was previously shown and the password is not empty
            if self.nopwd_error:
                self.win_height -= 50
                self.nopwd_err_frame.destroy()
                self.nopwd_error = False

        # check if password and retyped password are not equivalent
        if pwd != rpwd:
            # Show an error message if they are different
            if not self.diffpwds_error:
                self.win_height += 50
                self.diffpwds_error = True
                self.diffpwds_err_frame, self.diffpwds_err_label = show_error(
                    self, "Differing Passwords: Entered passwords do not match!"
                )
        else:
            # Remove the error message if it was previously shown and the password and retyped password are different
            if self.diffpwds_error:
                self.win_height -= 50
                self.diffpwds_err_frame.destroy()
                self.diffpwds_error = False

        self.geometry(f"{self.win_width}x{self.win_height}")

        # If no errors exist, save the info to the database and rebuild the ui of the parent window
        if not any(
            [
                self.name_error,
                self.noname_error,
                self.usedname_error,
                self.pwd_error,
                self.nopwd_error,
                self.diffpwds_error,
            ]
        ):
            add_entry_to_db(db_file, vmp, vid, sname, pwd)
            self.destroy()
            parent.build_ui(db_file, vmp, vname, vid)
