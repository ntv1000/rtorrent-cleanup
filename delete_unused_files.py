from __future__ import print_function
import os
import bencode

# option to also look into the folders and delete unreferenced files there

debug_flag = False
pause_on_debug = False
dryrun = True
ask_before_delete = True

def check_if_single_file_torrent(torrent_file_path):
    #return (path in download_dirs) # old version
    # new version
    with open (torrent_file_path, "r") as f:
        content = f.read()
    decoded_content = bencode.decode(content)
    result = not ("files" in decoded_content["info"])
    return result

def get_dir_or_file_size(path):
    result = 0
    if os.path.isdir(path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        result = total_size
    elif os.path.isfile(path):
        result = os.path.getsize(path) 
    return result

def format_size(size):
    if size >= 1024**3: # GB
        return str(size/(1024**3)) + "GB"
    if size >= 1024**2: # MB
        return str(size/(1024**2)) + "MB"
    if size >= 1024**1: # KB
        return str(size/(1024**1)) + "KB"

def debug(msg):
    if debug_flag:
        print(msg)
        if pause_on_debug:
            print("Continue? ", end = "")
            raw_input()

def main():
    rtorrent_working_dir = "/mnt/internal0/rtorrent"
    download_dirs = ["/mnt/internal0/rtorrent/data", "/mnt/external0/rtorrent/data"]

    rtorrent_files = [os.path.join(rtorrent_working_dir, f) for f in os.listdir(rtorrent_working_dir) if os.path.isfile(os.path.join(rtorrent_working_dir, f)) and os.path.splitext(f)[1] == ".rtorrent"]

    downloads = list() 
    referenced = list()

    for dir in download_dirs:
        downloads += [os.path.join(dir, x) for x in os.listdir(dir)]

    print("found " + str(len(downloads)) + " downloaded files")
    print("found " + str(len(rtorrent_files)) + " rtorrent files")

    for rtorrent_file in rtorrent_files:
        #debug("rtorrent_file: " + rtorrent_file)
        content = ""
        with open (rtorrent_file, "r") as f:
            content = f.read()
        if content != "":
            path = bencode.decode(content)["directory"]
            # extrect the path to the tied torrent file (not really tied, rather the torrent file with the same name)
            torrent_file = os.path.splitext(rtorrent_file)[0]
            if os.path.exists(torrent_file):
                if check_if_single_file_torrent(torrent_file):
                    # for "single-file"-torrent the filename has to be taken from the tied torrent_file
                    with open (torrent_file, "r") as f:
                        content = f.read()
                    single_file_name = bencode.decode(content)["info"]["name"]
                    assert os.path.isfile(os.path.join(path, single_file_name))
                    debug("single-file torrent: " + single_file_name)
                    referenced.append(os.path.join(path, single_file_name))
                else: 
                    debug("multi-file torrent: " + path)
                    referenced.append(path)
            else:
                print("ERROR - missing torrent file: '" + torrent_file + "' for rtorrent file '" + rtorrent_file + "'")
        else:
            print("ERROR - empty file")

    print("found " + str(len([x for x in referenced])) + " files that were referenced")
    print("found " + str(len(set(downloads) - set(referenced))) + " files that were not referenced")

    not_referenced = list(set(downloads) - set(referenced))
    #not_referenced = [x for x in downloads if x not in referenced]

    sizes = [get_dir_or_file_size(x) for x in not_referenced]
    total_size = sum(sizes)
    print ("deleting all unreferenced files will free up " + format_size(total_size) + " of storage")

    print("Not referenced files")
    for path in not_referenced:
        debug(path)
        
if __name__ == "__main__":
    main()
