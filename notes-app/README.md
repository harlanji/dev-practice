# Notes App

This is a notes web app that uses WebDAV to store plaintext files that can be
synced to a remote server.

The reason for storing the notes on the filesystem and exposing via WebDAV is to
make editing with any editor possible.

It's a precursor that lead to [The Notes App](https://harlanji.gumroad.com/l/the-notes-app).

## Requirements

* ExtJS 2.0.2 stored in or linked from the ext-2.0.2 path of each day.
* Nginx with the DAV extension enabled
* An .htpasswd file with at least one user confured in it (via apache tools).
* Optionally lsyncd

I believe the password in the provided .htpasswd files is demo123, pardon if I'm mistaken.

## Usage

The script `setup-deb-bullseye.sh` can be used to install a site to nginx,
or followed for nginx installation on any other platform.

The `sync-notes` script can be used to run lsync, manually or via a cron job.

## Dev Practice

This is an older demo from when I was just establishing the habit of breaking 
practice into a daily format.

It focuses on:

* Making minimal code changes from a prior demo
* Getting an app running in Nginx 
* Nginx DAV storage
* Syncing info to a remote server with LSyncd

The code is messy and intentionally left so because it's derived from an earlier 
work, which I mean to create a minimal diff from and sequentially commit to Git.
Please pardon the apparently amateur style. Releasing as-is to the dev-practice repo.

## Changelog

### 2023-05-21

Updated README for release in harlanji/dev-practice repo.

### Day 3

* Added Lunr code to index in browser and/or nodejs given notes

TODO

* Save notes as paintext and load them as plaintext (this would enable easy import).
* Create a way to change storage location for cross-site
* Either mount the webdav FS for node to index remote notes
* Or create an iterator over notes in the store to download all content.



### 2022-01-16

* Added cross-origin support to nginx config
* Updated code to work cross origin

### 2022-01-15

* Created baseline notes demo
* Created nginx config with webdav
* Created install script
* Created Lsyncd config
