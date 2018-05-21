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
            # Skip invalid transactions
            if transaction['isError'] != '0':
            	continue
            yield transaction
        if len(page['result']) < 10000:
            break
        transactions_params['page'] += 1


def get_transactions(address, startblock=0):
    for transaction in _transactions(
        action='txlist',
        address=address,
        startblock=startblock,
    ):
        # Not sure if this can be zero if isError is zero, but just in case
        if transaction['txreceipt_status'] == '1':
            incoming = transaction['to'] == address
            yield {
                'hash': transaction['hash'],
                'block_number': transaction['blockNumber'],
                'timestamp': int(transaction['timeStamp']),
                'value': int(transaction['value']) * (1 if incoming else -1),
                'gas_price': int(transaction['gasPrice']),
                'gas_used': int(transaction['gasUsed']),
                'function': transaction['input'][:10],
                'other_address': transaction['from'] if incoming else transaction['to'],
            }

def get_internal_transactions(address, startblock=0):
    for transaction in _transactions(
        action='txlistinternal',
        address=address,
        startblock=startblock
    ):
        incoming = transaction['to'] == address
        yield {
            'hash': transaction['hash'],
            'trace_id': transaction['traceId'],
            'block_number': transaction['blockNumber'],
            'timestamp': int(transaction['timeStamp']),
            'value': int(transaction['value']) * (1 if incoming else -1),
            'other_address': transaction['from'] if incoming else transaction['to'],
        }
