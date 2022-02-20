import git

VERSION=0.1

if __name__ == "__main__":
    try:
        sha = git.Repo(search_parent_directory=True).head.object.hexsha
    except:
        sha = None
        print('No git folder')
    print('OMLoader v.%s: %s' % (VERSION, sha))
