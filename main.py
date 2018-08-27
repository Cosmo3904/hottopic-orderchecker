import requests, json
from bs4 import BeautifulSoup as bs


def orderchecker(ordernum, email):
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    res = s.get('https://www.hottopic.com/on/demandware.store/Sites-hottopic-Site/default/OrderStatus-OrderLookup')
    soup = bs(res.text, 'lxml')
    posturl = soup.find('form', {'name':'RegistrationForm'})['action']
    payload = {
        'dwfrm_ordertrack_orderNumber' : ordernum.upper(),
        'dwfrm_ordertrack_orderEmail' : email,
        'dwfrm_ordertrack_findorder': 'Check Status',
        'dwfrm_profile_securekey' : soup.find('input', {'name' : 'dwfrm_profile_securekey'})['value']
    }
    res = s.post(posturl, data = payload)
    temp = res.text[res.text.find('OrderStatusStep'):].replace('OrderStatusStep', '')[0]
    if '1' in temp:
        orderstatus = 'Order Placed'
        trackingnum = 'N/A'
    elif '2' in temp:
        orderstatus = 'Order Confirmed'
        trackingnum = 'N/A'
    elif '3' in temp:
        orderstatus = 'Shipped'
        for item in soup.find_all('span', {'class':'order-deliveries-date'}):
            if 'Tracking number' in item.text:
                trackingnum = item.text.replace('Tracking number: ', '')
    else:
        orderstatus = 'Canceled'
        trackingnum = 'N/A'
    return({'Status' : orderstatus, 'Tracking' : trackingnum})

def jsonripper():
    try:
        with open('orders.json', 'r') as f:
            data = json.loads(f.read())
        s = input('Add More Orders? (Y/N) : ').lower()
        if s == 'y':
            while True:
                ordernum = input('Enter Order Number (Enter "Done" when done adding orders) : ')
                if ordernum.lower() == 'done':
                    break
                email = input('Enter Email for Above Order : ')
                data['Orders'].append({"Order Number" : ordernum, "Email" : email})
            with open('orders.json', 'w') as f:
                json.dump(data, f)
            print('Orders Saved for Next Check!')
        else:
            pass
    except:
        data = {}
        data["Orders"] = []
        while True:
            ordernum = input('Enter Order Number (Enter "Done" when done adding orders) : ')
            if ordernum.lower() == 'done':
                break
            email = input('Enter Email for Above Order : ')
            data['Orders'].append({"Order Number" : ordernum, "Email" : email})
        with open('orders.json', 'w') as f:
            json.dump(data, f)
        print('Orders Saved for Next Check!')
    for item in data['Orders']:
        status = orderchecker(item['Order Number'], item['Email'])
        print('[{}] [Tracking : {}]'.format(status['Status'], status['Tracking']))

jsonripper()
