"""
This is the miscellaneous component. 
It contains the functions necessary for the working of the app database, encryption and hashing.
"""

import sqlite3, os, random, string, hashlib
from cryptography.fernet import Fernet
import base64


def get_data(db_file, query):
    """
    Connects to a SQLite database specified by `db_file` and executes the SQL query
    specified by `query`. Returns the data resulting from the query as a list of tuples.

    Args:
        db_file (str): Path to the SQLite database file.
        query (str): SQL query to execute.

    Returns:
        list: A list of tuples representing the data resulting from the query.

    Raises:
        sqlite3.Error: An error occurred while connecting to or querying the database.
    """
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        print(f"Error fetching data from db: {e}")


def encrypt(key: str, msg: str) -> str:
    """Encrypts the given message using the given key.

    Args:
        key (str): The key to use for encryption.
        msg (str): The message to encrypt.

    Returns:
        str: The ciphertext as a string.
    """
    try:
        # Use padding to ensure key is 32 bytes long
        key = key.encode().ljust(32)[:32]
        # Initialize a Fernet object with the key
        fernet_obj = Fernet(base64.urlsafe_b64encode(key))
        # Use the Fernet object to encrypt the message
        ciphertext = fernet_obj.encrypt(msg.encode())
        # Return the ciphertext as a string
        return ciphertext.decode()
    except Exception as e:
        print(f"Encryption Error: {e}")
        return ""


def decrypt(key: str, ciphertext: str) -> str:
    """Decrypts the given ciphertext using the given key.

    Args:
        key (str): The key to use for decryption.
        ciphertext (str): The ciphertext to decrypt.

    Returns:
        str: The decrypted plaintext.
    """
    try:
        # Use padding to ensure key is 32 bytes long
        key = key.encode().ljust(32)[:32]
        # Initialize a Fernet object with the key
        fernet_obj = Fernet(base64.urlsafe_b64encode(key))
        # Use the Fernet object to decrypt the ciphertext
        original_msg = fernet_obj.decrypt(ciphertext.encode())
        # Return the original message as a string
        return original_msg.decode()
    except (InvalidToken, ValueError) as e:
        print(f"Decryption error: {e}")
        return ""


def generate_salt(length: int = 10) -> str:
    """Generates a random alphanumeric string of a given length.

    Args:
     - length (int, optional): The length of the string to generate. Defaults to 3.

    Returns: generated alphanumeric string.
    """
    return "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(length)
    )


def setup_db(db_file: str) -> None:
    """Sets up the application database.

    Args:
     - db_file (str): The filename of the database to use.

    Returns: None
    """

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Create the "vaults" table if it does not already exist
        # vid: vault id; vname: vault name
        # hmp: hashed master password of the vault; salt: salt used in hashing
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS vaults
                        (vid INTEGER PRIMARY KEY AUTOINCREMENT,
                         vname TEXT UNIQUE NOT NULL,
                         hmp TEXT NOT NULL,
                         salt TEXT NOT NULL);"""
        )

        # Create the "passwords" table if it does not already exist
        # pid: password id; vid: vault id
        # site: site name; esp: encrypted site password
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS entries
                        (pid INTEGER PRIMARY KEY AUTOINCREMENT,
                         vid INTEGER NOT NULL,
                         site TEXT NOT NULL,
                         esp TEXT NOT NULL,
                         FOREIGN KEY(vid) REFERENCES vaults(vid));"""
        )

        # check if vaults exist in the database
        # if not, insert an example vault "example_vault" using a random salt with password "pwd"
        no_of_vaults = cursor.execute("SELECT COUNT(*) FROM vaults;").fetchone()[0]
        if no_of_vaults == 0:
            salt = generate_salt()
            mp = "pwd"
            hmp = hashlib.sha256((mp + salt).encode()).hexdigest()
            cursor.execute(
                f"INSERT INTO vaults(vid, vname, hmp, salt) VALUES(1,'example_vault', '{hmp}', '{salt}');"
            )

        # check if passwords exist in the database
        # if not, insert an example password "pwd" for site "site"
        no_of_pwds = cursor.execute("SELECT COUNT(*) FROM entries;").fetchone()[0]
        if no_of_pwds == 0:
            esp = encrypt(key="pwd", msg="pwd")
            cursor.execute(
                f"INSERT INTO entries(pid, vid, site, esp) VALUES(1, 1, 'site', '{esp}')"
            )
        conn.commit()

    except sqlite3.Error as e:
        print(f"Error setting up databases: {e}")

    # Close the cursor and connection
    cursor.close()
    conn.close()


def add_vault_to_db(db_file: str, vault_name: str, vault_pwd: str) -> None:
    """Add a new vault to the database with the given name and password.

    Args:
    - db_file (str): The filename of the database to use.
    - vault_name (str): The name of the new vault to add.
    - vault_pwd (str): The password to use for the new vault.

    Returns: None

    Raises:
    - sqlite3.Error: If an error occurs while adding the vault to the database.
    """
    # Generate a random salt and hash the master password
    salt = generate_salt()
    hmp = hashlib.sha256((vault_pwd + salt).encode()).hexdigest()

    try:
        with sqlite3.connect(db_file) as conn:
            # Use placeholders in the SQL query to avoid SQL injection attacks
            query = "INSERT INTO vaults(vname, hmp, salt) VALUES(?,?,?)"
            values = (vault_name, hmp, salt)
            conn.cursor().execute(query, values)
            conn.commit()
    except sqlite3.Error as error:
        print(f"Error adding vault to database: {error}")


def add_entry_to_db(db_file: str, vmp: str, vid: int, site: str, pwd: str) -> None:
    """Adds an entry to the "entries" table of the database.

    Args:
        db_file (str): Filename of the database to use.
        vmp (str): Vault master password needed for encryption of pwd.
        vid (int): Vault id of used vault.
        pwd (str): Site password to encrypt and store.
        site (str): Site name to store.

    Raises:
        sqlite3.Error: If entry addition fails.
    """
    # encrypt the pwd using vmp
    esp = encrypt(key=vmp, msg=pwd)

    # Use placeholders in the SQL query to avoid SQL injection attacks
    query = "INSERT INTO entries(vid, site, esp) VALUES(?, ?, ?)"
    values = (vid, site, esp)

    try:
        with sqlite3.connect(db_file) as conn:
            conn.execute(query, values)
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding entry to database: {e}")
