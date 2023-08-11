import time
import requests
import selectorlib
import smtplib
import ssl
import os
import sqlite3

PASSWORD = "GMAIL APP PASSWORD"
URL = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/39.0.2171.95 Safari/537.36'}

connection = sqlite3.connect("data.db")


def scrape(url):
    """Scrape the page source from the URL"""
    response = requests.get(url, headers=HEADERS)
    source_code = response.text
    return source_code


def extract(source_code):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source_code)["tours"]  # have to reflect name in yaml
    return value


def send_email(message):
    host = "smtp.gmail.com"
    port = 465

    username = "YOUR GMAIL"
    password = PASSWORD

    receiver = "YOUR GMAIL"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)
    print("Email was sent!")


def store(extracted_event):
    row = extracted_event.split(",")
    row = [item.strip() for item in row]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
    connection.commit()


def read(extracted_data):
    row = extracted_data.split(",")
    row = [item.strip() for item in row]
    band, city, date = row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?",
                   (band, city, date))
    rows = cursor.fetchall()
    print(rows)
    return rows


if __name__ == "__main__":
    i = 0
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)

        if extracted is None:  # if a connection cannot be established
            if i == 0:  # we go with this demonstration data
                extracted = "Lions of the IDE, Clone City, 6.5.2088"
            if i == 1:
                extracted = "Feng Suave, Minimalia City, 5.5.2089"
            else:
                break
        i += 1

        if extracted != "No upcoming tours":
            extracted_row = read(extracted)
            if not extracted_row:
                store(extracted)
                send_email(message="Hey, new event was found")
        time.sleep(2)
