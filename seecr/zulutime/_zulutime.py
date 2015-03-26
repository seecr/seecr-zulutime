## begin license ##
#
# Zulutime helps formatting and parsing timestamps.
#
# Copyright (C) 2012-2015 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Zulutime"
#
# "Zulutime" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Zulutime" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Zulutime"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import re
from time import mktime, localtime, tzname, timezone, altzone, daylight
from datetime import datetime, tzinfo, timedelta
from email import utils as email
from calendar import timegm

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

    def __init__(self, input=None, timezone=None, _=None):
        """Parses verious formats safely, without loosing time zone information."""
        if _ is not None:
            self._ = _
        elif input is None:
            self._ = datetime.now(UTC)
        else:
            lastTimeError = None
            for m in [self._parseZulutimeFormat, self._parseLocalFormat, self._parseRfc2822]:
                try:
                    self._ = m(input, timezone)
                    break
                except TimeError, e:
                    lastTimeError = e
                except Exception:
                    pass
            else:
                if lastTimeError is not None:
                    raise lastTimeError
                raise TimeError('Format unknown')

    @classmethod
    def parseLocal(cls, input):
        return cls(input=input, timezone=Local)

    @classmethod
    def parseEpoch(cls, seconds):
        return cls(_=datetime.utcfromtimestamp(seconds).replace(tzinfo=UTC))

    def display(self, f):
        """Unsafe way to generate display strings that possibly loose information."""
        return self._.strftime(f)

    def iso8601(self, timezone=UTC):
        """A safe way to generate ISO date that contains proper timezone information"""
        return self._format(_ISO8601, timezone)

    def rfc2822(self, timezone=UTC):
        """A safe way to generate RFC2822 date that contains proper timezone information"""
        return self._format(_RFC2822, timezone)

    def rfc1123(self):
        """The expires date in HTTP cookies is specified in this format."""
        return self._format(_RFC1123, timezone=UTC)

    def zulu(self, timezone=UTC):
        """A safe way to generate Zulu date that contains proper timezone information"""
        return self._format(_ZULU, timezone)

    def local(self):
        return self._format(_LOCAL, Local)

    def formatDutch(self, time):
        t = self._.astimezone(Local)
        date = '{day} {month} {year}'.format(
                day=t.day,
                month=_MONTHS['nl'][t.month],
                year=t.year
            )
        if not time:
            return date
        return '{date}, {hour:02d}:{minute:02d} uur'.format(
            date=date,
            hour=t.hour,
            minute=t.minute,
            )

    def _format(self, f, timezone=UTC):
        return self._.astimezone(timezone).strftime(f)

    def add(self, **kwargs):
        return type(self)(_=self._ + timedelta(**kwargs))

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

    @property
    def epoch(self):
        return timegm(self._.utctimetuple())

    @staticmethod
    def _parseZulutimeFormat(input, timezone):
        timezone = UTC if timezone is None else timezone
        input = _ZULU_FRACTION_REMOVAL_RE.sub(r'\g<delimSeconds>\g<Z>', input)
        return datetime.strptime(input, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone)

    @staticmethod
    def _parseLocalFormat(input, timezone):
        timezone = UTC if timezone is None else timezone
        return datetime.strptime(input, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone)

    @staticmethod
    def _parseRfc2822(input, timezone):
        result = utcoffset = email.parsedate_tz(input)
        if result is None:
            raise TimeError("Format unknown")
        year, month, day, hour, minutes, seconds, _, _, _, utcoffset = email.parsedate_tz(input)
        if utcoffset is None:
            if timezone is None:
                raise TimeError("Time zone unknown, use timezone=")
        else:
            timezone = _TzHelper(utcoffset)
        return datetime(year, month, day, hour, minutes, seconds, 0, timezone).astimezone(UTC)

_RFC2822 = "%a, %d %b %Y %H:%M:%S %z"
_RFC1123 = "%a, %d %b %Y %H:%M:%S GMT"
_ISO8601 = "%Y-%m-%dT%H:%M:%S %Z"
_ZULU =  "%Y-%m-%dT%H:%M:%SZ"
_LOCAL =  "%Y-%m-%d %H:%M:%S"

_NO_TIME_DELTA = timedelta(0)
_LOCAL_DELTA = timedelta(seconds=-timezone)
_DST_DELTA = timedelta(seconds=-altzone) if daylight else _LOCAL_DELTA

_MONTHS = {
    'nl': [
            None,
            'januari',
            'februari',
            'maart',
            'april',
            'mei',
            'juni',
            'juli',
            'augustus',
            'september',
            'oktober',
            'november',
            'december'
        ]
}

_ZULU_FRACTION_REMOVAL_RE = re.compile(r'(?P<delimSeconds>:[0-9]+)\.[0-9]+(?P<Z>Z)$')

