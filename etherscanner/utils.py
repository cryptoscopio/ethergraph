from collections import defaultdict
from decimal import Decimal


def collate(*args, interval=600, value_type=int):
    """
    Collates any number of iterators of (timestamp, value) tuples into a
    cumulative time series, with times grouped by rounding down to the nearest
    increment of the provided interval (in seconds). The `value_type` can be
    used to override the assumed value type of int.

    Yields a tuple of the form (timestamp, cumulative_value, ...), with the
    cumulative value for each of the provided iterators.
    """
    # Aggregate each iterator into a dictionary of rounded timestamps and the
    # sum of the values observed within an interval's distance in the future
    # from the rounded timestamp.
    aggregates = []
    for series in args:
        aggregate = defaultdict(value_type)
        for timestamp, value in series:
            rounded = timestamp // interval * interval
            aggregate[rounded] += value
        aggregates.append(aggregate)
    # Determine earliest and latest timestamps across all the interators
    start_timestamp = min([min(d.keys()) for d in aggregates if d.keys()] or [0])
    end_timestamp = max([max(d.keys()) for d in aggregates if d.keys()] or [0]) + interval
    # Maintain the cumulative total for each iterator in `cumulative`
    cumulative = [value_type()] * len(args)
    for index in range(start_timestamp, end_timestamp, interval):
        # Updates the mutable `cumulative` list in-place
        for i, aggregate in enumerate(aggregates):
            cumulative[i] += aggregate.get(index, value_type())
        yield [index] + cumulative


def wei_to_eth(value):
    """Convert wei value into ETH value as a Decimal"""
    return Decimal(value) / Decimal('1000000000000000000')

def gwei_to_eth(value):
    """Convert gwei value into ETH value as a Decimal"""
    return Decimal(value) / Decimal('1000000000')
