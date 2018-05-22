from django.db import models

from . import fetcher


class Transaction(models.Model):
    hash = models.CharField(max_length=66, primary_key=True)
    address = models.CharField(max_length=42, db_index=True)
    block_number = models.IntegerField()
    timestamp = models.IntegerField()
    value = models.IntegerField()
    gas_price = models.IntegerField(default=0)
    gas_used = models.IntegerField(default=0)
    function = models.CharField(max_length=10)
    other_address = models.CharField(max_length=42, db_index=True)

    @classmethod
    def fetch(cls, address):
        last_block = cls.objects.filter(address=address).aggregate(
            models.Max('block_number')
        )['block_number__max'] or -1
        for transaction in fetcher.get_transactions(address, last_block + 1):
            cls.objects.create(address=address, **transaction)


class InternalTransaction(models.Model):
    hash = models.CharField(max_length=66, db_index=True)
    trace_id = models.CharField(max_length=66)
    address = models.CharField(max_length=42, db_index=True)
    block_number = models.IntegerField()
    timestamp = models.IntegerField()
    value = models.IntegerField()
    other_address = models.CharField(max_length=42, db_index=True)

    class Meta:
        unique_together = ('hash', 'trace_id')

    @classmethod
    def fetch(cls, address):
        last_block = cls.objects.filter(address=address).aggregate(
            models.Max('block_number')
        )['block_number__max'] or -1
        for transaction in fetcher.get_internal_transactions(address, last_block + 1):
            cls.objects.create(address=address, **transaction)
