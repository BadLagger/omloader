from mainframe import MainFrame
from ver import VersionInspector

if __name__ == "__main__":
    vi = VersionInspector()
    title = 'OMLoader v.%s git %s' % (vi.get_version(), vi.get_sha())
    print(title)
    mf = MainFrame(title)
    mf.go()
