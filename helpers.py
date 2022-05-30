import csv
import os
# from flickr_api_helper import *
import datetime
import sqlite3
import smtplib
# from geo_api_helper import *


def read_csv(filename):
    """This function opens csv file, reads it into a dictionary and converts in json format"""
    try:
        with open(filename, encoding='utf8') as file:
            cook_book_list = []
            reader = csv.DictReader(file)
            for row in reader:
                cook_book_list.append(row)
    except FileNotFoundError:
        return {}
    else:
        return cook_book_list


def extract_recepies(cookdb):
    """This function takes a list of recepies and creates a dictionary to display on website"""
    recepies = {}
    for recipe in cookdb:
        recepies[recipe['name'].capitalize()] = recipe['ingridients']
    return recepies


def make_html_table(data):
    if len(data) == 0:
        return "<div><h1>Nothing found, please try again</h1></div>"
    """Function takes a dictionary as input and returns html-formatted table with data from dictionary"""
    html_table = '<table>\n'
    html_table += '<tr>\n<th>Recipe</th>\n<th>Ingridients</th>\n</tr>\n'
    for key, value in data.items():
        row = '<tr>\n<td>' + f"{make_post_link_recipe(key)}" + '</td>\n' + '<td>' + make_post_link_ingridient(value) + \
              '</td>\n</tr>\n'
        html_table += row
    else:
        html_table += '</table>'
    return html_table


def make_post_link_recipe(name):
    """Creates a form with a psot method so you can pass recepi name to handler and load a recipe"""
    form = f'''<form action="/recipe_request.html" method="post" class="inline">
    <button style="background: none; border: none; text-decoration: underline; cursor: pointer; text-align:left" 
    type="submit" name="recipe" value="{name}">
      {name}</button>'''
    return form


def make_post_link_ingridient(name):
    """Creates a form with a psot method so you can pass recepi name to handler and load a recipe"""
    form = ''
    for item in name.split(','):
        form += f'''<form action="/search_result.html" method="post" class="inline">
    <button style="background: none; border: none; text-decoration: underline; cursor: pointer; text-align:left" 
    type="submit" name="search" value="{item.strip()}">
      {item.strip().capitalize()}</button>''' + ' '
    return form


def load_recipe_from_file(name):
    read_recipe = ''
    with open('data/recepies.txt', encoding='utf-8-sig') as file:
        for line in file:
            if line.strip().lower() == name.lower():
                while len(line) > 1:
                    line = file.readline()
                    read_recipe += line
                return read_recipe
    return 'The recipe is not found'


def make_search(keyword):
    """Looks for a value provided in database, returns a dictionary with results"""
    recepies = {}
    cookdb = extract_recepies(read_csv('data/cookbook.csv'))
    if '+' in keyword:
        keyword = keyword.replace('+', ' ')
    for key, value in cookdb.items():
        if keyword.lower() in key.lower() or keyword.lower() in value.lower():
            recepies[key] = value
    return recepies


def return_recepies_html(data):
    """Function takes a dictionary as input and returns html-formatted table with recepies to display on web page"""
    html_table = '<table>\n'
    for num, key in enumerate(data.keys()):
        if num == 0 or num % 5 == 0:
            html_table += '<tr>\n'
        row = '<td>' + make_post_link_recipe(key) + '</td>\n'
        html_table += row
        if num % 5 == 4 or num == len(data)-1:
            html_table += '</tr>\n'
    else:
        html_table += '</table>'
    return html_table


def return_ingridients_html(data):
    """Function takes a dictionary as input and returns html-formatted table with ingridients to display on web page"""
    html_table = '<table>\n'
    ingridients = set(item.strip() for items in data.values() for item in list(items.split(',')))
    for num, val in enumerate(sorted(ingridients)):
        if num == 0 or num % 5 == 0:
            html_table += '<tr>\n'
        row = '<td>' + make_post_link_ingridient(val) + '</td>\n'
        html_table += row
        if num % 5 == 4 or num == len(data)-1:
            html_table += '</tr>\n'
    else:
        html_table += '</table>'
    return html_table


def gallery_loader():
    """Prepares file saved locally to be send to gallery"""
    file_list = os.listdir('./img') # Getting list of files saved locally in /img folder
    data = '<table>\n'
    # Going through the loop to cycle through all the files and create a table where cells are images
    for num, file in enumerate(file_list):
        if file == 'nothing_to_display.jpg':
            continue
        if num == 0 or num % 3 == 0:
            data += '<tr>\n'
        file_path = os.path.join('/img', file)
        name = file[:-4].replace('_', ' ')
        name = name.swapcase()
        data += f'<td><h3>{name}</h3><br><br><img src={file_path} alt="{file}"/></td>'
        if num % 3 == 2 or num == len(data)-1:
            data += '</tr>\n'
    else:
        data += '</table>\n'
    return data


def feedback_loader():
    message = ''
    try:
        db = sqlite3.connect('data/users.sqlite3')
        data = db.execute('SELECT * FROM feedback').fetchall()
    except (FileNotFoundError, sqlite3.DatabaseError):
        return 'Could not open Database'
    else:
        db.close()
        for entry in data:
            message += f"<h3>{entry[1]} said @ {entry[3]}:</h2><br>"
            msg = entry[2]
            msg = msg.replace('+', ' ')
            message += f"<div>{msg}</div><br>"
            message += "<br>"
        return message


def feedback_saver(message, ip_address):
    try:
        db = sqlite3.connect('data/users.sqlite3')
        db.execute('CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, message TEXT, datetime TEXT, ip TEXT)')
    except (FileNotFoundError, sqlite3.DatabaseError):
        return 'Entry has not been added'
    else:
        name = message[0][6:]
        msg = message[1][6:]
        now = datetime.datetime.now()
        date = now.strftime('%d-%b-%Y, %H:%M:%S')
        try:
            db.execute("INSERT INTO feedback (name, message, datetime, ip) VALUES (?, ?, ?, ?)",
                       (name, msg, date, ip_address))
        except sqlite3.DatabaseError:
            return 'Database Error. Could not add data.'
        else:
            db.commit()
            db.close()
            return 'Feedback has been added, update page to see'


def register_user(data, ip_address):
    name = data[0][5:]
    email = data[1][6:]
    now = datetime.datetime.now()
    date = now.strftime('%d-%b-%Y, %H:%M:%S')
    try:
        age = int(data[2][4:])
    except (TypeError, ValueError):
        return 'Age must contain only digits'
    if not "%40" in email:
        return 'Please enter valid email'
    try:
        result = geo_request(ip_address)
        country = result['country']
    except KeyError:
        country = 'Unknown'
    email = email.replace("%40", "@").lower()
    try:
        db = sqlite3.connect('data/users.sqlite3')
        db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age TEXT, \
                   email TEXT UNIQUE, datetime TEXT, country TEXT)')
    except (FileNotFoundError, sqlite3.DatabaseError):
        return 'Entry has not been added'
    else:
        now = datetime.datetime.now()
        date = now.strftime('%d-%b-%Y, %H:%M:%S')
        try:
            db.execute("INSERT INTO users (name, age, email, datetime, country) VALUES (?, ?, ?, ?, ?)",
                       (name, age, email, date, country))
        except sqlite3.IntegrityError:
            return "Email already in database"
        except sqlite3.DatabaseError:
            return 'Database Error. Could not add data.'
        else:
            db.commit()
            db.close()
            send_email(name, email)
            return 'User has been registered. Keep an eye for updates'


def send_email(name, email):
    sender = 'olesliusarenko@gmail.com'
    passw = 'bvhfyt123#f'
    receivers = [email]
    message = f"""From: Ultimate Cookbook <ultimatecookbook.com>
To: {name} <{email}>
Subject: Thank you for registering!

    Congratulations, {name}! You have been registered at the ultimate cookbook website!
    """
    try:
        session = smtplib.SMTP('smtp.gmail.com', 25)
        session.starttls()
        session.login(sender, passw)
        session.sendmail(sender, receivers, message)
        session.close()
    except Exception:
        print('Something went wrong')
