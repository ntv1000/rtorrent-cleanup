# rtorrent-cleanup

This script is used to automatically delete files that are not visible in rtorrent anymore, but still present in the download directory.

# Usage

`./delete_unused_files.py [--dry] WORKING_DIR DOWNLOAD_DIR [DOWNLOAD_DIR ...]`

**Arguments:**

  `WORKING_DIR`       The working directory (called 'session' in rtorrent.rc) of your rtorrent instance.
  
  `DOWNLOAD_DIR`      The download directories that should be cleaned up.

**Optional arguments:**

  `--dry`             Lists all files that would be deleted

# Example

`./delete_unused_files.py /path/to/working/dir/ /path/to/download/dir/`

This will delete all files from `/path/to/working/dir` that are not visible in the rtorrent instance which uses `/path/to/download/dir/` as session directory.
