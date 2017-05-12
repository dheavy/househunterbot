# -*- coding: utf-8 -*-
import os
import re
import requests
import pygsheets
import hashlib
from bs4 import BeautifulSoup as Bs


SEARCH_PAGE = 'http://www.pap.fr/annonce/locations-appartement-paris-18e-g37785-3-pieces-jusqu-a-1500-euros'
SPREADSHEET_URL = os.environ.get('SPREADSHEET_URL')
URL_DOMAIN = 'http://www.pap.fr'

PAGINATION_SELECTOR = '.pagination li a'
LISTING_DETAIL_BTN_SELECTOR = '.btn-details'
NEXT_PAGE_SELECTOR = '.next'
GEOLOC_SELECTOR = '.item-geoloc'
SPECS_SELECTOR = '.item-summary'
DESCRIPTION_SELECTOR = '.item-description'
METRO_SELECTOR = '.item-metro .label'
TEL_WRAPPER = '.tel-wrapper'

def clean_markup(string):
    return re.sub(r'<[^>]*>', '', string)

def clean_spaces(string):
    string = re.sub('\n|\r|\t', ' ', string)
    return re.sub('\s{2,}', ' ', string).strip()

def process_listings_page(link):
    try:
        res = requests.get(link)
        dom = Bs(res.text, 'lxml')

        details_btns = [URL_DOMAIN + btn.get('href') for btn in dom.select('.btn-details')]

        listings = []

        for listing in details_btns:
            listings.append(process_listing(listing))

        return listings

    except Exception as e:
        print(e)

def process_listing(listing):
    res = requests.get(listing)
    dom = Bs(res.text, 'lxml')

    specs = ' / '.join([
        clean_spaces(clean_markup(str(li).replace('<strong>', ': ').lower()))
        for li in dom.select(SPECS_SELECTOR)[0].select('li')
    ])

    description_body = dom.select(DESCRIPTION_SELECTOR)[0]
    location = dom.select(GEOLOC_SELECTOR)[0].h2.text
    metro = ', '.join([clean_markup(elm.get_text()) for elm in dom.select(METRO_SELECTOR)])
    description = clean_spaces(description_body.get_text())
    tel = dom.select(TEL_WRAPPER) and dom.select(TEL_WRAPPER)[0].get_text().replace('.', '') or '---'

    return {
        'id': hashlib.md5(b'' + description + tel)
        'specs': specs,
        'location': location,
        'description': description,
        'metro': metro,
        'tel': tel,
        'url': link
    }

try:
    gc = pygsheets.authorize(service_file='credentials.json')

    sheet = gc.open_by_url(SPREADSHEET_URL).sheet1

    res = requests.get(SEARCH_PAGE)
    dom = Bs(res.text, 'lxml')

    links = [SEARCH_PAGE] + [
        URL_DOMAIN + a.get('href')
        for a in dom.select(PAGINATION_SELECTOR)
    ]

    # data = []

    for link in links:
        for ls in process_listings_page(link):
            # data.append(ls)
            sheet.insert_rows(
                row=0, values=[
                    ls['id'], ls['specs'], ls['location'],
                    ls['description'], ls['metro'],
                    ls['tel'], ls['url']
                ]
            )

    # print(data)

except Exception as e:
    print(e)
