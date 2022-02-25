import subprocess

class Subroute:
    def __init__(self, cmd):
        self.__cmd = None
        try:
            self.__cmd = subprocess.Popen(cmd, shell=True, universal_newlines=False, stdout=subprocess.PIPE)
        except ValueError as err:
            print("Value error:", err)
        except OSError as err:
            print("Os error:", err)
        except subprocess.SubprocessError as err:
            print("Other error:", err)

    def print_log(self):
        if self.__cmd != None:
            print(type(self.__cmd.stdout))
            print(dir(self.__cmd.stdout))
            while self.__cmd.poll() == None:
                b = self.__cmd.stdout.read()
                print(b, end='')
        else:
            print("Route doesn't exist...")

    def is_online(self):
        if self.__cmd != None:
            if self.__cmd.poll() == None:
                return True
        return False

    def stop(self):
        if self.__cmd != None:
            self.__cmd.kill()

if __name__ == "__main__":
    print('Suboute')
    k = Subroute("ls -al")
    k.print_log()
