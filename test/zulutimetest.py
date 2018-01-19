## begin license ##
#
# Zulutime helps formatting and parsing timestamps.
#
# Copyright (C) 2012-2018 Seecr (Seek You Too B.V.) http://seecr.nl
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

from unittest import TestCase
from os import popen

from seecr.zulutime import ZuluTime, TimeError, UTC, Local
from seecr.zulutime._zulutime import _ZULU_FRACTION_REMOVAL_RE, _CEST, _TIMEDELTA_RE


# TODO:
#   - Use python-aniso8601 for _parseZulutimeFormat (maybe formats too);
#     since it supports:
#       * Fractions of seconds (example: 2012-09-06T23:27:11.123456789Z )
#                                                           ^^^^^^^^^^
#       * Can return the granularity/precision of the parsed datetime / date / time format.
#         Handy for when you want to output a datetime format in the same precision as some input.


class ZuluTimeTest(TestCase):
    def testParseRfc2822(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 0000")
        self.assertEquals(1995, t.year)
        self.assertEquals(11, t.month)
        self.assertEquals(20, t.day)
        self.assertEquals(21, t.hour)
        self.assertEquals(12, t.minute)
        self.assertEquals( 8, t.second)
        self.assertEquals("UTC", t.timezone.tzname(None))
        self.assertEquals(0, t.timezone.utcoffset(t).days)
        self.assertEquals(0, t.timezone.dst(t).seconds)

    def testConvertTimeZoneToUTC(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 -0500")
        self.assertEquals(21, t.day) # Time zone wraps day
        self.assertEquals( 2, t.hour)
        self.assertEquals("UTC", t.timezone.tzname(None))
        self.assertEquals(0, t.timezone.utcoffset(t).days)
        self.assertEquals(0, t.timezone.dst(t).seconds)

    def testTimeZoneMustBePresent(self):
        try:
            t = ZuluTime("Mon, 20 Nov 1995 21:12:08")
            self.fail()
        except TimeError, e:
            self.assertEquals("Time zone unknown, use timezone=", str(e))

        t = ZuluTime("Mon, 20 Nov 1995 21:12:08", timezone=UTC)
        self.assertEquals(21, t.hour)
        self.assertEquals(20, t.day)

    def testConversionFromLocalTimeInWinter(self):
        # test only works in Central Europe ;-(
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08", timezone=Local)
        self.assertEquals(20, t.hour)
        self.assertEquals(20, t.day)
        self.assertEquals('CET', Local.tzname(t))
        self.assertEquals( 3600, Local.utcoffset(t).seconds)
        self.assertEquals(    0, Local.dst(t).seconds)
        self.assertEquals("UTC", t.timezone.tzname(None))
        self.assertEquals(    0, t.timezone.utcoffset(t).seconds)
        self.assertEquals(    0, t.timezone.dst(t).seconds)

    def testConversionFromLocalTimeInSummer(self):
        # test only works in Central Europe ;-(
        t = ZuluTime("Mon, 21 Jul 1996 21:12:08", timezone=Local)
        self.assertEquals(19, t.hour)
        self.assertEquals(21, t.day)
        self.assertEquals('CEST', Local.tzname(t))
        self.assertEquals(  7200, Local.utcoffset(t).seconds)
        self.assertEquals(  3600, Local.dst(t).seconds)
        self.assertEquals( "UTC", t.timezone.tzname(None))
        self.assertEquals(     0, t.timezone.utcoffset(t).seconds)
        self.assertEquals(     0, t.timezone.dst(t).seconds)

    def testConversionFromSecondsSinceEpoch(self):
        epoch = 1510240477.14 # seconds since epoch (1970, such as in Python time module)
        t_no_timezone = ZuluTime(epoch)
        t = ZuluTime(epoch, timezone=UTC)
        self.assertEquals(t_no_timezone, t)
        self.assertEquals(2017, t.year)
        self.assertEquals(  11, t.month)
        self.assertEquals(   9, t.day)
        self.assertEquals(  15, t.hour)
        self.assertEquals(  14, t.minute)
        self.assertEquals(  37, t.second)
        self.assertEquals("UTC", t.timezone.tzname(None))
        self.assertEquals(    0, t.timezone.utcoffset(t).days)

    def testGetCurrentTime(self):
        os_date = popen('date --rfc-2822').readline()
        t_ref = ZuluTime(os_date)
        t = ZuluTime()
        self.assertEquals(t_ref.year, t.year)
        self.assertEquals(t_ref.month, t.month)
        self.assertEquals(t_ref.day, t.day)
        self.assertEquals(t_ref.hour, t.hour)
        self.assertEquals(t_ref.minute, t.minute)
        self.assertEquals(t_ref.second, t.second)
        self.assertEquals(UTC, t.timezone)

    def testParseZulu(self):
        t = ZuluTime("2012-09-06T23:27:11Z")
        self.assertEquals(2012, t.year)
        self.assertEquals(   9, t.month)
        self.assertEquals(   6, t.day)
        self.assertEquals(  23, t.hour)
        self.assertEquals(  27, t.minute)
        self.assertEquals(  11, t.second)
        self.assertEquals("UTC", t.timezone.tzname(None))
        self.assertEquals(    0, t.timezone.utcoffset(t).days)
        self.assertEquals(    0, t.timezone.dst(t).seconds)

    def testParseIso8601WithoutTimeOrDay(self):
        a = ZuluTime("2012-09-06T23:27:11")
        self.assertEquals(ZuluTime("2012-09-06T23:27:11Z"), ZuluTime("2012-09-06T23:27:11"))
        self.assertEquals(ZuluTime("2012-09-06T00:00:00Z"), ZuluTime("2012-09-06"))
        self.assertEquals(ZuluTime("2012-09-01T00:00:00Z"), ZuluTime("2012-09"))
        self.assertEquals(ZuluTime("2012-01-01T00:00:00Z"), ZuluTime("2012"))

    def testParseIso8601Basic(self):
        self.assertEquals(ZuluTime("2012-09-06T23:27:11Z"), ZuluTime("20120906232711"))
        self.assertEquals(ZuluTime("2012-09-06T23:27:11Z"), ZuluTime("20120906232711000"))
        self.assertNotEquals(ZuluTime("2012-09-06T23:27:11Z"), ZuluTime("20120906"))
        self.assertEquals(ZuluTime("2012-09-06T00:00:00Z"), ZuluTime("20120906"))
        self.assertEquals(ZuluTime("2012-09-06T23:00:00Z"), ZuluTime("2012090623"))
        self.assertRaises(TimeError, lambda: ZuluTime("20120906Z"))

    def testIso8601ZuluTimeFractions(self):
        # Hack for not using a better iso8601 / Zulu time parser.
        self.assertEquals({'Z': 'Z', 'delimSeconds': ':11'}, _ZULU_FRACTION_REMOVAL_RE.search('2012-09-06T23:27:11.0123Z').groupdict())
        self.assertEquals({'Z': 'Z', 'delimSeconds': ':59'}, _ZULU_FRACTION_REMOVAL_RE.search(':59.00000000000000000001Z').groupdict())
        self.assertEquals({'Z': 'Z', 'delimSeconds': ':00'}, _ZULU_FRACTION_REMOVAL_RE.search(':00.0Z').groupdict())

        self.assertEquals(None, _ZULU_FRACTION_REMOVAL_RE.search('2012-09-06T23:27:11Z'))
        self.assertEquals(None, _ZULU_FRACTION_REMOVAL_RE.search(':11Z'))
        self.assertEquals(None, _ZULU_FRACTION_REMOVAL_RE.search(':11.Z'))
        self.assertEquals(None, _ZULU_FRACTION_REMOVAL_RE.search(':.0Z'))

        # Wrong, but we don't want to make a parser, strptime will fail for us.
        self.assertEquals({'Z': 'Z', 'delimSeconds': ':99'}, _ZULU_FRACTION_REMOVAL_RE.search(':99.0Z').groupdict())
        self.assertEquals({'Z': 'Z', 'delimSeconds': ':0'}, _ZULU_FRACTION_REMOVAL_RE.search(':0.0Z').groupdict())

    def testParseZuluWithFractionalSecondsParsesButFractionIsIgnored(self):
        # Hack for not using a better iso8601 / Zulu time parser.
        t = ZuluTime("2012-09-06T23:27:11.123456789Z")
        self.assertEquals(2012, t.year)
        self.assertEquals(   9, t.month)
        self.assertEquals(   6, t.day)
        self.assertEquals(  23, t.hour)
        self.assertEquals(  27, t.minute)
        self.assertEquals(  11, t.second)
        self.assertEquals("UTC", t.timezone.tzname(None))
        self.assertEquals(    0, t.timezone.utcoffset(t).days)
        self.assertEquals(    0, t.timezone.dst(t).seconds)

    def testParseIso8601CET(self):
        zt = ZuluTime("2011-01-13T16:59:59 CET")
        self.assertEquals('2011-01-13T16:59:59 CET', str(zt))
        self.assertEquals('2011-01-13T15:59:59 UTC', zt.iso8601())
        self.assertEqualsPointInTime(ZuluTime("2011-01-13T15:59:59Z"), zt)
        self.assertEqualsPointInTime(ZuluTime("2011-01-12T23:59:59Z"), ZuluTime("2011-01-13T00:59:59 CET"))

    def testParseIso8601CEST(self):
        zt = ZuluTime("2011-08-13T16:59:59 CEST")
        self.assertEquals('2011-08-13T16:59:59 CEST', str(zt))
        self.assertEquals('2011-08-13T14:59:59 UTC', zt.iso8601())
        self.assertEqualsPointInTime(ZuluTime("2011-08-13T14:59:59Z"), zt)
        self.assertEqualsPointInTime(ZuluTime("2011-08-12T22:59:59Z"), ZuluTime("2011-08-13T00:59:59 CEST"))

    def testParseJavaDefaultDateFormat(self):
        zt = ZuluTime('Thu Jan 13 00:59:59 CET 2011')
        self.assertEquals('2011-01-12T23:59:59 UTC', zt.iso8601())
        self.assertEquals("2011-01-13T00:59:59 CET", zt.iso8601(zt.timezone))

    def testRaiseExceptionOnUnknownFormat(self):
        try:
            ZuluTime("this is no valid time")
            self.fail()
        except TimeError, e:
            self.assertEquals("Format unknown", str(e))

    def testFormatIso8601(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 +0200")
        self.assertEquals("1995-11-20T19:12:08 UTC", t.iso8601())
        self.assertEquals("1995-11-20T19:12:08 UTC", ZuluTime("1995-11-20T19:12:08 UTC").iso8601())

    def testFormatIso8601WithTimezoneInHours(self):
        self.assertEquals({'timedelta_hours': '02', 'timedelta_minutes': '01', 'timedelta_sign': '+'}, _TIMEDELTA_RE.search("1995-11-20T19:12:08 +02:01").groupdict())
        self.assertEquals({'timedelta_hours': '03', 'timedelta_minutes': '05', 'timedelta_sign': '+'}, _TIMEDELTA_RE.search("1995-11-20T19:12:08 +0305").groupdict())
        self.assertEquals({'timedelta_hours': '03', 'timedelta_minutes': None, 'timedelta_sign': '+'}, _TIMEDELTA_RE.search("1995-11-20T19:12:08 +03").groupdict())
        self.assertEquals(None, _TIMEDELTA_RE.search("1995-11-20T19:12:08Z"))
        self.assertEquals({'timedelta_hours': '01', 'timedelta_minutes': '30', 'timedelta_sign': '-'}, _TIMEDELTA_RE.search("1995-11-20T19:12:08-01:30").groupdict())
        self.assertEquals("1995-11-20T19:12:08 UTC", ZuluTime("1995-11-20T19:12:08 +00:00").iso8601())
        self.assertEquals('2012-09-06T21:27:11Z', ZuluTime("2012-09-06T23:27:11+02:00").zulu())
        self.assertEquals('2012-09-06T21:27:11Z', ZuluTime("2012-09-06T23:27:11 +02").zulu())
        self.assertEquals('2012-09-07T01:27:11Z', ZuluTime("2012-09-06T23:27:11 -02").zulu())
        self.assertEquals('2012-09-07T01:00:11Z', ZuluTime("2012-09-06T23:27:11-0133").zulu())

    def testFormatZulu(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 +0200")
        self.assertEquals("1995-11-20T19:12:08Z", t.zulu())

    def testFormatRfc2822(self):
        t = ZuluTime("1995-11-20T19:12:08Z")
        self.assertEquals("Mon, 20 Nov 1995 19:12:08 +0000", t.rfc2822())

    def testFormatRfc1123(self):
        t = ZuluTime("1995-11-20T19:12:08Z")
        self.assertEquals("Mon, 20 Nov 1995 19:12:08 GMT", t.rfc1123())

    def testFormatWithTimeZone(self):
        t = ZuluTime("2007-06-11T15:30:00Z")
        self.assertEquals("Mon, 11 Jun 2007 17:30:00 +0200", t.rfc2822(timezone=Local))
        self.assertEquals("2007-06-11T17:30:00 CEST", t.iso8601(timezone=Local))

    def testDiplayString(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 +0200")
        self.assertEquals("19:12:08", t.display("%H:%M:%S"))

    def testFormatJavaDefaultDateFormat(self):
        t = ZuluTime("2007-06-11T15:30:00Z")
        self.assertEquals('Mon Jun 11 15:30:00 UTC 2007', t.javaDefaultFormat())
        self.assertEquals('Mon Jun 11 17:30:00 CEST 2007', t.javaDefaultFormat(_CEST))

    def testSubtractSeconds(self):
        t = ZuluTime('2013-11-22T15:00:00Z')
        self.assertEquals('2013-11-22T14:59:00Z', t.add(seconds=-60).zulu())
        self.assertEquals('2013-11-22T15:00:00Z', t.zulu())

    def testLocal(self):
        t = ZuluTime('2013-11-22T15:00:00Z')
        self.assertEquals('2013-11-22 16:00:00', t.local())

    def testIso8601Basic(self):
        t = ZuluTime('2013-11-22T15:00:00Z')
        self.assertEquals('20131122150000', t.iso8601basic())

    def testLocalToZulu(self):
        t = ZuluTime('2014-09-03 12:30:00', timezone=Local)
        self.assertEquals('2014-09-03T10:30:00Z', t.zulu())
        t = ZuluTime('2014-12-03 12:30:00', timezone=Local)
        self.assertEquals('2014-12-03T11:30:00Z', t.zulu())
        t = ZuluTime.parseLocal('2014-09-03 12:30:00')
        self.assertEquals('2014-09-03T10:30:00Z', t.zulu())

    def testDefaultZuluForOtherFormats(self):
        t = ZuluTime('2014-09-03 12:30:00')
        self.assertEquals('2014-09-03T12:30:00Z', t.zulu())

    def testFormatInDutchWithoutTime(self):
        inDutch = lambda s: ZuluTime(s).formatDutch(time=False)
        self.assertEquals('30 juni 2014', inDutch('2014-06-30T12:00:00Z'))
        self.assertEquals('29 februari 2012', inDutch('2012-02-29T12:00:00Z'))
        self.assertEquals('1 maart 2012', inDutch('2012-02-29T23:30:00Z'))

    def testFormatInDutchWithTime(self):
        inDutch = lambda s: ZuluTime(s).formatDutch(time=True)
        self.assertEquals('30 juni 2014, 14:00 uur', inDutch('2014-06-30T12:00:00Z'))
        self.assertEquals('29 februari 2012, 13:00 uur', inDutch('2012-02-29T12:00:00Z'))
        self.assertEquals('1 maart 2012, 00:30 uur', inDutch('2012-02-29T23:30:00Z'))

    def testSecondsEpoch(self):
        inSeconds = lambda s: ZuluTime(s).epoch
        self.assertEquals(0,          inSeconds('1970-01-01T00:00:00Z'))
        self.assertEquals(1,          inSeconds('1970-01-01T00:00:01Z'))
        self.assertEquals(-31535999,  inSeconds('1969-01-01T00:00:01Z'))
        self.assertEquals(1426596781, inSeconds('2015-03-17T12:53:01Z'))

    def testFromSecondsEpoch(self):
        fromSeconds = lambda s: ZuluTime.parseEpoch(s).zulu()
        self.assertEquals('1970-01-01T00:00:00Z', fromSeconds(0))
        self.assertEquals('1970-01-01T00:00:00Z', fromSeconds(0.001))
        self.assertEquals('1970-01-01T00:00:01Z', fromSeconds(1))
        self.assertEquals('1969-01-01T00:00:01Z', fromSeconds(-31535999))
        self.assertEquals('2015-03-17T12:53:01Z', fromSeconds(1426596781))

    def assertEqualsPointInTime(self, a, b):
        self.assertTrue(a.equalsPointInTime(b), "%s !equalsPointInTime %s" % (a, b))
