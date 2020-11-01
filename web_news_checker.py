#!/usr/bin/env python3

import requests
import bs4
import difflib
import os
import datetime
import smtplib
import configparser


def check_news(old_file, new_file, title, config):
    if not os.path.isfile(old_file):
        return

    old_content = open(old_file).readlines()
    new_content = open(new_file).readlines()

    if len(new_content) == 0 or len(old_content) == 0:
        return

    if old_content == new_content:
        print('no changes')
        return

    added = []
    removed = []
    for line in difflib.unified_diff(old_content, new_content):
        if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
            continue
        if line.startswith('+'):
            added.append(line)
        elif line.startswith('-'):
            removed.append(line)
        else:
            pass

    message = 'Added: <br>\n'
    for a in added:
        message += a[1:] + '<br>\n'

    message += '<br>\n'
    message += 'Removed: <br>\n'
    for r in removed:
        message += r[1:] + '<br>\n'

    send_email(title, message, config)


def backup_file(filename):
    if os.path.isfile('{0}'.format(filename)):
        os.system("mv {0} {0}.backup".format(filename))


def send_email(subject, content, config):
    # Replace end sequence chars in subject
    for item in ["\n", "\r"]:
        subject = subject.replace(item, ' ')

    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Disposition': 'inline',
        'Content-Transfer-Encoding': '8bit',
        'From': config['DEFAULT']['EMAIL_SENDER'],
        'To': config['DEFAULT']['EMAIL_RECIPENT'],
        'Date': datetime.datetime.now().strftime('%a, %d %b %Y  %H:%M:%S %Z'),
        'X-Mailer': 'python',
        'Subject': subject
    }

    # create the message
    message = ''
    for key, value in headers.items():
        message += "%s: %s\n" % (key, value)

    # add contents
    message += "\n%s\n" % (content)

    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.ehlo()
    s.starttls()
    s.ehlo()

    s.login(config['DEFAULT']['GMAIL_LOGIN'], config['DEFAULT']['GMAIL_PASSWORD'])

    print("sending %s to %s" % (subject, headers['To']))
    s.sendmail(headers['From'], headers['To'], message.encode("utf8"))


def load_news(url, selector, output_file):
    res = requests.get(url)

    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    elem = soup.select(selector)
    with open(output_file, 'w') as f:
        for res in elem:
            f.write(res.text)


def handle_single_web(url, selector, filename, headline, config):
    backup_file(filename)
    load_news(url, selector, filename)
    check_news('{0}.backup'.format(filename), filename, headline, config)


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    urls = config['DEFAULT']['URLS'].split(', ')
    filenames = config['DEFAULT']['FILES'].split(', ')
    headlines = config['DEFAULT']['HEADLINES'].split(', ')
    selectors = config['DEFAULT']['SELECTORS'].split(', ')

    for i in range(0, len(urls)):
        handle_single_web(urls[i], selectors[i], filenames[i], headlines[i], config)



if __name__ == '__main__':
    main()
