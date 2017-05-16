# -*- coding: utf-8 -*-
import os
import re
import requests
import pygsheets
import callr
from pyshorteners import Shortener
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
PRICE_SELECTOR = '.price'

CALLR_API_LOGIN = os.environ.get('LOGIN')
CALLR_API_PASSWORD = os.environ.get('PASSWORD')
GOOGLE_SHORTENER_API_KEY = os.environ.get('API_KEY')

PHONE = os.environ.get('PHONE')

shortener = Shortener('Google', api_key=GOOGLE_SHORTENER_API_KEY)
api = callr.Api(CALLR_API_LOGIN, CALLR_API_PASSWORD)

def get_scraped_page(url):
    res = requests.get(url)
    return Bs(res.text, 'lxml')

def clean_markup(string):
    return re.sub(r'<[^>]*>', '', string)

def clean_spaces(string):
    string = re.sub('\n|\r|\t', ' ', string)
    return re.sub('\s{2,}', ' ', string).strip()

def process_listings_page(link):
    try:
        dom = get_scraped_page(link)

        details_urls = [URL_DOMAIN + btn.get('href') for btn in dom.select('.btn-details')]

        return [
            process_listing(listing_details_url)
            for listing_details_url in details_urls
        ]

    except Exception as e:
        print(e)

def process_listing(listing):
    dom = get_scraped_page(listing)

    print('Processing ' + listing)

    specs = ' / '.join([
        clean_spaces(clean_markup(str(li).replace('<strong>', ': ').lower()))
        for li in dom.select(SPECS_SELECTOR)[0].select('li')
    ])

    description_body = dom.select(DESCRIPTION_SELECTOR)[0]
    location = dom.select(GEOLOC_SELECTOR)[0].h2.text
    metro = ', '.join([clean_markup(elm.get_text()) for elm in dom.select(METRO_SELECTOR)])
    description = clean_spaces(description_body.get_text())
    price = dom.select(PRICE_SELECTOR)[0].text

    return {
        'specs': specs,
        'location': location,
        'description': description,
        'metro': metro,
        'url': listing,
        'price': price
    }

def send_data_via_sms(data):
    msg = "{0} - {1} - {2} - {3} - {4}".format(
        data['specs'], data['price'], data['location'], data['metro'],
        shortener.short(data['url'])
    )
    api.call('sms.send', 'SMS', PHONE, msg, None)

try:
    gc = pygsheets.authorize(service_file='credentials.json')

    sheet = gc.open_by_url(SPREADSHEET_URL).sheet1

    dom = get_scraped_page(SEARCH_PAGE)

    links = [SEARCH_PAGE] + [
        URL_DOMAIN + a.get('href')
        for a in dom.select(PAGINATION_SELECTOR)
    ]

    urls_stored = sheet.get_col(5)

    for link in links:
        for ls in process_listings_page(link):
            if ls['url'] not in urls_stored:
                sheet.insert_rows(row=0, values=[
                    ls['specs'], ls['location'],
                    ls['description'], ls['metro'], ls['url']
                ])

                # If this is not the first time we store data (i.e. urls_stored is not empty)
                # we want to receive SMS alerts with the newest listings (i.e. those we hadn't before).
                if len(urls_stored) > 0:
                    send_data_via_sms(ls)

except Exception as e:
    print(e)
