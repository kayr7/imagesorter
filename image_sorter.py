import os
import sys
import errno
import shutil
import exifread


scanned_dirs = set()
requested_locations = []

scanned_dirs.add('./Organized')


def cached_location(lat, lon):
    for (lt, ln, loc) in requested_locations:
        d = great_circle((lt, ln), (lat, lon)).miles
        if great_circle((lt, ln), (lat, lon)).miles < 10:
            print('found in cache!')
            return loc
    return None


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def filecopy(f, t):
    while os.path.exists(t):
        front, ext = os.path.splitext(t)
        t = '{}_{}'.format(front, ext)
    shutil.copy2(f, t)


def scan_dir(curdir):
    for root, subfolders, files in os.walk(curdir):
        if any(root.startswith(x) for x in scanned_dirs):
            print('skipping folder: {}'.format(root))
            continue
        for file in files:
            _, file_extension = os.path.splitext(file)
            if file_extension.lower() in ['.jpg', '.jpeg']:
                filename = '{}/{}'.format(root, file)
                tags = {}
                year = '1998'
                month = '1'
                day = '1'
                unset = True
                with open(filename, 'rb') as fileobj:
                    tags = exifread.process_file(fileobj)
                    if 'EXIF DateTimeOriginal' in tags:
                        dt = tags['EXIF DateTimeOriginal']
                        dt = str(dt).split(' ')
                        year, month, day = dt[0].split(':')
                        unset = False
                    elif 'Image DateTime' in tags:
                        dt = tags['Image DateTime']
                        dt = str(dt).split(' ')
                        year, month, day = dt[0].split(':')
                        unset = False

                if unset or int(year) < 2000:
                    print('problems with: {}'.format(filename))
                path = './Organized/{}/{}/{}/'.format(year, month, day)
                to = '{}{}'.format(path, file)
                make_sure_path_exists(path)
                filecopy('{}/{}'.format(root, file), to)


rootdir = "./"
scan_dir(rootdir)
