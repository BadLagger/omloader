from mainframe import MainFrameEMMC, MainFrameNAND
from ver import VersionInspector
from sys import argv

if __name__ == "__main__":
    if len(argv) == 2 and argv[1] == '-emmc':
        vi = VersionInspector()
        title = 'OMLoader v.%s git %s' % (vi.get_version(), vi.get_sha())
        print(title)
        mf = MainFrameEMMC(title)
        mf.go()
    else:
        print('There is should be NAND Form')
        mf = MainFrameNAND('OMLoader')
        mf.go()
