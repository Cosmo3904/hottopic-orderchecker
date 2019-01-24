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
    with open('test.html', 'w') as openfile:
        openfile.write(res.text)
    soup = bs(res.text, 'lxml')
    pidquan = ''
    for item in soup.find('td', {'class' : 'order-status-table-items'}).find_all('div'):
        try:
            pidquan += str(item.text)
        except:
            pass
    tempPIDQUAN = ''
    for item in pidquan.split('\n'):
        if str(len(item)) == "8":
            tempPIDQUAN += item + ':'
    for item in pidquan.split('\n'):
        if '$' in item:
            tempPIDQUAN += str(item[:item.find('$')]).replace('.0', '')
    pidquan = tempPIDQUAN
    if '1' in temp:
        orderstatus = 'Order Placed'
        trackingnum = 'N/A'
    elif '2' in temp:
        orderstatus = 'Order Confirmed'
        trackingnum = 'N/A'
    elif '3' in temp:
        orderstatus = 'Shipped'
        for item in soup.find_all('a'):
            try:
                if 'http://wwwapps.ups.com/WebTracking/track' in str(item):
                    trackingnum = item.text
                    trackingnum = trackingnum[trackingnum.find('1ZA'):]
                    while '\n' in trackingnum:
                        trackingnum=trackingnum[:trackingnum.find('\n')]
            except:
                pass
    else:
        orderstatus = 'Canceled'
        trackingnum = 'N/A'
    return({'Status' : orderstatus, 'Tracking' : trackingnum, 'PID' : pidquan})

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
        print('[{}] [{}] [Tracking : {}] [{}]'.format(item['Order Number'], status['Status'], status['Tracking'], status['PID']))

jsonripper()
