## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2012-2013 Seecr (Seek You Too B.V.) http://seecr.nl
#
## end license ##

from time import mktime, localtime, tzname, timezone, altzone, daylight
from datetime import datetime, tzinfo, timedelta
from email import utils as email

class TimeError(Exception): pass

class _UtcTimeZone(tzinfo):
    def tzname(self, _): return "UTC"
    def utcoffset(self, _): return _NO_TIME_DELTA
    def dst(self, _): return _NO_TIME_DELTA

UTC = _UtcTimeZone()

class _LocalTimezone(tzinfo):
    def utcoffset(self, t):
        return _DST_DELTA if self._isdst(t) else _LOCAL_DELTA
    def dst(self, t):
        return _DST_DELTA - _LOCAL_DELTA if self._isdst(t) else _NO_TIME_DELTA
    def tzname(self, t):
        return tzname[self._isdst(t)]
    def _isdst(self, t):
        tt = (t.year, t.month, t.day, t.hour, t.minute, t.second, t.weekday(), 0, 0)
        stamp = mktime(tt)
        return localtime(stamp).tm_isdst > 0

Local = _LocalTimezone()

class _TzHelper(tzinfo):
    def __init__(self, utcoffset_inseconds):
        self._utcoffset_inseconds = utcoffset_inseconds
    def utcoffset(self, dt):
        return timedelta(seconds=self._utcoffset_inseconds)

class ZuluTime(object):
    """Converts timestamps making sure time zone information is properly dealt with."""

    def __init__(self, input=None, timezone=None):
        """Parses verious formats safely, without loosing time zone information."""
        if input is None:
            self._ = datetime.now(UTC)
        elif input.endswith('Z'):
            self._ = datetime.strptime(input, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        else:
            result = utcoffset = email.parsedate_tz(input)
            if result is None:
                raise TimeError("Format unknown")
            year, month, day, hour, minutes, seconds, _, _, _, utcoffset = email.parsedate_tz(input)
            if utcoffset is None:
                if timezone is None:
                    raise TimeError("Time zone unknown, use timezone=")
            else:
                timezone = _TzHelper(utcoffset)
            self._ = datetime(year, month, day, hour, minutes, seconds, 0, timezone).astimezone(UTC)

    def display(self, f):
        """Unsafe way to generate display strings that possibly loose information."""
        return self._.strftime(f)

    def iso8601(self, timezone=UTC):
        """A safe way to generate ISO date that contains proper timezone information"""
        return self._format(_ISO8601, timezone)

    def rfc2822(self, timezone=UTC):
        """A safe way to generate RFC2822 date that contains proper timezone information"""
        return self._format(_RFC2822, timezone)

    def zulu(self, timezone=UTC):
        """A safe way to generate Zulu date that contains proper timezone information"""
        return self._format(_ZULU, timezone)

    def _format(self, f, timezone=UTC):
        return self._.astimezone(timezone).strftime(f)

    def add(self, **kwargs):
        self._ += timedelta(**kwargs)

    @property
    def year(self): return self._.year

    @property
    def month(self): return self._.month

    @property
    def day(self): return self._.day

    @property
    def hour(self): return self._.hour

    @property
    def minute(self): return self._.minute

    @property
    def second(self): return self._.second

    @property
    def timezone(self): return self._.tzinfo

    @property
    def weekday(self): return self._.weekday

_RFC2822 = "%a, %d %b %Y %H:%M:%S %z"
_ISO8601 = "%Y-%m-%dT%H:%M:%S %Z"
_ZULU =  "%Y-%m-%dT%H:%M:%SZ"

_NO_TIME_DELTA = timedelta(0)
_LOCAL_DELTA = timedelta(seconds=-timezone)
_DST_DELTA = timedelta(seconds=-altzone) if daylight else _LOCAL_DELTA

