# Command Line Interface 
import typer 
from rich.console import Console
from rich.table import Table
from typing import Optional

from dotenv import load_dotenv
import os

# DataBase PostgreSQL
import psycopg2
from configparser import ConfigParser

# isbn tool
from isbnlib import meta, is_isbn13, cover, desc
from isbnlib.registry import bibformatters


import pandas as pd



console = Console()
app = typer.Typer()


# Load .env file
load_dotenv()

# Get the connection string from the environment variable
connection_string = os.getenv('DATABASE_URL')

# Connect to the Postgres database
conn = psycopg2.connect(connection_string)

# Create a cursor object
cur = conn.cursor()

# Create DataFrame

@app.command()
def add_title_isbn():
    pass

@app.command('ok_data')
def ok_data(isbn: str = '9781844145720'):
    '''returns: ISBN, title, Authors, Publisher, Year, Language'''
    
    print("Looking up ISBN", isbn)
    try:
        metabook = meta(isbn)
        newmeta = {}
        print('METABOOK IS  ')
        for x,y in metabook.items():
            if x == 'Authors':
                x = 'Author'
                y = (', ').join(y)
            newmeta[x] = y
            typer.secho(f'{x}: {y}', fg=typer.colors.GREEN)
        newmeta['desc'] = desc(isbn)
        
        print()
        return newmeta
    except (Exception, KeyError):
        print(Exception, KeyError)
        return False

def is_exists(isbn, title):
    '''Return True if book already exists in the DB'''
    query = f"SELECT id FROM store_book \
        WHERE isbn = '{isbn}' AND title = '{title}'"
    cur.execute(query)
    id = cur.fetchone()
    if id:
        return id[0]
    return False

# Collect data

@app.command('bookdata')
def get_bookdata(isbn: str = '9781844145720'):
    isbn = input('Enter ISBN  ')
    ''' This returns title, author, puplisher, year, language of the book usind ISBN13'''

    print("Looking up data using", isbn)

    try:
        metabook = meta(isbn)
        bookdata = {}
        for x,y in metabook.items():
            if x == "Authors":
                x = 'Author'
                y = (',').join(y)
            bookdata[x] = y
            typer.secho(f'{x}: {y}', fg=typer.colors.GREEN)
        bookdata['desc'] = desc(isbn)
        print(bookdata['desc'])
        print(cover(isbn))
        return bookdata
    except (Exception, KeyError):
        print(Exception, KeyError)
        return False

# ADD to Database

def is_exists(isbn, title):
    ''' Returns 'True' if book already exists in the DB '''
    query = f"SELECT id FROM storage_title \
        WHERE isbn = '{isbn}' AND title = '{title}'"
    
    cur.execute(query)
    id = cur.fetchone()
    if id:
        print('ID is: ', id)
        return id[0]
    return False
    
@app.command()
def add_book_isbn():
    while True:
        print()
        isbn_ = input("ENTER THE ISBN ---> ")
        if not is_isbn13(isbn_):
            print('ISBN is nor correct')
            continue
        bookdata = get_bookdata(isbn_)

        if bookdata:
            isbn = bookdata["ISBN-13"]
            title = bookdata['Title']
            author = bookdata['Author']
            publisher = bookdata['Publisher']
            year = bookdata['Year']
            lang = bookdata['Language']
            description = bookdata['desc']

            description = description.replace("'", "''")
            title = title.replace("'","''")

            query = f'''INSERT INTO storage_title (isbn, title, author, publisher, year, language, description, user_id, created, in_stock, is_active)
                VALUES ('{isbn}', '{title}', '{author}', '{publisher}', '{year}', '{lang}', '{description}', '1', CURRENT_TIMESTAMP, TRUE, TRUE)'''
            
            # if not is_exists(isbn, title):
            #     cur.execute(query)
            #     print('The Title is successfully added')
            #     id = is_exists(isbn, title)
            
            cur.execute(query)
            conn.commit()
            print('The Title is successfully added')
        

        else:
            message = '''ISBN is correct but data not found.
                Please add the titel by hand'''
            typer.secho(message, fg=typer.colors.RED)
            act = input("Add title by hand? [y/n]  ")
            if act.lower() == "y":
                add_title_hand()
        break
    conn.close()


@app.command("add_title_hand")
def add_title_hand():
    ''' Add book data to DB
    '''
    while True:
        isbn = input("Enter the ISBN: ")
        title = input("Enter the Title: ")
        author = input("Enter the Author: ")
        publisher = input("Enter the publisher: ")
        year = input("Enter the Year: ")
        lang = input("Enter the Language: ")
        description = input("Add the description: ")

        query = f'''INSERT INTO storage_title (isbn, title, author, publisher, year, lang, description) VALUES ('{isbn}', '{title}', '{author}', '{publisher}', '{year}', '{lang}', '{description}')'''
        
        if not is_exists(isbn, title):
            cur.execute(query)
            id = is_exists(isbn, title)
            print(f"Success added ID is {id}")
        else:
            id = is_exists(isbn, title)
            print(f"Book is already added. ID is {id}")
        act = input("Add another book? [y/n]  ")
        if act.lower() != 'y':
            break
        else: 
            continue
        

@app.command('add_title_excel')
def add_title_excel(row):
    "Add the title and boot-to-place one by one from Excel's rows"
    isbn, title, author, category_name, level_name, year, location, quantity, description  = row
    description = description.replace("'", "''")
    title = title.replace("'", "''")
    query = f"""INSERT INTO storage_title (isbn, title, author, category_name, level_name, year, description, created)\
        VALUES ('{isbn}', '{title}', '{author}', '{category_name}', '{level_name}', '{year}', '{description}', CURRENT_TIMESTAMP)"""
    

    if not is_exists(isbn, title):
        cur.execute(query)
        print('THE TITLE IS SUCCESSFULLY ADDED')
        id = is_exists(isbn, title)
        # act = input('ADD TO PLACE? [Y / N] --> ')
        # if act.lower() == 'y':
        # add_to_place(id, location, quantity)
            
    else:
        print('BOOK IS ALREADY EXISTS')
        id = is_exists(isbn, title)
        # act = input('ADD TO PLACE? [Y/N] --> ')
        # if act.lower() == 'y':
        print('ID IS ', id)
        # add_to_place(id, location, quantity)



def add_to_place(book_id, place: Optional[int] = None, amount: Optional[int] = None):
    '''Add book to place'''
    if place == None:
        # place = input("ENTER THE PLACE ID (cold_room it's 3) --> ")
        
        place = 5 # <<< -----  CHANGE THE PLACE!!!!! -------------------------------------------
    
    if amount == None:
        amount = input("ENTER AMOUNT OF COPIES --> ")
    query = f"INSERT INTO storage_placebook (place_id, title_id, copies_num)\
        VALUES ({place}, {book_id}, {amount})"
    cur.execute(query)
    print()
    typer.secho('BOOKS ARE SUCCESSFULLY ADDED TO PLACE', fg=typer.colors.GREEN)
    print()
    
    ##############

@app.command("display_table")
def display_table():
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Column 1", style="dim", width=10)
    table.add_column("Column 2", style="dim", min_width=10, justify=True)

    table.add_row('Value 1', 'Value 2')
    table.add_row('Value 3', 'Value 4')
    table.add_row('Value 5', 'Value 6')

    console.print(table)


@app.command("show_book")
def show_book():
    query = 'SELECT * FROM storage_book'
    cur.execute(query)
    data = cur.fetchone()
    print(data)

# READ EXCEL
@app.command("read_excel")
def add_book_excel():
    
    import openpyxl as xl
    from openpyxl.chart import BarChart, Reference
    
    wb = xl.load_workbook('english_books1.xlsx')
    sheet = wb['Blad1']
    ws = wb.active
    values = list(ws.values)

    for i in range(1, len(values)):
        row = values[i]
        isbn, title, author, category_name, level, year, location, quantity, description  = row
        
    #     # add_book:
        add_title_excel(row)
        

def fetch():
    query = f'''SELECT title FROM storage_title WHERE id= (SELECT MAX(id) FROM storage_title)'''
    cur.execute(query)
    data = cur.fetchall()
    print("COUNT ROW IS", data)

    
if __name__ == "__main__":
    get_bookdata()
    # print(is_exists('9783770740215', 'Wo geht der Astronaut aufs Klo? - Hardcover'))
    # fetch()
