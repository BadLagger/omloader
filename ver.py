import pathlib
import git
import sys
import inspect

class VersionInspector:
    __version =  0.1
    __sha = "579e50b"

    def get_version(self):
        return self.__version

    def get_sha(self):
        return self.__sha

if __name__ == "__main__":

    def change_version(line):
        pure_line = line.split('=')
        pure_vers = pure_line[1].strip()
        if pure_vers == 'None':
            pure_line[1] = ' 0.1'
        else:
            pure_num = pure_line[1].split('.')
            if int(pure_num[1]) < 9:
                pure_num[1] = str(int(pure_num[1]) + 1)
            else:
                pure_num[0] = str(int(pure_num[0]) + 1)
                pure_num[1] = '0'
            pure_line[1] = '.'.join(pure_num).strip()
        pure_line[1] = ' %s\n' % pure_line[1]
        return '='.join(pure_line)

    def change_sha(line):
        pure_line = line.split('=')
        try:
            current_dir = pathlib.Path().resolve()
            repo = git.Repo(current_dir)
            pure_line[1] = ' "%s"\n' % repo.head.object.hexsha[0:7]
            line = '='.join(pure_line)
        except:
            print('No git repo found')
        return line

    def set_None(line):
        pure_line = line.split('=')
        pure_line[1] = " None\n"
        return '='.join(pure_line)

    def all():
        print(inspect.stack()[0][3])

        with open('ver.py', 'r') as rf:
            lines = rf.readlines()

        set_vers, set_sha = False, False
        with open('ver.py', 'w') as wf:
            for line in lines:
                if set_vers == False:
                    search = line.find('__version')
                    if search != -1:
                        set_vers = True
                        line = change_version(line)
                elif set_sha == False:
                    search = line.find('__sha')
                    if search != -1:
                        set_sha = True
                        line = change_sha(line)
                wf.write(line)

    def version():
        print(inspect.stack()[0][3])

        with open('ver.py', 'r') as rf:
            lines = rf.readlines()

        set_vers = False
        with open('ver.py', 'w') as wf:
            for line in lines:
                if set_vers == False:
                    search = line.find('__version')
                    if search != -1:
                        set_vers = True
                        line = change_version(line)
                wf.write(line)

    def sha():
        print(inspect.stack()[0][3])

        with open('ver.py', 'r') as rf:
            lines = rf.readlines()

        set_sha = False
        with open('ver.py', 'w') as wf:
            for line in lines:
                if set_sha == False:
                    search = line.find('__sha')
                    if search != -1:
                        set_sha = True
                        line = change_sha(line)
                wf.write(line)

    def clean():
        print(inspect.stack()[0][3])

        with open('ver.py', 'r') as rf:
            lines = rf.readlines()

        set_vers, set_sha = False, False
        with open('ver.py', 'w') as wf:
            for line in lines:
                if set_vers == False:
                    search = line.find('__version')
                    if search != -1:
                        set_vers = True
                        line = set_None(line)
                elif set_sha == False:
                    search = line.find('__sha')
                    if search != -1:
                        set_sha = True
                        line = set_None(line)
                wf.write(line)

    def get():
        print(inspect.stack()[0][3])
        ver = VersionInspector()
        print(ver.get_version())
        print(ver.get_sha())
        pass

    fooTab = ('all', 'version', 'sha', 'clean', 'get')

    if len(sys.argv) != 2:
        print('Should set 1 argument: %s' % fooTab)
    else:
        print('Good argument number')
        if sys.argv[1] in fooTab:
            locals()[sys.argv[1]]()
        else:
            print('Unknown: %s. Should be in %s' % (sys.argv[1], fooTab))
