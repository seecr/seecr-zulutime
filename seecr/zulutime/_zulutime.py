## begin license ##
#
# Zulutime helps formatting and parsing timestamps.
#
# Copyright (C) 2012-2016 Seecr (Seek You Too B.V.) http://seecr.nl
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

class ZuluTime(object):
    """Converts timestamps making sure time zone information is properly dealt with."""

    def __init__(self, input=None, timezone=None, _=None):
        """Parses verious formats safely, without losing time zone information."""
        if _ is not None:
            self._ = _
        elif input is None:
            self._ = datetime.now(UTC)
        else:
            lastTimeError = None
            for m in [
                    self._parseIso8601,
                    self._parseZulutimeFormat,
                    self._parseLocalFormat,
                    self._parseRfc2822,
                    self._parseIso8601BasicLocal,
                    self._parseJavaDefaultDateFormat,
                    self._parseEpoch,
                ]:
                try:
                    self._ = m(input, timezone=timezone)
                    lastTimeError = None
                    break
                except TimeError, e:
                    lastTimeError = e
                except Exception:
                    pass
            else:
                if not lastTimeError is None:
                    raise lastTimeError
                raise TimeError('Format unknown')

    @classmethod
    def parseLocal(cls, input):
        return cls(input=input, timezone=Local)

    @classmethod
    def parseEpoch(cls, seconds):
        return cls(seconds, UTC)

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self._ == other._ and self.timezone == other.timezone

    def equalsPointInTime(self, other):
        return self.__class__ is other.__class__ and self._ == other._

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(str(self)))

    def __str__(self):
        return self.iso8601(self.timezone)

    def display(self, f):
        """Unsafe way to generate display strings that possibly loses information."""
        return self._.strftime(f)

    def iso8601(self, timezone=None):
        """A safe way to generate ISO date that contains proper timezone information"""
        timezone = timezone or UTC
        return self._format(_ISO8601, timezone)

    def rfc2822(self, timezone=None):
        """A safe way to generate RFC2822 date that contains proper timezone information"""
        timezone = timezone or UTC
        return self._format(_RFC2822, timezone)

    def rfc1123(self):
        """The expires date in HTTP cookies is specified in this format."""
        return self._format(_RFC1123, timezone=UTC)

    def zulu(self, timezone=None):
        """A safe way to generate Zulu date that contains proper timezone information"""
        timezone = timezone or UTC
        return self._format(_ZULU, timezone=timezone)

    def local(self):
        return self._format(_LOCAL, Local)

    def iso8601basic(self, timezone=None):
        timezone = timezone or UTC
        return self._format(''.join(element for (sep, element, l) in _ISO8601_NO_TZ), timezone=timezone)

    def javaDefaultFormat(self, timezone=None):
        timezone = timezone or UTC
        return self._format(_JAVA_DEFAULT_DATE_FORMAT, timezone=timezone)

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

    def _format(self, f, timezone=None):
        timezone = timezone or UTC
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
    def _parseIso8601(input, timezone=None):
        remainder = input.strip()
        inputParts = []
        pattern = []
        for (sep, element, l) in _ISO8601_NO_TZ:
            if sep and not remainder.startswith(sep):
                if sep == 'T' and remainder.startswith(' '):
                    pass
                else:
                    break
            fragmentSize = len(sep) + l
            inputParts.append(remainder[:fragmentSize])
            remainder = remainder[fragmentSize:]
            pattern.append(sep)
            pattern.append(element)
            if len(''.join(pattern)) >= len(''.join(inputParts)):
                break
        for tzName, tz in _TimeZone.registered.iteritems():
            if tzName in remainder:
                if timezone is None:
                    timezone = tz
                    remainder = remainder.replace(tzName, '').strip()
        if timezone is None:
            remainder, timezone = _parseTimezone(remainder)
        if remainder:
            raise ValueError("'%s' does not match" % (input + remainder))
        return datetime.strptime(''.join(inputParts), ''.join(pattern)).replace(tzinfo=timezone)

    @staticmethod
    def _parseZulutimeFormat(input, timezone):
        timezone = UTC if timezone is None else timezone
        input = _ZULU_FRACTION_REMOVAL_RE.sub(r'\g<delimSeconds>\g<Z>', input)
        return datetime.strptime(input, _ZULU).replace(tzinfo=timezone)

    @staticmethod
    def _parseLocalFormat(input, timezone):
        timezone = UTC if timezone is None else timezone
        return datetime.strptime(input, _LOCAL).replace(tzinfo=timezone)

    @staticmethod
    def _parseEpoch(seconds, timezone):
        if not float(seconds):
            raise TimeError("Format unknown")
        if timezone is None:
            raise TimeError("Time zone unknown, use timezone=")
        return datetime.fromtimestamp(seconds, timezone)

    @staticmethod
    def _parseRfc2822(input, timezone):
        result = email.parsedate_tz(input)
        if result is None:
            raise TimeError("Format unknown")
        year, month, day, hour, minutes, seconds, _, _, _, utcoffset = result
        if utcoffset is None:
            if timezone is None:
                raise TimeError("Time zone unknown, use timezone=")
        else:
            timezone = _OffsetOnlyTimeZone(utcoffset)
        return datetime(year, month, day, hour, minutes, seconds, 0, timezone).astimezone(UTC)

    @staticmethod
    def _parseIso8601BasicLocal(input, timezone):
        timezone = UTC if timezone is None else timezone
        pattern = []
        cumulative = 0
        for (sep, element, l) in _ISO8601_NO_TZ:
            cumulative += l
            pattern.append(element)
            if cumulative >= len(input):
                break
        input = input[:cumulative]
        return datetime.strptime(input, ''.join(pattern)).replace(tzinfo=timezone)

    @staticmethod
    def _parseJavaDefaultDateFormat(input, timezone=None):
        input = input.strip()
        for tzName, tz in _TimeZone.registered.iteritems():
            if tzName in input:
                if timezone is None:
                    timezone = tz
        if timezone is None:
            timezone = UTC
        return datetime.strptime(input, _JAVA_DEFAULT_DATE_FORMAT).replace(tzinfo=timezone)



_NO_TIME_DELTA = timedelta(0)

class _TimeZone(tzinfo):
    registered = {}
    def __init__(self, name, utcoffset, dst=None):
        self.name = name
        self._utcoffset = utcoffset
        self._dst = dst or _NO_TIME_DELTA
        _TimeZone.registered[name] = self
    def tzname(self, _):
        return self.name
    def utcoffset(self, t):
        return self._utcoffset + self.dst(t)
    def dst(self, _):
        return self._dst

UTC = _TimeZone("UTC", _NO_TIME_DELTA)
_CET = _TimeZone("CET", timedelta(hours=1))
_CEST = _TimeZone("CEST", timedelta(hours=1), dst=timedelta(hours=1))


class _OffsetOnlyTimeZone(tzinfo):
    def __init__(self, utcoffset_inseconds):
        self._utcoffset_inseconds = utcoffset_inseconds
    def utcoffset(self, _):
        return timedelta(seconds=self._utcoffset_inseconds)
    def dst(self, _):
        return _NO_TIME_DELTA


_LOCAL_DELTA = timedelta(seconds=-timezone)
_LOCAL_DST_DELTA = timedelta(seconds=-altzone) if daylight else _LOCAL_DELTA

class _LocalTimezone(tzinfo):
    def utcoffset(self, t):
        return _LOCAL_DST_DELTA if self._isdst(t) else _LOCAL_DELTA
    def dst(self, t):
        return _LOCAL_DST_DELTA - _LOCAL_DELTA if self._isdst(t) else _NO_TIME_DELTA
    def tzname(self, t):
        return tzname[self._isdst(t)]
    def _isdst(self, t):
        tt = (t.year, t.month, t.day, t.hour, t.minute, t.second, t.weekday(), 0, 0)
        stamp = mktime(tt)
        return localtime(stamp).tm_isdst > 0

Local = _LocalTimezone()

def _parseTimezone(dateString):
    result = _TIMEDELTA_RE.search(dateString)
    if result is None:
        return dateString, UTC
    hours = int(result.groupdict()['timedelta_hours'])
    minutes = int(result.groupdict()['timedelta_minutes'] or '0')
    sign = -1 if result.groupdict()['timedelta_sign'] == '-' else 1
    delta = timedelta(hours=sign*hours, minutes=sign*minutes)
    return dateString.replace(result.group(), '').strip(), \
        _TimeZone(name="{sign}{hours:02d}:{minutes:02d}".format(
                sign='+' if sign > 0 else '-',
                hours=hours,
                minutes=minutes),
            utcoffset=delta)


_ISO8601_NO_TZ = [('', '%Y', 4), ('-', '%m', 2,), ('-', '%d', 2), ('T', '%H', 2), (':', '%M', 2), (':', '%S', 2)]  # "%Y-%m-%dT%H:%M:%S"
_ISO8601 = "%Y-%m-%dT%H:%M:%S %Z"
_ZULU =  "%Y-%m-%dT%H:%M:%SZ"
_LOCAL =  "%Y-%m-%d %H:%M:%S"
_RFC2822 = "%a, %d %b %Y %H:%M:%S %z"
_RFC1123 = "%a, %d %b %Y %H:%M:%S GMT"
_JAVA_DEFAULT_DATE_FORMAT = "%a %b %d %H:%M:%S %Z %Y"


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
_TIMEDELTA_RE = re.compile(r'(?P<timedelta_sign>\+|\-)(?P<timedelta_hours>[0-9]{2})\:?(?P<timedelta_minutes>[0-9]{2})?$')

lookbehind = '(?<![0-9]{4}\-[0-9]{2})(?<![0-9]{4})'  # TODO: get rid of...

