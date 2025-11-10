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
        uris = []
        news_divs = []
        for i in range(1,5):
            req=urllib.request.Request(f"https://www.sensacine.com/noticias/?page={i}",         
            headers={'User-Agent': 'Mozilla/5.0'}) 
            f = urllib.request.urlopen(req) 
            s = BeautifulSoup(f, 'lxml')
            container = s.find("div", class_="gd-col-left")
            news_divs_page = container.find_all("div", class_="meta")
            news_divs.extend(news_divs_page)
        
        for nd in news_divs:
            
            not_parsed_category = nd.find("div", class_="meta-category").text.strip()
            category = parse_category_name(not_parsed_category)
            
            url_div = nd.find("a", href=True)
            link = 'https://www.sensacine.com' + url_div['href']
            
            description = url_div.text.strip()
            
            date_div = nd.find("div", class_="meta-date")
            date_without_weekday = delete_weekday_from_date(date_div.text.strip())
            date = parse_date(date_without_weekday)
          
            uris.append((category, link, description, date))
        return uris

    def parse_category_name (category_name):
        parts = category_name.split("-")
        if len (parts) > 1:
            return parts[1].strip()
        else:
            return category_name.strip()
    
    def delete_weekday_from_date(date_text):
        parts = date_text.split(",")
        if len(parts) > 1:
            return parts[1].strip()
        else:
            return date_text.strip()
    
    def parse_date(date):
        months = {'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04', 'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08', 'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'}
        slices = date.lower().split()
        slices = [slices[-5], slices[-3], slices[-1]]
        modified_date = f"{slices[0]} {months[slices[1]]} {slices[2]}"
        return datetime.strptime(modified_date, '%d %m %Y')


    def obtain_news_from_uris(news_uris):
        news = list()
        for category, link, description, date in news_uris:
            req=urllib.request.Request(link,         
            headers={'User-Agent': 'Mozilla/5.0'}) 
            f = urllib.request.urlopen(req) 
            s = BeautifulSoup(f, 'lxml')
            title = s.find('div', class_='titlebar-title titlebar-title-lg').text.strip() if s.find('div', class_='titlebar-title titlebar-title-lg') else 'Unknown'
            new = (category, title, link, description, date)
            # print(new)
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
                            title=str(j[1]), 
                            link=str(j[2]), 
                            description=str(j[3]), 
                            date=j[4])
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
        lb.insert(END,"    Category: " + row['category'])
        lb.insert(END,"    Title: "+ row['title'])
        lb.insert(END,"    Link: "+ row['link'])
        lb.insert(END,"    Date: "+ row['date'].strftime('%d/%m/%Y'))
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
    def show_list():    
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
    
    b =Button(v, text="Search", command=show_list)
    b.pack(side=LEFT)

def title_or_description():
    def show_list():
        ix=open_dir("Index")   
        with ix.searcher() as searcher:
            title_words = str(en.get()).strip()
            description_words = str(en1.get()).strip()
            
            query_parts = []
            
            full_query_string = f'title:({title_words}) AND description:({description_words})'

            try:
                query = QueryParser(None, ix.schema).parse(full_query_string)
                results = searcher.search(query, limit=None)
                
                if (title_words and description_words):
                    print_list(results)
                else:
                    messagebox.showinfo("Error", "Please enter words in both fields.")

            except Exception as e:
                messagebox.showerror("ERROR", f"Error: {e}")
    
    v = Toplevel()
    v.title("Search by title or description")
    l = Label(v, text="Write phrase from title:")
    l.pack(side=LEFT)   
    en = Entry(v)
    en.pack(side=LEFT)
    
    l1 = Label(v, text="Write words from description:")
    l1.pack(side=LEFT)
    en1 = Entry(v, width=75)
    en1.pack(side=LEFT)
    
    b =Button(v, text="Buscar", command=show_list)
    b.pack(side=LEFT)

def date():
    def parse_date(date):
        months = {
            'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04', 'mayo': '05', 'junio': '06',
            'julio': '07', 'agosto': '08', 'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
        }
        slices = date.lower().split()
        slices = [s for s in slices if s != "de"]
        day, month, year = slices[0], slices[1], slices[2]
        formatted_date = f"{year}{months[month]}{int(day):02d}"
        return formatted_date
    
    def list_films_between_dates(event):
        ix=open_dir('Index')
        with ix.searcher() as searcher:
            myquery = QueryParser("title", ix.schema).parse('date:['+ parse_date(str(entry_date_1.get())) +' TO ' + parse_date(str(entry_date_2.get())) + ']')
            results = searcher.search(myquery, limit=None)
            print_list(results)

    v = Toplevel()
    label = Label(v, text="Search for films between dates (DD de (Nombre mes) de YYYY): ")
    label.pack(side=LEFT)
    
    entry_date_1 = Entry(v)
    entry_date_1.bind("<Return>", list_films_between_dates)
    entry_date_1.pack(side=LEFT)

    entry_date_2 = Entry(v)
    entry_date_2.bind("<Return>", list_films_between_dates)
    entry_date_2.pack(side=LEFT)

def delete_by_description():
    def modify(event):
        ix=open_dir("Index") 
        with ix.searcher() as searcher:
            query = QueryParser("description", ix.schema).parse(str(en.get()))
            results = searcher.search(query, limit=None)
            if len(results) > 0: 
                v = Toplevel()
                v.title("News to delete")
                v.geometry('800x150')
                sc = Scrollbar(v)
                sc.pack(side=RIGHT, fill=Y)
                lb = Listbox(v, yscrollcommand=sc.set)
                lb.pack(side=BOTTOM, fill = BOTH)
                sc.config(command = lb.yview)
                for r in results:
                    lb.insert(END,r['title'])
                    lb.insert(END,'')
                respuesta = messagebox.askyesno(title="Confirm",message="Are you sure that you want to delete this new?")
                if respuesta:
                    writer = ix.writer()
                    writer.delete_by_query(query)
                    writer.commit()
            else:
                messagebox.showinfo("WARNING", "There is no new with a description with those words")

    v = Toplevel()
    v.title("Delete news by description")
    l = Label(v, text="Write description words:")
    l.pack(side=LEFT)
    en = Entry(v, width=75)
    en.bind("<Return>", modify)
    en.pack(side=LEFT)

def title_and_date():
    def parse_date(date):
        new_date = '' + date[4:] + date[2:4] + date[:2]
        return new_date

    def list_films_by_date_and_title():
        ix=open_dir('Index')
        with ix.searcher() as searcher:
            s = re.compile('\d{8}').match(str(entry_date.get()))
            if s:
                myquery = QueryParser("title", ix.schema).parse('date:['+ parse_date(str(entry_date.get())) +' TO ' + parse_date(str(entry_date.get())) + '] '+ str(entry_title.get()))
                results = searcher.search(myquery, limit=5)
                print_list(results)
            else:
                messagebox.showerror("ERROR", "formato de fecha incorrecto DDMMYYY")

    v = Toplevel()
    label = Label(v, text="Search for films with that title and publish date (DDMMYYYY): ")
    label.pack(side=LEFT)
    
    entry_title = Entry(v)
    entry_title.pack(side=LEFT)

    entry_date = Entry(v)
    entry_date.pack(side=LEFT)

    b =Button(v, text="Buscar", command=list_films_by_date_and_title)
    b.pack(side=LEFT)


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
