#!/usr/bin/python
# vim:ts=4:sts=4:sw=4:et
# -*- coding: utf-8 -*-

import os, sys, zipfile
import xml.etree.ElementTree as ET
from models import *

def get_or_create(session, model, **kwargs):
    object = session.query(model).filter_by(**kwargs).first()
    if object is None:
        object = model(**kwargs)
        session.add(object)
        session.commit()
    return object

def process_file(f):
    ns = "{http://www.gribuser.ru/xml/fictionbook/2.0}"
    print f
    genre=[]
    author=[]
    title=""
    sequence=""
    if f.endswith(".fb2"):
        ext = ".fb2"
        title=os.path.basename(f)[:-4].decode("utf-8")
        print "tmp title",title
        tree = ET.parse(f)
    else:
        ext = ".fb2.zip"
        title=os.path.basename(f)[:-8].decode("utf-8")
        print "tmp title",title
        print "unzipping ...",f
        tmp = zipfile.ZipFile(f, 'r')
        nl = tmp.namelist()
        tmp = tmp.read(nl[0])
        tree = ET.fromstring(tmp)
    for i in tree.find(ns + "description/" + ns + "title-info"):
        if i.tag == ns + "genre":
            # remove multiple spaces
            genre.append(' '.join(i.text.split()))
        if i.tag == ns + "book-title" and i.text is not None:
            title = ' '.join(i.text.split())
        if i.tag == ns + "author":
            a = []
            for an in i:
                if "name" in an.tag and an.text is not None:
                    a.append(' '.join(an.text.split()))
            if len(a):
                author.append(" ".join(a))
        if i.tag == ns + "sequence":
            sequence = ' '.join(i.get("name").split())
    print title
    s = session()
    book_entry = get_or_create(session = s, model = Books, title = title, ext = ext.decode("utf-8"), path = f.decode("utf-8"))
    author_code = 1
    genre_code = 2
    seq_code = 3
    for i in genre:
        genre_entry = get_or_create(session = s, model = Data, data = i)
        meta_link = get_or_create(session = s, model = Meta, book_id = book_entry.id, desc_id = genre_code, data_id = genre_entry.id)
    for i in author:
        author_entry = get_or_create(session = s, model = Data, data = i)
        meta_link = get_or_create(session = s, model = Meta, book_id = book_entry.id, desc_id = author_code, data_id = author_entry.id)
    if len(sequence):
        seq_entry = get_or_create(session = s, model = Data, data = sequence)
        meta_link = get_or_create(session = s, model = Meta, book_id = book_entry.id, desc_id = seq_code, data_id = seq_entry.id)
    s.commit()


def run(path):
    print "Running with",path
    fileList=[]
    for root, subFolders, files in os.walk(path):
        for file in files:
            fileList.append(os.path.join(root,file))
    for f in fileList:
        if f.endswith(".fb2") or f.endswith(".fb2.zip"):
            try:
                process_file(os.path.join(path,f))
            except Exception as e:
                print e

if __name__ == '__main__':
    run(sys.argv[1])

