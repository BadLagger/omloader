import pathlib
import git
from mainframe import MainFrame

VERSION=0.1
if __name__ == "__main__":
    current_dir = pathlib.Path().resolve()
    print(current_dir)
    try:
        repo = git.Repo(current_dir)
        sha = repo.head.object.hexsha[0:7]
    except:
        sha = None
        print('No git folder')
    title = 'OMLoader v.%s git %s' % (VERSION, sha)
    print(title)
    mf = MainFrame(title)
    mf.go()
