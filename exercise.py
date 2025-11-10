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
import locale

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def read_data():
    def obtain_news_uris():
        uris = []
        req=urllib.request.Request("https://www.sensacine.com/noticias/",         
        headers={'User-Agent': 'Mozilla/5.0'}) 
        f = urllib.request.urlopen(req) 
        s = BeautifulSoup(f, 'lxml')
        container = s.find("div", class_="gd-col-left")
        
        news_divs = container.find_all("div", class_="meta")
        for nd in news_divs:
            category = nd.find("div", class_="meta-category").text.strip()
            parsed_category = parse_category_name(category)
            
            url_div = nd.find("a", href=True)
            full_url = 'https://www.sensacine.com' + url_div['href']
            
            description = url_div.text.strip()
            
            date_div = nd.find("div", class_="meta-date")
            date_without_weekday = delete_weekday_from_date(date_div.text.strip())
            parsed_date = parse_date(date_without_weekday)
          
            uris.append((parsed_category, full_url, description, parsed_date))
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
        return datetime.strptime(modified_date, '%d %m %Y').strftime('%d%m%Y')


    def obtain_news_from_uris(news_uris):
        pass

    news_uris = obtain_news_uris()
    data = obtain_news_from_uris(news_uris)
    return data

def load():
    data = read_data()
    pass

def title_or_introduction():
    pass

def date():
    pass

def features_and_title():
    pass

def main_window():
    root = Tk()
    menu = Menu(root)

    # DATA
    datamenu = Menu(menu, tearoff=0)
    datamenu.add_command(label="Load", command=load)
    datamenu.add_command(label="Exit", command=root.quit)
    menu.add_cascade(label="Data", menu=datamenu)

    # SEARCH
    searchmenu = Menu(menu, tearoff=0)
    searchmenu.add_command(label="Author", command=title_or_introduction)
    searchmenu.add_command(label="Delete by summary", command=date)
    searchmenu.add_command(label="Date and title", command=features_and_title)    
    menu.add_cascade(label="Search", menu=searchmenu)

    root.config(menu=menu, background='lightblue', width=500, height=400)

    root.mainloop()

if __name__ == '__main__':
    # main_window()
    read_data()
