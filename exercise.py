from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, ID
from whoosh.qparser import QueryParser
from datetime import datetime
from whoosh import qparser, index, query
import locale

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def read_data():
    def obtain_recipes_uris():
        pass

    def obtain_recipes_from_uris(recipes_uris):
        pass

    recipes_uris = obtain_recipes_uris()
    data = obtain_recipes_from_uris(recipes_uris)
    return data

def load():
    data = read_data()
    pass

def list_all():
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            results = searcher.search(query.Every(),limit=None)
            print_list(results)

def print_list():
    pass

def description():
    pass

def category_and_title():
    pass

def title_or_description():
    pass

def date():
    pass

def delete_by_description():
    pass

def title_and_date():
    pass


def main_window():
    root = Tk()
    menu = Menu(root)

    # DATA
    datamenu = Menu(menu, tearoff=0)
    datamenu.add_command(label="Load", command=load)
    datamenu.add_command(label="Exit", command=root.quit)
    datamenu.add_command(label="List", command=list_all)
    menu.add_cascade(label="Data", menu=datamenu)

    # SEARCH
    searchmenu = Menu(menu, tearoff=0)
    searchmenu.add_command(label="Description", command=description)
    searchmenu.add_command(label="Category and title", command=category_and_title)
    searchmenu.add_command(label="Tittle or description", command=title_or_description)
    searchmenu.add_command(label="Date", command=date)
    searchmenu.add_command(label="Delete by description", command=delete_by_description)
    searchmenu.add_command(label="Tittle and date", command=title_and_date)
    menu.add_cascade(label="Search", menu=searchmenu)

    root.config(menu=menu, background='lightblue', width=500, height=400)

    root.mainloop()

if __name__ == '__main__':
    main_window()