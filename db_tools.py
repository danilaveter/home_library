#  install KB plugin for ISBNLIB please using pip install isbnlib-kb

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
import isbnlib
from isbnlib import meta, is_isbn13, is_isbn10, cover, desc
from isbnlib.registry import bibformatters

# import pandas as pd

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

# def is_exists(isbn, title):
#     '''Return True if book already exists in the DB'''
#     query = f"SELECT id FROM store_book \
#         WHERE isbn = '{isbn}' AND title = '{title}'"
#     cur.execute(query)
#     id = cur.fetchone()
#     if id:
#         return id[0]
#     return False

# Collect data

@app.command('bookdata')
def get_bookdata(isbn, service: str = 'default'):
    # isbn = input('Enter ISBN  ')
    ''' This returns title, author, puplisher, year, language of the book usind ISBN13'''

    print("Looking up data using ", service)
    isbn = '9781838690588'

    try:
        metabook = isbnlib.meta(isbn)

        if not metabook:
            print('No data in the default servise')
            metabook = meta(isbn, service='kb')

        if metabook:
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
        else:
            return False

    except Exception as e:
        print(e)
        return False


        
    

# ADD to Database

def is_exists(isbn):
    ''' Returns 'True' if book already exists in the DB '''
    query = f"SELECT id FROM app_title \
        WHERE isbn = '{isbn}'"
    
    cur.execute(query)
    id = cur.fetchone()
    if id:
        print(f'ID in collection: {id}')
        return id[0]
    print("Title doesnt exist in the Biblionef collection")
    return False
    
@app.command()
def add_book_isbn():
    while True:
        print()
        isbn_ = input("ENTER THE ISBN ---> ")
        if (is_isbn13(isbn_) + is_isbn10(isbn_)) < 1:
            print('ISBN is not correct')
            reaction = input("Continue?  y/n")
            if reaction in 'yY':
                pass
            else:
                continue
        
        bookdata = get_bookdata(isbn_)

        if bookdata:
            isbn = bookdata["ISBN-13"]
            title = bookdata['Title'][250:]
            author = bookdata['Author']
            publisher = bookdata['Publisher']
            year = bookdata['Year']
            lang = bookdata['Language']
            description = bookdata['desc']
            
            if not year:
                year = 0
    
            publisher = publisher.replace("'", "''")
            author = author.replace("'", "''")
            description = description.replace("'", "''")
            title = title.replace("'","''")

            query = f'''INSERT INTO app_title (isbn, title, author, publisher, year, language, description, user_id, date_added, in_stock, is_active, ignore_amount)
                VALUES ('{isbn}', '{title}', '{author}', '{publisher}', '{year}', '{lang}', '{description}', '1', CURRENT_TIMESTAMP, TRUE, TRUE, FALSE)'''
            
            title_id = is_exists(isbn)
            
            if not title_id:
                cur.execute(query)
                conn.commit()
                print('The Title is successfully added')
                
            title_id = is_exists(isbn)
            add_to_place(title_id)
        

        else:
            id = is_exists(isbn_)
            if id:
                add_to_place(id)
            else:
                message = '''ISBN is correct but data not found.
                    Please add the titel by hand.'''
                typer.secho(message, fg=typer.colors.RED)
                
                act = input("Add title by hand? [y/n]  ")
                if act.lower() == "y":
                    add_title_hand()
                
    conn.close()


@app.command("add_title_hand")
def add_title_hand():
    ''' Add book data to DB
    '''
    print()
    print('MANUAL ADDING MODE')
    print()
    isbn = input("Enter the ISBN: ")
    title = input("Enter the Title: ")
    author = input("Enter the Author: ")
    publisher = input("Enter the publisher: ")
    year = input("Enter the Year: ")
    lang = input("Enter the Language: ")
    description = input("Add the description: ")

    description = description.replace("'", "''")
    title = title.replace("'","''")
    publisher = publisher.replace("'","''")
    author = author.replace("'","''")

    if not year:
        year = 0

    query = f'''INSERT INTO app_title (isbn, title, author, publisher, year, language, description, date_added, in_stock, must_always_be) VALUES ('{isbn}', '{title}', '{author}', '{publisher}', '{year}', '{lang}', '{description}', CURRENT_TIMESTAMP, TRUE, FALSE)'''
    
    if not is_exists(isbn):
        cur.execute(query)
        title_id = is_exists(isbn)
        conn.commit()
        print(f"Success added ID is {title_id}")
    else:
        id = is_exists(isbn)
        print(f"Book is already added to table app_title. ID is {title_id}")
    
    add_to_place(title_id)

        

@app.command('add_title_excel')
def add_title_excel(row):
    "Add the title and boot-to-place one by one from Excel's rows"
    isbn, title, author, category_name, level_name, year, location, quantity, description  = row
    description = description.replace("'", "''")
    title = title.replace("'", "''")
    query = f"""INSERT INTO app_title (isbn, title, author, category_name, level_name, year, description, date_created)\
        VALUES ('{isbn}', '{title}', '{author}', '{category_name}', '{level_name}', '{year}', '{description}', CURRENT_TIMESTAMP)"""
    

    if not is_exists(isbn):
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



def add_to_place(title_id, place: Optional[int] = None, amount: Optional[int] = None):
    '''Add book to place. ID=1 -> Forth room. ID=2 -> Cold room. ID = 3 -> English room'''
    if place == None:
        # place = input("ENTER THE PLACE ID (cold_room it's 3) --> ")
        
        place = 304 # <<< -----  CHANGE THE PLACE!!!!! -------------------------------------------
    
    place_amount = is_placebook_exist(title_id, place)
    if place_amount:
        print(f'Place book already exist. Current amount is {place_amount}')
    else:
        print('place_amount is null')

    if amount == None:
        print()
        amount = input("ENTER AMOUNT OF COPIES --> ")
        if not amount:
            amount = 1
            print("Amount is 1")
        else:
            amount = int(amount)
            
    handle = f"{place}_{title_id}_{amount}"
    
    # chech
    
    
    if place_amount:
        place_amount = int(place_amount)
        query = f"UPDATE app_placebook SET amount = {amount + place_amount}, date_added = CURRENT_TIMESTAMP\
        WHERE title_id = {title_id} AND place_id = {place}"
        print()
        
    else:
        query = f"INSERT INTO app_placebook (place_id, title_id, amount, date_added)\
        VALUES ({place}, {title_id}, {amount}, CURRENT_TIMESTAMP)"
        
    cur.execute(query)
    conn.commit()
    print()
    typer.secho('BOOKS ARE SUCCESSFULLY ADDED TO PLACE', fg=typer.colors.GREEN)
    print()
    
    ##############


def is_placebook_exist(title_id, place):
    ''' Returns amount of books if placebook already exists in the DB '''

    query = f"SELECT amount FROM app_placebook \
        WHERE title_id = {title_id} AND place_id = {place}"
    
    cur.execute(query)
    amount = cur.fetchone()
    if amount:
        print('Amount is: ', amount)
        return amount[0]
    return False
    


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
    query = 'SELECT * FROM app_book'
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
    query = f'''SELECT title FROM app_title WHERE id= (SELECT MAX(id) FROM app_title)'''
    cur.execute(query)
    data = cur.fetchall()
    print("COUNT ROW IS", data)

    
if __name__ == "__main__":
    add_book_isbn()
    # print(is_exists('9783770740215', 'Wo geht der Astronaut aufs Klo? - Hardcover'))
    # fetch()
    # add_to_place(490)
    # add_title_hand()