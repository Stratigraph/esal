# Event objects
#
# Copyright (c) 2015 Aubrey Barnard.  This is free software.  See
# LICENSE for details.

import collections

from . import general
from .general import Any


# Export public API
__all__ = (
    'Header',
    'Event',
    )


class Header:

    """A Header describes a collection of fields, like a tuple or a row
    in a table, by giving the fields names and indices.  This supports
    field access by name for objects without such existing support.
    """

    # TODO what about a sparse header (non-contiguous indices)?

    def __init__(self, names):
        """Creates a header using the given iterable of field names, in
        order.
        """
        self.idxs_to_names = tuple(names)
        self.names_to_idxs = dict(
            (name, index) for index, name in
            enumerate(self.idxs_to_names))

    def __len__(self):
        """Returns the number of fields."""
        return len(self.idxs_to_names)

    def __getitem__(self, key):
        """Returns the index of the given key (name or index)."""
        if isinstance(key, int):
            if key < 0 or key >= len(self.idxs_to_names):
                raise IndexError(key)
            return key
        elif isinstance(key, str):
            return self.names_to_idxs[key]
        else:
            raise KeyError(key)

    def name_of(self, index):
        """Returns the name of the given index."""
        return self.idxs_to_names[index]

    def index_of(self, name):
        """Returns the index of the given name."""
        return self.names_to_idxs[name]

    @property
    def names(self):
        """Names of the fields in this header."""
        return self.idxs_to_names


def _valuepred_matches_value(valuepred, value):
    return (valuepred is Any or valuepred == value or
            (callable(valuepred) and valuepred(value)))


# TODO rename 'ev' -> 'type'
_EVENT_FIELD_NAMES = ('seq', 'time', 'dura', 'ev', 'val')

class Event(collections.namedtuple('_Event', _EVENT_FIELD_NAMES)):

    """Event(sequence_id, start_time, duration, event, value)

    An event is a tuple of values representing the occurrence of an
    event in a sequence.  The fields are ordered so that events have a
    useful default sort order and are as follows.  The fields can be
    accessed by index, name, or attribute reference.

    * sequence_id, 'seq': ID of the containing sequence
    * start_time, 'time': When this event happened.  Can be any
      orderable type such as integer, float, str, date, time, or
      datetime.
    * duration, 'dura': How long the event lasted in a form compatible
      with the start time.  Can be omitted for point events.
    * event, 'ev': Type of this event
    * value, 'val': Value of this event.  Can be omitted for
      binary-valued events (when the value would always be True).

    For example, a blood pressure measurement could be represented by
    the following two events:

        Event(patient0123456789, '2015-04-25T11:39', None, bpSystolic, 120)
        Event(patient0123456789, '2015-04-25T11:39', None, bpDiastolic, 80)
    """

    _header = Header(_EVENT_FIELD_NAMES)

    # Override __new__ to enable default values and specifying values by
    # name.  Otherwise tuple needs all values specified up front.
    def __new__(cls, seq=None, time=None, dura=None, ev=None, val=None):
        # Copy from source generated by namedtuple
        return tuple.__new__(cls, (seq, time, dura, ev, val))

    # Enable access by name as well as index
    def __getitem__(self, key):
        """Returns the item corresponding to the given key which may be
        the index or name of a field.
        """
        if isinstance(key, (int, slice)):
            return super().__getitem__(key)
        elif isinstance(key, str):
            return self[self._header.index_of(key)]
        else:
            raise KeyError(key)

    @property
    def header(self):
        """Header describing this Event record."""
        return self._header

    def sort_key(self):
        """Returns a key for sorting this event."""
        return general.iterable_sort_key(self)

    def matches(self, seq=Any, time=Any, dura=Any, ev=Any, val=Any):
        """Returns true if the fields of this event are equal to all of
        the given values; that is, a partial equality match.

        The field values can be:
        * Any: matches any value.  This is the default and is equivalent
          to leaving the field out of the equality comparison.
        * an object: matches by equality
        * a predicate: matches if the predicate is True for the value
        """
        # Order the comparisons by likely to fail first
        return (_valuepred_matches_value(ev, self.ev) and
                _valuepred_matches_value(time, self.time) and
                _valuepred_matches_value(val, self.val) and
                _valuepred_matches_value(dura, self.dura) and
                _valuepred_matches_value(seq, self.seq))
