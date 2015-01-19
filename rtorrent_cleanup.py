#!/usr/bin/python
from __future__ import print_function
import os
import shutil
import bencode
import argparse


args = argparse.Namespace()
args.debug_flag = False
args.pause_on_debug = False
args.dryrun_flag = False

def get_rtorrent_files(path):
    return [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and os.path.splitext(f)[1] == ".rtorrent"]

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

def delete_path(path):
    debug("deleting " + path)
    if os.path.isdir(path):        
        shutil.rmtree(path) 
    elif os.path.isfile(path):
        os.remove(path)


def format_size(size):
    if size >= 1024**3: # GB
        return str(size/(1024**3)) + "GB"
    if size >= 1024**2: # MB
        return str(size/(1024**2)) + "MB"
    if size >= 1024**1: # KB
        return str(size/(1024**1)) + "KB"
    return str(size) + "B"

def debug(msg):
    if args.debug_flag:
        print(msg)
        if args.pause_on_debug:
            print("Continue? ", end = "")
            raw_input()

def main(rtorrent_working_dir, rtorrent_download_dirs, dont_confirm=False):
    debug('debug_flag=' + str(args.debug_flag))
    debug('dryrun_flag=' + str(args.dryrun_flag))
    debug('rtorrent_working_dir=' + rtorrent_working_dir)
    debug('rtorrent_download_dirs=' + str(rtorrent_download_dirs))

    rtorrent_files = get_rtorrent_files(rtorrent_working_dir)

    downloads = list() 
    referenced = list()

    for dir in rtorrent_download_dirs:
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

    if len(not_referenced) > 0:
        sizes = [get_dir_or_file_size(x) for x in not_referenced]
        total_size = sum(sizes)
        print ("deleting all unreferenced files will free up " + format_size(total_size) + " of storage")

        if args.dryrun_flag:
            print("Not referenced files:")
            for path in not_referenced:
                print(path)
        else:
            if not dont_confirm:
                print("unreferenced files will now be deleted (WARNING: DELETED FILES ARE NOT RECOVERABLE) continue? (yes/no) ",end="")
                input = raw_input()
            if dont_confirm or input == "yes":
                for path in not_referenced:
                    delete_path(path)
    else:
        print("there are no files that are not referenced in rtorrent - exiting...")

if __name__ == "__main__":
    # parse arguments
    # TODO option to also look into the folders and delete unreferenced files there
    # TODO option to confirm every deletion
    # TODO quite option to just run without any confirmations
    # TODO option for save mode that just moves all unreferenced files into a target directory
    parser = argparse.ArgumentParser(description='Deletes files from rtorrent download directories that are not referenced in rtorrent', epilog='Github: github.com/ntv1000')
    parser.add_argument('--debug', dest='debug_flag', action='store_true', default=False, help='Debugging information will be displayed')
    parser.add_argument('--pause_on_debug', dest='pause_on_debug', action='store_true', default=False, help='Debugging information will be displayed')
    parser.add_argument('--dry', dest='dryrun_flag', action='store_true', default=False, help='All files that would be deleted will be listed, but not deleted')
    parser.add_argument('rtorrent_working_dir', metavar='WORKING_DIR', help='The working directory of your rtorrent instance')
    parser.add_argument('rtorrent_download_dirs', metavar='DOWNLOAD_DIR', nargs='+', help='The download directories that should be cleaned up')
    #global args
    args = parser.parse_args()
    main(args.rtorrent_working_dir, args.rtorrent_download_dirs)
