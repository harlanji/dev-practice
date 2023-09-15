import os
import json
import hashlib

import time
import shutil

import requests


CACHE_PATH='.data'
CACHE_QUOTA=5*8192

def find_cache_usage ():
    usage = 0
    with os.scandir(CACHE_PATH) as sd:
        for entry in sd:
            if entry.name.endswith('.headers'):
                continue
            usage = usage + entry.stat().st_size
    
    return usage

def find_oldest_file ():
    """
    
    Returns a DirEntry for the oldest file in the cache path.
    
    """
    oldest_file = None
    with os.scandir(CACHE_PATH) as sd:
        for entry in sd:
            if entry.name.endswith('.headers'):
                continue
            ## print(entry.stat())
            osatime = os.path.getatime(entry.path)
            ## print(f'{entry.name} atime = {entry.stat().st_atime}, osatime = {osatime}')
            #if not oldest_file or entry.stat().st_atime < oldest_file.stat().st_atime:
            if not oldest_file or osatime < oldest_file[1]:
                oldest_file = [entry, osatime]
    
    if oldest_file:
        return oldest_file[0]

def purge_cache (request_free_bytes=0):
    """
    
    Deletes the oldest files from the cache until enough bytes have been freed.
    
    Returns false if not enough bytes could be freed.
    
    Deletes nothing if request bytes freed is 0
    
    """
    usage = find_cache_usage()
    
    request_free_bytes = request_free_bytes - (CACHE_QUOTA - usage)

    bytes_freed = 0
    oldest_file = find_oldest_file()
    while oldest_file and bytes_freed < request_free_bytes:
        file_size = oldest_file.stat().st_size
        ## print(f'purge_cache: deleting {oldest_file.name}')
        os.remove(oldest_file.path)
        if os.path.exists(oldest_file.path + '.headers'):
            os.remove(oldest_file.path + '.headers')
        bytes_freed = bytes_freed + file_size
        
        oldest_file = find_oldest_file()
        
    
    if request_free_bytes < bytes_freed:
        return False
    
    
    return True

def filename_for_url (url):
    filename = hashlib.md5(url.encode('utf-8')).hexdigest()
    
    return filename

def write_response (url, cache_filename, resp):
    with open(CACHE_PATH + '/' + cache_filename + '.headers', 'wt', encoding='utf-8') as f:
        headers = dict(resp.headers)
        headers['X-Request-URL'] = url
        headers['X-Cache-Filename'] = cache_filename
        json.dump(headers, f, indent=2)
    
    with open(CACHE_PATH + '/' + cache_filename, 'wb') as f:
        f.write(resp.content)

def request_url (url):
    # add auth like S3
    # idea: credentials like .netrc
    return requests.get(url)

def fetch_file (url):
    cache_filename = filename_for_url(url)
    
    if os.path.exists(CACHE_PATH + '/' + cache_filename):
        # check expiration
        return CACHE_PATH + '/' + cache_filename
    
    resp = request_url(url)
    
    content_length = resp.headers.get('Content-Length', 0)
    
    if content_length == 0:
        content_length = len(resp.content)
        print(f'WARNING: Content-Length = 0, url = {url}, content len = {content_length}')
    
    purge_cache(request_free_bytes=content_length)
    
    write_response(url, cache_filename, resp)
    
    return CACHE_PATH + '/' + cache_filename

def main ():
    if os.path.exists(CACHE_PATH):
        shutil.rmtree(CACHE_PATH)
        
    os.mkdir(CACHE_PATH)
    
    test_purge_cache()
    
    shutil.rmtree(CACHE_PATH)
    os.mkdir(CACHE_PATH)
    
    test_write_quota()
    
    shutil.rmtree(CACHE_PATH)


def test_purge_cache ():
    # create 3 files, each 8KB
    for i in range(0, 5):
        with open(f'{CACHE_PATH}/{i}.txt', 'wb') as f:
            buf = os.urandom(8192)
            f.write(buf)
        time.sleep(1)
    
    with open(f'{CACHE_PATH}/0.txt', 'rb') as f:
        f.read()
    
    oldest_file = find_oldest_file()
    
    print(f'oldest_file: {oldest_file.name}')
    assert oldest_file.name == '1.txt'
    
    purge_cache(request_free_bytes=8192)
    
    oldest_file = find_oldest_file()
    
    print(f'oldest_file: {oldest_file.name}')
    assert oldest_file.name == '2.txt'
    
    purge_cache(request_free_bytes=0)
    
    
    oldest_file = find_oldest_file()
    
    print(f'oldest_file: {oldest_file.name}')
    assert oldest_file.name == '2.txt'
    
    purge_cache(request_free_bytes=2*8192)
    
    
    oldest_file = find_oldest_file()
    
    print(f'oldest_file: {oldest_file.name}')
    assert oldest_file.name == '3.txt'
    
    purge_cache(request_free_bytes=3*8192)
    
    
    oldest_file = find_oldest_file()
    
    print(f'oldest_file: {oldest_file.name}')
    assert oldest_file.name == '4.txt'
    
    purge_cache(request_free_bytes=4*8192)
    
    
    oldest_file = find_oldest_file()
    
    print(f'oldest_file: {oldest_file.name}')
    assert oldest_file.name == '0.txt'
    
    purge_cache(request_free_bytes=5*8192)
    
    
    oldest_file = find_oldest_file()
    
    assert oldest_file == None
    
    # open the first file
    # purge cache
    # assert first 2 files exists
    # purge cache
    # assert only second file exists
    # clear file
    
    return True


def test_write_quota ():
    for i in range(0, 5):
        with open(f'{CACHE_PATH}/{i}.txt', 'wb') as f:
            buf = os.urandom(8192)
            f.write(buf)
            
            time.sleep(1)
    
    purge_cache(request_free_bytes=2*8192)
    
    oldest_file = find_oldest_file()
    
    print(f'oldest_file: {oldest_file.name}')
    assert oldest_file.name == '2.txt'
    
    purge_cache(request_free_bytes=2*8192)
    
    oldest_file = find_oldest_file()
    
    print(f'oldest_file: {oldest_file.name}')
    assert oldest_file.name == '2.txt'
    
    purge_cache(request_free_bytes=2*8192 + 1)
    
    oldest_file = find_oldest_file()
    
    print(f'oldest_file: {oldest_file.name}')
    assert oldest_file.name == '3.txt'

if __name__ == '__main__':
    main()
