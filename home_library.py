# isbn tools
from isbnlib import meta, is_isbn13, cover, desc
from isbnlib.registry import bibformatters

import pandas as pd
import os


def get_dict(box, isbn):
    ''' returns doctionary like # {'ISBN-13': '9781782094234', 'Title': 'Super Science Experiments', 'Authors': ['Chris Oxlade'], 'Publisher': 'SUPER SCIENCE EXPERIMENTS', 'Year': '2013', 'Language': 'en'}
    
    meta(isbn, service='default')
Gives you the main metadata associated with the ISBN. 

    
    '''
    servise_dict = {'goob': 'Google', 'wiki': 'KB', 'openl': 'the OpenLibrary.org'}
    print('Welcome to the meta function')
    print()
    
    try:
        for serv in servise_dict:
            dict = meta(isbn, service=serv)
            print(f'Looking in {servise_dict[serv]}... ')
            
            if not dict:
                continue
            else:
                dict['box'] = box
                dict['amount'] = input('Amount of the same books/sets:  ')
                if len(dict["Authors"]) > 1:
                    dict["Authors"] = [", ".join(dict["Authors"])]
                return dict
                
        if not dict:
            print('DATA NOT FOUND')
            return False
    except: 
        Exception
        print()
        print('error')
        print()

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
    language = input("Enter the Language: ")
    
    if not year:
        year = 0
    
    bookdata = {'ISBN-13': isbn, 'Title': title, 'Authors': [author], 'Publisher': publisher, 'Year': year, 'Language': language}
    
    return bookdata

def create_df():
    ''' returns empty pandas data frame with columns: ISBN-13, Title, Authors, Publisher, Year, Language'''
    df = pd.DataFrame(columns = ['box', 'amount', 'ISBN-13', 'Title', 'Authors', 'Publisher', 'Year', 'Language'])
    return df

def append_to_df(bookdata, df):
    '''Append to Data Frame'''
    df1 = pd.DataFrame.from_dict(bookdata)
    df = pd.concat([df, df1], ignore_index=True)
    df
    return df


def append_to_excel(df: pd.DataFrame, file, row):
    '''create or append to the excel'''
    
    if os.path.exists(file):
        with pd.ExcelWriter(file, mode='a', if_sheet_exists='overlay', engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name = 'Sheet1', startrow=row, startcol=1, header=False, index=False)
    else:
        with pd.ExcelWriter(file, mode='w') as writer:
            df.to_excel(writer, sheet_name = 'Sheet1', startrow=0, startcol=0)

def get_next_row(file):
    '''returns number of rows in excel file'''
    df = pd.read_excel(file, index_col=0)
    index = df.index
    number_of_rows = len(index)
    return number_of_rows

# programme execution

df = create_df()
file = input("Enter a name of the file or n -->  ") + '.xlsx'
while True:
    if os.path.exists(file):
        next_row = get_next_row(file) + 1
    else:
        next_row = 0
    box = input("Enter the box number or n -->  ")
    if box in 'nN':
        print('See you! Your file will saved')
        break
    while True:
        isbn = input("Enter ISBN or N for change box -->  ")
        if isbn in "nN":
            break
        if not is_isbn13(isbn):
            print('ISBN is no correct')
            continue
        bookdata = get_dict(box, isbn)
        if not bookdata:
            print('OTHER BOOK PLEASE')
            continue
        df = append_to_df(bookdata, df)
        print(df)
    append_to_excel(df, file, next_row)
    df = create_df()
            




