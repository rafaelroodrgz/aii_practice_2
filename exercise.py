from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, ID, KEYWORD
from whoosh.qparser import QueryParser, MultifieldParser
from datetime import datetime
from whoosh import qparser, index, query
import locale

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def read_data():
    def obtain_news_uris():
        pass

    def obtain_news_from_uris(news_uris):
        news = list()
        for n_uri, category, publish_date  in news_uris:
            raw_data = urllib.request.urlopen(n_uri).read().decode('UTF-8')
            soup = BeautifulSoup(raw_data, 'lxml')
            title = soup.find('div', class_='titlebar-title titlebar-title-lg').text.strip() if soup.find('div', class_='titlebar-title titlebar-title-lg') else 'Unknown'
            description = soup.find('p', class_='article-lead').text.strip() if soup.find('p', class_='article-lead') else 'Unknown'
            new = (category, title, n_uri, description, publish_date)
            print(new)
            news.append(new)
        return news

    news_uris = obtain_news_uris()
    data = obtain_news_from_uris(news_uris)
    return data

def load():
    schem = Schema(category=ID(stored=True), 
                   title=TEXT(stored=True), 
                   link=ID(stored=True), 
                   description=TEXT,
                   date=DATETIME(stored=True))
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    ix = create_in("Index", schema=schem)
    writer = ix.writer()
    i=0
    list=read_data()
    for j in list:
        writer.add_document(category=str(j[0]), 
                            title=int(j[1]), 
                            link=str(j[2]), 
                            description=j[3], 
                            date=str(j[4]))    
        i+=1
    writer.commit()
    messagebox.showinfo("End of index", "Indexed "+str(i)+ " news")   

def list_all():
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            results = searcher.search(query.Every(),limit=None)
            print_list(results)

def print_list(cursor):
    v = Toplevel()
    v.title("FILM NEWS")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row['title'])
        lb.insert(END,"    Description: "+ row['description'])
        lb.insert(END,"    Link: "+ row['link'])
        lb.insert(END,"    Date: "+ row['date'])
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)

def description():
    def show_list(event):
        ix=open_dir("Index")   
        with ix.searcher() as searcher:
            query = MultifieldParser(["description"], ix.schema).parse('"'+ str(en.get()) + '"')
            results = searcher.search(query,limit=10)
            print_list(results)
    
    v = Toplevel()
    v.title("Search by description")
        
    l1 = Label(v, text="Enter a phrase")
    l1.pack(side=LEFT)
    en = Entry(v, width=75)
    en.bind("<Return>", show_list)
    en.pack(side=LEFT)

def category_and_title():
    def mostrar_lista():    
        with ix.searcher() as searcher:
            entrada = '"'+str(en.get())+'"'
            query = QueryParser("title", ix.schema).parse('category:'+ entrada +' '+str(en1.get()))
            results = searcher.search(query,limit=10)
            print_list(results)
    
    v = Toplevel()
    v.title("Search by Category and Title")
    l = Label(v, text="Choose a category:")
    l.pack(side=LEFT)
    
    ix=open_dir("Index")      
    with ix.searcher() as searcher:
        lista_caracteristicas = [i.decode('utf-8') for i in searcher.lexicon('category')]
    
    en = Spinbox(v, values=lista_caracteristicas, state="readonly")
    en.pack(side=LEFT)
    
    l1 = Label(v, text="Write title words:")
    l1.pack(side=LEFT)
    en1 = Entry(v, width=75)
    en1.pack(side=LEFT)
    
    b =Button(v, text="Search", command=mostrar_lista)
    b.pack(side=LEFT)

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