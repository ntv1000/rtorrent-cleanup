import nose
import bencode
import rtorrent_cleanup
from os.path import join, realpath, dirname, exists
from os import remove
import shutil

PLACEHOLDER = "{{pathtotestenv}}"
testsdirectory_path = realpath(__file__)
testenvtemplate_path = join(dirname(testsdirectory_path), "testenv_template")
testenv_path = join(dirname(testsdirectory_path), "testenv")
testworkingdir_path = join(testenv_path, "workingdir")
testwatchdir_path = join(testworkingdir_path, "watchfolder")
testdownloaddir_path = join(testenv_path, "downloaddir")

def setup_env():
    # copy the template
    shutil.copytree(testenvtemplate_path, testenv_path)

    # replace PLACEHOLDERS with the actual paths
    rtorrent_files = rtorrent_cleanup.get_rtorrent_files(testworkingdir_path)
    for rtorrent_file in rtorrent_files:
        with open (rtorrent_file, "r") as f:
            data = bencode.decode(f.read())
        directory = data["directory"]
        loaded_file = data["loaded_file"]
        tied_to_file = data["tied_to_file"]
        data["directory"] = directory.replace(PLACEHOLDER, testenv_path)
        data["loaded_file"] = loaded_file.replace(PLACEHOLDER, testenv_path)
        data["tied_to_file"] = tied_to_file.replace(PLACEHOLDER, testenv_path)
        with open (rtorrent_file, "w") as f:
            f.write(bencode.encode(data))

def teardown_env():
    shutil.rmtree(testenv_path) 
    
@nose.with_setup(setup_env, teardown_env)
def test_delete_none():
    rtorrent_cleanup.main(testworkingdir_path, [testdownloaddir_path], True)
    assert exists(join(testdownloaddir_path, "directory1"))
    assert exists(join(testdownloaddir_path, "file1.txt"))

@nose.with_setup(setup_env, teardown_env)
def test_delete_dirtorrent():
    remove(join(testworkingdir_path, "80AA702AB8D207E076AC3D2B5C09E1B067CCB1BE.torrent.rtorrent"))
    remove(join(testworkingdir_path, "80AA702AB8D207E076AC3D2B5C09E1B067CCB1BE.torrent"))
    remove(join(testwatchdir_path, "directory1.torrent"))
    rtorrent_cleanup.main(testworkingdir_path, [testdownloaddir_path], True)
    assert not exists(join(testdownloaddir_path, "directory1"))
    assert exists(join(testdownloaddir_path, "file1.txt"))

@nose.with_setup(setup_env, teardown_env)
def test_delete_filetorrent():
    remove(join(testworkingdir_path, "327587C17AA1214BF7400A0922E9832A8D1B4C0A.torrent.rtorrent"))
    remove(join(testworkingdir_path, "327587C17AA1214BF7400A0922E9832A8D1B4C0A.torrent"))
    remove(join(testwatchdir_path, "file1.txt.torrent"))
    rtorrent_cleanup.main(testworkingdir_path, [testdownloaddir_path], True)
    assert exists(join(testdownloaddir_path, "directory1"))
    assert not exists(join(testdownloaddir_path, "file1.txt"))

@nose.with_setup(setup_env, teardown_env)
def test_delete_both():
    remove(join(testworkingdir_path, "80AA702AB8D207E076AC3D2B5C09E1B067CCB1BE.torrent.rtorrent"))
    remove(join(testworkingdir_path, "80AA702AB8D207E076AC3D2B5C09E1B067CCB1BE.torrent"))
    remove(join(testwatchdir_path, "directory1.torrent"))
    remove(join(testworkingdir_path, "327587C17AA1214BF7400A0922E9832A8D1B4C0A.torrent.rtorrent"))
    remove(join(testworkingdir_path, "327587C17AA1214BF7400A0922E9832A8D1B4C0A.torrent"))
    remove(join(testwatchdir_path, "file1.txt.torrent"))
    rtorrent_cleanup.main(testworkingdir_path, [testdownloaddir_path], True)
    assert not exists(join(testdownloaddir_path, "directory1"))
    assert not exists(join(testdownloaddir_path, "file1.txt"))
