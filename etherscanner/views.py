import csv
import datetime

from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views import View

from . import fetcher, utils


class Echo(object):
    """Helper class for writing csv into a streaming response"""
    def write(self, value):
        return value

class CSVView(View):
    """An abstract view for returning CSV data"""
    def get_filename(self, request, *args, **kwargs):
        raise NotImplementedError()
    def rows(self, rewuest, *args, **kwargs):
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        writer = csv.writer(Echo())
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in self.rows(request, *args, **kwargs)),
            content_type='text/csv',
        )
        response['Content-Disposition'] = 'attachment; filename="%s"' \
            % self.get_filename(request, *args, **kwargs)
        return response


class CSVAddressView(CSVView):
    """
    Returns a CSV of timestamps and cumulative values for the ETH transferred
    as normal transaction, as regular transaction, and the balance.
    """

    def get_filename(self, request, address):
        return '%s-%s' % (address, datetime.datetime.now())

    def rows(self, request, address):
        transactions = fetcher.get_transactions(address)
        internal = fetcher.get_internal_transactions(address)
        for timestamp, incoming, outgoing in utils.collate(transactions, internal):
            yield (
                datetime.datetime.fromtimestamp(timestamp),
                utils.wei_to_eth(incoming),
                utils.wei_to_eth(outgoing),
                utils.wei_to_eth(incoming - outgoing),
            )