import os
from pathlib import Path
from tkinter import Tk, Button, Label, filedialog, Text, END
from Crypto.Cipher import AES
from PIL import Image

# -------------------------------------------------
# Xiaomi/Redmi LSA Decryption Parameters
# -------------------------------------------------

KEY = bytes.fromhex('3082046c30820354a003020102020900')

IV = bytes([
    17, 19, 33, 35,
    49, 51, 65, 67,
    81, 83, 97, 102,
    103, 104, 113, 114
])

# -------------------------------------------------
# Detect Image Extension
# -------------------------------------------------

def detect_extension(data):
    if data.startswith(b'\xff\xd8\xff'):
        return '.jpg'

    if data.startswith(b'\x89PNG'):
        return '.png'

    if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
        return '.gif'

    if data.startswith(b'BM'):
        return '.bmp'

    return '.bin'

# -------------------------------------------------
# Decrypt File
# -------------------------------------------------

def decrypt_file(input_path, output_folder):
    try:
        encrypted = Path(input_path).read_bytes()

        cipher = AES.new(
            KEY,
            AES.MODE_CTR,
            initial_value=int.from_bytes(IV, 'big'),
            nonce=b''
        )

        decrypted = cipher.decrypt(encrypted)

        ext = detect_extension(decrypted)

        output_name = Path(input_path).stem + ext
        output_path = Path(output_folder) / output_name

        output_path.write_bytes(decrypted)

        return True, output_path

    except Exception as e:
        return False, str(e)

# -------------------------------------------------
# GUI Application
# -------------------------------------------------

class LSARecoveryApp:

    def __init__(self, root):
        self.root = root
        self.root.title('LSA Image Recovery Tool')
        self.root.geometry('700x500')

        title = Label(
            root,
            text='Xiaomi/Redmi LSA Recovery Tool',
            font=('Arial', 16, 'bold')
        )
        title.pack(pady=10)

        self.select_btn = Button(
            root,
            text='Select Folder Containing .lsa Files',
            command=self.select_folder,
            height=2,
            width=40
        )
        self.select_btn.pack(pady=10)

        self.log = Text(root, height=20, width=85)
        self.log.pack(padx=10, pady=10)

    def write_log(self, text):
        self.log.insert(END, text + '\n')
        self.log.see(END)
        self.root.update()

    def select_folder(self):
        folder = filedialog.askdirectory()

        if not folder:
            return

        folder = Path(folder)

        output_folder = folder / 'Recovered_Images'
        output_folder.mkdir(exist_ok=True)

        lsa_files = list(folder.glob('*.lsa'))

        if not lsa_files:
            self.write_log('No .lsa files found.')
            return

        self.write_log(f'Found {len(lsa_files)} encrypted files.')
        self.write_log('Starting recovery...\n')

        success_count = 0

        for file in lsa_files:
            success, result = decrypt_file(file, output_folder)

            if success:
                success_count += 1
                self.write_log(f'[SUCCESS] {file.name}')
            else:
                self.write_log(f'[FAILED] {file.name} -> {result}')

        self.write_log('\n--------------------------------')
        self.write_log(f'Recovered {success_count}/{len(lsa_files)} files')
        self.write_log(f'Saved to: {output_folder}')

        try:
            os.startfile(output_folder)
        except:
            pass

# -------------------------------------------------
# Run App
# -------------------------------------------------

if __name__ == '__main__':
    root = Tk()
    app = LSARecoveryApp(root)
    root.mainloop()
