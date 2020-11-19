import requests
import os
from bs4 import BeautifulSoup as bs
import logging

webhook_url = os.getenv('WEBHOOK_URL')
webhook_6800_url = os.getenv('WEBHOOK_6800_URL')

def scrape_stock_data(url):
    soup = bs(requests.get(url).text, 'html.parser')
    table = soup.find_all(id='data')[0]
    rows = table.find_all('tr')[1:]
    results = []
    for row in soup.find_all('tr')[1:]:
        try:
            cells = row.find_all('td')
            if len(cells) != 4:
                continue
            name = cells[0].text.strip()
            link = cells[0].find('a').get('href')
            status = cells[1].text.lower()
            result = [name, link, status]
            results.append(result)
        except Exception as e:
            logging.warning('failed to parse row: %s', row, exc_info=True)
    return results

def send_discord_webhook(product_name, link, users):
    # user_tags = ' '.join(users)
    user_tags = '@here'
    msg = f'{user_tags} {product_name} is in stock! order at:\n{link}'
    data = {'content': msg}
    url = webhook_url if '6800' not in product_name else webhook_6800_url
    print(requests.post(url, data=data).text)

searches = {
        'NVIDIA RTX 3080 FE' : [], 
        'NVIDIA RTX 3080 TI' : [], 
	'5900X': [],
	'3080': [],
	'6800XT': [],
	'5950X': []
        }

def run(event, context):
    urls = ['https://www.nowinstock.net/computers/videocards/nvidia/rtx3080/',
            'https://www.nowinstock.net/computers/processors/amd/',
            'https://www.nowinstock.net/computers/videocards/amd/rx6800xt/']

    items = map(scrape_stock_data, urls)
    instock_items = filter(lambda x: 'in stock' in x, items)
    for name, link, status in instock_items:
        for search, users in searches.items():
            if status == 'in stock' and search in name:
                send_discord_webhook(name, link, users)

if __name__ == '__main__':
    run(None, None)
