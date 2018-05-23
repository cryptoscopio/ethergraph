import csv
import datetime

from django.conf import settings
from django.db import DatabaseError
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views import View

from . import fetcher, models, utils


to_eth = utils.gwei_to_eth if settings.ETHERSCAN_USE_GWEI else utils.wei_to_eth

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
        address = address.lower()
        try:
            models.Transaction.fetch(address)
            models.InternalTransaction.fetch(address)
        except Exception as e:
            # Never catch database errors, they invalidate transactions
            if isinstance(e, DatabaseError):
                raise
            # If fetching failed, we should still output what data we have
            raise
        transactions = models.Transaction.objects.filter(address=address)\
            .order_by('timestamp').values_list('timestamp', 'value')
        internal = models.InternalTransaction.objects.filter(address=address)\
            .order_by('timestamp').values_list('timestamp', 'value')
        for timestamp, incoming, outgoing in utils.collate(transactions, internal):
            yield (
                datetime.datetime.fromtimestamp(timestamp),
                to_eth(incoming),
                to_eth(abs(outgoing)),
                to_eth(incoming + outgoing),
            )
