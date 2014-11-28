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
    if f.endswith(".fb2"):
        ext = ".fb2"
        tree = ET.parse(f)
    else:
        ext = ".fb2.zip"
        print "unzipping ...",f
        tmp = zipfile.ZipFile(f, 'r')
        nl = tmp.namelist()
        tmp = tmp.read(nl[0])
        tree = ET.fromstring(tmp)
    for i in tree.find(ns + "description/" + ns + "title-info"):
        if i.tag == ns + "genre":
            genre.append(i.text)
        if i.tag == ns + "book-title":
            title = i.text
        if i.tag == ns + "author":
            a = []
            for an in i:
                if "name" in an.tag and an.text is not None:
                    a.append(an.text)
            if len(a):
                author.append(" ".join(a))
    print title," ", ";".join(genre), ";".join(author)
    s = session()
    book_entry = get_or_create(session = s, model = Books, title = title, ext = ext.decode("utf-8"), path = f.decode("utf-8"))
    author_code = 1
    genre_code = 2
    for i in genre:
        genre_entry = get_or_create(session = s, model = Data, data = i)
        meta_link = get_or_create(session = s, model = Meta, book_id = book_entry.id, desc_id = genre_code, data_id = genre_entry.id)
    for i in author:
        author_entry = get_or_create(session = s, model = Data, data = i)
        meta_link = get_or_create(session = s, model = Meta, book_id = book_entry.id, desc_id = author_code, data_id = author_entry.id)
    s.commit()


def run(path):
    print "Running with",path
    for f in os.listdir(path):
        if f.endswith(".fb2") or f.endswith(".fb2.zip"):
            process_file(os.path.join(path,f))

if __name__ == '__main__':
    run(sys.argv[1])

