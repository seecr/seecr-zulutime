from time import mktime, localtime, tzname, timezone, altzone, daylight
from datetime import datetime, tzinfo, timedelta
from email import utils as email

class TimeError(Exception): pass

NO_TIME_DELTA = timedelta(0)
LOCAL_DELTA = timedelta(seconds=-timezone)
DST_DELTA = timedelta(seconds=-altzone) if daylight else LOCAL_DELTA

class UtcTimeZone(tzinfo):
    def tzname(self, _): return "UTC"
    def utcoffset(self, _): return NO_TIME_DELTA
    def dst(self, _): return NO_TIME_DELTA

UTC = UtcTimeZone()

class LocalTimezone(tzinfo):
    def utcoffset(self, t):
        return DST_DELTA if self._isdst(t) else LOCAL_DELTA
    def dst(self, t):
        return DST_DELTA - LOCAL_DELTA if self._isdst(t) else NO_TIME_DELTA
    def tzname(self, t):
        return tzname[self._isdst(t)]
    def _isdst(self, t):
        tt = (t.year, t.month, t.day, t.hour, t.minute, t.second, t.weekday(), 0, 0)
        stamp = mktime(tt)
        return localtime(stamp).tm_isdst > 0

Local = LocalTimezone()

class TzHelper(tzinfo):
    def __init__(self, utcoffset_inseconds):
        self._utcoffset_inseconds = utcoffset_inseconds
    def utcoffset(self, dt):
        return timedelta(seconds=self._utcoffset_inseconds)

class ZuluTime(object):
    """Maintains datetime objects with UTC and proper conversion according to systems locale."""

    def __init__(self, input=None, tz=None):
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
                if tz is None:
                    raise TimeError("Time zone unknown, use tz=")
            else:
                tz = TzHelper(utcoffset)
            self._ = datetime(year, month, day, hour, minutes, seconds, 0, tz).astimezone(UTC)

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

    def display(self, f):
        return self._.strftime(f)

    def iso8601(self, timzone=UTC):
        return self._.astimezone(timezone)

    def format(self, f, timezone=UTC):
        if timezone is not UTC and "%Z" not in f and "%z" not in f:
            raise TimeError("Format does not include timezone.")

        return self._.astimezone(timezone).strftime(f)

RFC2822 = "%a, %d %b %Y %H:%M:%S %z"
ISO8601 = "%Y-%m-%dT%H:%M:%S %Z"
ZULU =  "%Y-%m-%dT%H:%M:%SZ"
