import json
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings


API_URL = 'http://api.etherscan.io/api'


def _transactions(**params):
    """
    A generic function to return transactions while handling pagination. The
    keyword arguments are used as GET parameters for the API call.
    """
    transactions_params = {
        'module': 'account',
        'startblock': 0,
        'endblock': 999999999,
        'sort': 'asc',
        'apikey': settings.ETHERSCAN_API_KEY,
        'page': 1,
        'offset': 10000,
    }
    transactions_params.update(params)
    while True:
        page = json.load(urlopen('%s?%s' % (
            API_URL, urlencode(transactions_params)
        )))
        if not len(page['result']):
            break
        for transaction in page['result']:
            # Skip invalid and zero-value transactions
            if transaction.get('txreceipt_status', '1') != '1' \
            or transaction['isError'] != '0' \
            or transaction['value'] == '0':
            	continue
            yield int(transaction['timeStamp']), int(transaction['value'])
        if len(page['result']) < 10000:
            break
        transactions_params['page'] += 1


def get_transactions(address):
    return _transactions(
        action='txlist',
        address=address,
    )

def get_internal_transactions(address):
    return _transactions(
        action='txlistinternal',
        address=address,
    )
