#!/usr/bin/python
# vim:ts=4:sts=4:sw=4:et
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
import sys
import stat
import errno
from fuse import Fuse
import fuse
fuse.fuse_python_api = (0, 2)

from models import *

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class EbookFS(Fuse):
    def __init__(self, **kwargs):
        super(EbookFS, self).__init__(**kwargs)
        s = session()
        self.tree = dict()
        p_dir = stat.S_IFDIR | 0755
        p_file = stat.S_IFREG | 0644
        for i in s.query(Desc).all():
            name = "/" + i.name.encode("utf-8")
            self.tree[name] = [p_dir]
            for meta in s.query(Meta).filter_by(desc_id = i.id):
                data = s.query(Data).filter_by(id = meta.data_id).first()
                book = s.query(Books).filter_by(id = meta.book_id).first()
                d_name = data.data.encode("utf-8")
                f_name = (book.title + book.ext).encode("utf-8")
                self.tree[name + "/" + d_name] = [p_dir]
                self.tree[name + "/" + d_name + "/" + f_name] = [p_file, book.path.encode("utf-8")]
        for i in self.tree.keys():
            print "added",i

    # Helpers
    # =======

    def good_path(self, path):
        return path in self.tree.keys()

    def resolve_path(self, path):
        xa = self.tree[path]
        if len(xa) == 2:
            return xa[1]

    # Filesystem methods
    # ==================

    def getattr(self, path):
        st= MyStat();
        if path == "/":
            print "get attr",path
            st.st_mode = stat.S_IFDIR | 0755
            return st
        if self.good_path(path):
            print "get attr",path
            xa = self.tree[path]
            if len(xa) == 1:
                st.st_mode = xa[0]
            else:
                st = os.lstat(xa[1])
            return st
        else:
            print "get NX attr",path
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        dirents = ['.', '..']
        if path[-1] != "/":
            path += "/"
        print "start with [" + path + "]"
        elem_n = path.count("/")
        for i in self.tree.keys():
            if i != path and i.startswith(path) and i.count("/") == elem_n:
                i = i[len(path):]
                print "add entry",i
                dirents.append(i)
        for r in dirents:
            yield fuse.Direntry(r)

    def open(self, path, flags):
        print "open",path
        if self.good_path(path) and len(self.resolve_path(path)):
            if flags & os.O_RDONLY != os.O_RDONLY:
                return -errno.EACCES
            else:
                return 0
        return -errno.ENOENT

    def read(self, path, length, offset):
        if self.good_path(path):
            f = os.open(self.resolve_path(path), os.O_RDONLY)
            os.lseek(f, offset, os.SEEK_SET)
            return os.read(f, length)
        return -errno.ENOENT


if __name__ == '__main__':
    server = EbookFS(version="%prog " + fuse.__version__,
                     dash_s_do='setsingle')
    server.parse(errex=1)
    server.main()

