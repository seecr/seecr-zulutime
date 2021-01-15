## begin license ##
#
# Zulutime helps formatting and parsing timestamps.
#
# Copyright (C) 2012-2018, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
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
from random import shuffle

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
        self.assertEqual(1995, t.year)
        self.assertEqual(11, t.month)
        self.assertEqual(20, t.day)
        self.assertEqual(21, t.hour)
        self.assertEqual(12, t.minute)
        self.assertEqual( 8, t.second)
        self.assertEqual("UTC", t.timezone.tzname(None))
        self.assertEqual(0, t.timezone.utcoffset(t).days)
        self.assertEqual(0, t.timezone.dst(t).seconds)

    def testConvertTimeZoneToUTC(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 -0500")
        self.assertEqual(21, t.day) # Time zone wraps day
        self.assertEqual( 2, t.hour)
        self.assertEqual("UTC", t.timezone.tzname(None))
        self.assertEqual(0, t.timezone.utcoffset(t).days)
        self.assertEqual(0, t.timezone.dst(t).seconds)

    def testTimeZoneMustBePresent(self):
        # In python3 there is no distinction between no timezone or UTC :(
        #try:
        #    t = ZuluTime("Mon, 20 Nov 1995 21:12:08")
        #    self.fail()
        #except TimeError as e:
        #    self.assertEqual("Time zone unknown, use timezone=", str(e))

        t = ZuluTime("Mon, 20 Nov 1995 21:12:08", timezone=UTC)
        self.assertEqual(21, t.hour)
        self.assertEqual(20, t.day)

    def testConversionFromLocalTimeInWinter(self):
        # test only works in Central Europe ;-(
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08", timezone=Local)
        self.assertEqual(20, t.hour)
        self.assertEqual(20, t.day)
        self.assertEqual('CET', Local.tzname(t))
        self.assertEqual( 3600, Local.utcoffset(t).seconds)
        self.assertEqual(    0, Local.dst(t).seconds)
        self.assertEqual("UTC", t.timezone.tzname(None))
        self.assertEqual(    0, t.timezone.utcoffset(t).seconds)
        self.assertEqual(    0, t.timezone.dst(t).seconds)

    def testConversionFromLocalTimeInSummer(self):
        # test only works in Central Europe ;-(
        t = ZuluTime("Mon, 21 Jul 1996 21:12:08", timezone=Local)
        self.assertEqual(19, t.hour)
        self.assertEqual(21, t.day)
        self.assertEqual('CEST', Local.tzname(t))
        self.assertEqual(  7200, Local.utcoffset(t).seconds)
        self.assertEqual(  3600, Local.dst(t).seconds)
        self.assertEqual( "UTC", t.timezone.tzname(None))
        self.assertEqual(     0, t.timezone.utcoffset(t).seconds)
        self.assertEqual(     0, t.timezone.dst(t).seconds)

    def testConversionFromSecondsSinceEpoch(self):
        epoch = 1510240477.14 # seconds since epoch (1970, such as in Python time module)
        t_no_timezone = ZuluTime(epoch)
        t = ZuluTime(epoch, timezone=UTC)
        self.assertEqual(t_no_timezone, t)
        self.assertEqual(2017, t.year)
        self.assertEqual(  11, t.month)
        self.assertEqual(   9, t.day)
        self.assertEqual(  15, t.hour)
        self.assertEqual(  14, t.minute)
        self.assertEqual(  37, t.second)
        self.assertEqual("UTC", t.timezone.tzname(None))
        self.assertEqual(    0, t.timezone.utcoffset(t).days)

    def testGetCurrentTime(self):
        with popen('date --rfc-2822') as fp:
            os_date = fp.readline()
        t_ref = ZuluTime(os_date)
        t = ZuluTime()
        self.assertEqual(t_ref.year, t.year)
        self.assertEqual(t_ref.month, t.month)
        self.assertEqual(t_ref.day, t.day)
        self.assertEqual(t_ref.hour, t.hour)
        self.assertEqual(t_ref.minute, t.minute)
        self.assertEqual(t_ref.second, t.second)
        self.assertEqual(UTC, t.timezone)

    def testParseZulu(self):
        t = ZuluTime("2012-09-06T23:27:11Z")
        self.assertEqual(2012, t.year)
        self.assertEqual(   9, t.month)
        self.assertEqual(   6, t.day)
        self.assertEqual(  23, t.hour)
        self.assertEqual(  27, t.minute)
        self.assertEqual(  11, t.second)
        self.assertEqual("UTC", t.timezone.tzname(None))
        self.assertEqual(    0, t.timezone.utcoffset(t).days)
        self.assertEqual(    0, t.timezone.dst(t).seconds)

    def testParseIso8601WithoutTimeOrDay(self):
        a = ZuluTime("2012-09-06T23:27:11")
        self.assertEqual(ZuluTime("2012-09-06T23:27:11Z"), ZuluTime("2012-09-06T23:27:11"))
        self.assertEqual(ZuluTime("2012-09-06T00:00:00Z"), ZuluTime("2012-09-06"))
        self.assertEqual(ZuluTime("2012-09-01T00:00:00Z"), ZuluTime("2012-09"))
        self.assertEqual(ZuluTime("2012-01-01T00:00:00Z"), ZuluTime("2012"))

    def testParseIso8601Basic(self):
        self.assertEqual(ZuluTime("2012-09-06T23:27:11Z"), ZuluTime("20120906232711"))
        self.assertEqual(ZuluTime("2012-09-06T23:27:11Z"), ZuluTime("20120906232711000"))
        self.assertNotEqual(ZuluTime("2012-09-06T23:27:11Z"), ZuluTime("20120906"))
        self.assertEqual(ZuluTime("2012-09-06T00:00:00Z"), ZuluTime("20120906"))
        self.assertEqual(ZuluTime("2012-09-06T23:00:00Z"), ZuluTime("2012090623"))
        self.assertRaises(TimeError, lambda: ZuluTime("20120906Z"))

    def testIso8601ZuluTimeFractions(self):
        # Hack for not using a better iso8601 / Zulu time parser.
        self.assertEqual({'Z': 'Z', 'delimSeconds': ':11'}, _ZULU_FRACTION_REMOVAL_RE.search('2012-09-06T23:27:11.0123Z').groupdict())
        self.assertEqual({'Z': 'Z', 'delimSeconds': ':59'}, _ZULU_FRACTION_REMOVAL_RE.search(':59.00000000000000000001Z').groupdict())
        self.assertEqual({'Z': 'Z', 'delimSeconds': ':00'}, _ZULU_FRACTION_REMOVAL_RE.search(':00.0Z').groupdict())

        self.assertEqual(None, _ZULU_FRACTION_REMOVAL_RE.search('2012-09-06T23:27:11Z'))
        self.assertEqual(None, _ZULU_FRACTION_REMOVAL_RE.search(':11Z'))
        self.assertEqual(None, _ZULU_FRACTION_REMOVAL_RE.search(':11.Z'))
        self.assertEqual(None, _ZULU_FRACTION_REMOVAL_RE.search(':.0Z'))

        # Wrong, but we don't want to make a parser, strptime will fail for us.
        self.assertEqual({'Z': 'Z', 'delimSeconds': ':99'}, _ZULU_FRACTION_REMOVAL_RE.search(':99.0Z').groupdict())
        self.assertEqual({'Z': 'Z', 'delimSeconds': ':0'}, _ZULU_FRACTION_REMOVAL_RE.search(':0.0Z').groupdict())

    def testParseZuluWithFractionalSecondsParsesButFractionIsIgnored(self):
        # Hack for not using a better iso8601 / Zulu time parser.
        t = ZuluTime("2012-09-06T23:27:11.123456789Z")
        self.assertEqual(2012, t.year)
        self.assertEqual(   9, t.month)
        self.assertEqual(   6, t.day)
        self.assertEqual(  23, t.hour)
        self.assertEqual(  27, t.minute)
        self.assertEqual(  11, t.second)
        self.assertEqual("UTC", t.timezone.tzname(None))
        self.assertEqual(    0, t.timezone.utcoffset(t).days)
        self.assertEqual(    0, t.timezone.dst(t).seconds)

    def testParseIso8601CET(self):
        zt = ZuluTime("2011-01-13T16:59:59 CET")
        self.assertEqual('2011-01-13T16:59:59 CET', str(zt))
        self.assertEqual('2011-01-13T15:59:59 UTC', zt.iso8601())
        self.assertEqualsPointInTime(ZuluTime("2011-01-13T15:59:59Z"), zt)
        self.assertEqualsPointInTime(ZuluTime("2011-01-12T23:59:59Z"), ZuluTime("2011-01-13T00:59:59 CET"))

    def testParseIso8601CEST(self):
        zt = ZuluTime("2011-08-13T16:59:59 CEST")
        self.assertEqual('2011-08-13T16:59:59 CEST', str(zt))
        self.assertEqual('2011-08-13T14:59:59 UTC', zt.iso8601())
        self.assertEqualsPointInTime(ZuluTime("2011-08-13T14:59:59Z"), zt)
        self.assertEqualsPointInTime(ZuluTime("2011-08-12T22:59:59Z"), ZuluTime("2011-08-13T00:59:59 CEST"))

    def testParseIso8601WithSpecifiedTime(self):
        self.assertEqual('2020-12-21T00:42:24Z', ZuluTime("2020-12-21T01:42:24+01:00").zulu())
        self.assertEqual('2020-12-21T00:42:24Z', ZuluTime("2020-12-21T01:42:24.403578+01:00").zulu())

    def testParseJavaDefaultDateFormat(self):
        zt = ZuluTime('Thu Jan 13 00:59:59 CET 2011')
        self.assertEqual('2011-01-12T23:59:59 UTC', zt.iso8601())
        self.assertEqual("2011-01-13T00:59:59 CET", zt.iso8601(zt.timezone))

    def testRaiseExceptionOnUnknownFormat(self):
        try:
            ZuluTime("this is no valid time")
            self.fail()
        except TimeError as e:
            self.assertEqual("Format unknown", str(e))

    def testFormatIso8601(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 +0200")
        self.assertEqual("1995-11-20T19:12:08 UTC", t.iso8601())
        self.assertEqual("1995-11-20T19:12:08 UTC", ZuluTime("1995-11-20T19:12:08 UTC").iso8601())

    def testFormatIso8601WithTimezoneInHours(self):
        self.assertEqual({'timedelta_hours': '02', 'timedelta_minutes': '01', 'timedelta_sign': '+'}, _TIMEDELTA_RE.search("1995-11-20T19:12:08 +02:01").groupdict())
        self.assertEqual({'timedelta_hours': '03', 'timedelta_minutes': '05', 'timedelta_sign': '+'}, _TIMEDELTA_RE.search("1995-11-20T19:12:08 +0305").groupdict())
        self.assertEqual({'timedelta_hours': '03', 'timedelta_minutes': None, 'timedelta_sign': '+'}, _TIMEDELTA_RE.search("1995-11-20T19:12:08 +03").groupdict())
        self.assertEqual(None, _TIMEDELTA_RE.search("1995-11-20T19:12:08Z"))
        self.assertEqual({'timedelta_hours': '01', 'timedelta_minutes': '30', 'timedelta_sign': '-'}, _TIMEDELTA_RE.search("1995-11-20T19:12:08-01:30").groupdict())
        self.assertEqual("1995-11-20T19:12:08 UTC", ZuluTime("1995-11-20T19:12:08 +00:00").iso8601())
        self.assertEqual('2012-09-06T21:27:11Z', ZuluTime("2012-09-06T23:27:11+02:00").zulu())
        self.assertEqual('2012-09-06T21:27:11Z', ZuluTime("2012-09-06T23:27:11 +02").zulu())
        self.assertEqual('2012-09-07T01:27:11Z', ZuluTime("2012-09-06T23:27:11 -02").zulu())
        self.assertEqual('2012-09-07T01:00:11Z', ZuluTime("2012-09-06T23:27:11-0133").zulu())

    def testFormatZulu(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 +0200")
        self.assertEqual("1995-11-20T19:12:08Z", t.zulu())

    def testFormatRfc2822(self):
        t = ZuluTime("1995-11-20T19:12:08Z")
        self.assertEqual("Mon, 20 Nov 1995 19:12:08 +0000", t.rfc2822())

    def testFormatRfc1123(self):
        t = ZuluTime("1995-11-20T19:12:08Z")
        self.assertEqual("Mon, 20 Nov 1995 19:12:08 GMT", t.rfc1123())

    def testFormatWithTimeZone(self):
        t = ZuluTime("2007-06-11T15:30:00Z")
        self.assertEqual("Mon, 11 Jun 2007 17:30:00 +0200", t.rfc2822(timezone=Local))
        self.assertEqual("2007-06-11T17:30:00 CEST", t.iso8601(timezone=Local))

    def testDiplayString(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 +0200")
        self.assertEqual("19:12:08", t.display("%H:%M:%S"))

    def testFormatJavaDefaultDateFormat(self):
        t = ZuluTime("2007-06-11T15:30:00Z")
        self.assertEqual('Mon Jun 11 15:30:00 UTC 2007', t.javaDefaultFormat())
        self.assertEqual('Mon Jun 11 17:30:00 CEST 2007', t.javaDefaultFormat(_CEST))

    def testSubtractSeconds(self):
        t = ZuluTime('2013-11-22T15:00:00Z')
        self.assertEqual('2013-11-22T14:59:00Z', t.add(seconds=-60).zulu())
        self.assertEqual('2013-11-22T15:00:00Z', t.zulu())

    def testAddSubractYearMonthEtc(self):
        t = ZuluTime('2013-11-22T15:00:00Z')
        self.assertEqual('2013-12-22T15:00:00Z', t.add(months=+1).zulu())
        self.assertEqual('2014-01-22T15:00:00Z', t.add(months=+2).zulu())
        self.assertEqual('2015-06-22T15:00:00Z', t.add(years=+2, months=-5).zulu())
        self.assertEqual('2013-11-21T15:00:00Z', t.add(days=-1).zulu())
        t = ZuluTime('2013-01-30T15:00:00Z')
        self.assertEqual('2013-02-28T15:00:00Z', t.add(months=+1).zulu())
        self.assertEqual('2013-03-30T15:00:00Z', t.add(months=+2).zulu())

    def testLocal(self):
        t = ZuluTime('2013-11-22T15:00:00Z')
        self.assertEqual('2013-11-22 16:00:00', t.local())

    def testIso8601Basic(self):
        t = ZuluTime('2013-11-22T15:00:00Z')
        self.assertEqual('20131122150000', t.iso8601basic())

    def testLocalToZulu(self):
        t = ZuluTime('2014-09-03 12:30:00', timezone=Local)
        self.assertEqual('2014-09-03T10:30:00Z', t.zulu())
        t = ZuluTime('2014-12-03 12:30:00', timezone=Local)
        self.assertEqual('2014-12-03T11:30:00Z', t.zulu())
        t = ZuluTime.parseLocal('2014-09-03 12:30:00')
        self.assertEqual('2014-09-03T10:30:00Z', t.zulu())

    def testDefaultZuluForOtherFormats(self):
        t = ZuluTime('2014-09-03 12:30:00')
        self.assertEqual('2014-09-03T12:30:00Z', t.zulu())

    def testFormatInDutchWithoutTime(self):
        inDutch = lambda s: ZuluTime(s).formatDutch(time=False)
        self.assertEqual('30 juni 2014', inDutch('2014-06-30T12:00:00Z'))
        self.assertEqual('29 februari 2012', inDutch('2012-02-29T12:00:00Z'))
        self.assertEqual('1 maart 2012', inDutch('2012-02-29T23:30:00Z'))

    def testFormatInDutchWithTime(self):
        inDutch = lambda s: ZuluTime(s).formatDutch(time=True)
        self.assertEqual('30 juni 2014, 14:00 uur', inDutch('2014-06-30T12:00:00Z'))
        self.assertEqual('29 februari 2012, 13:00 uur', inDutch('2012-02-29T12:00:00Z'))
        self.assertEqual('1 maart 2012, 00:30 uur', inDutch('2012-02-29T23:30:00Z'))

    def testSecondsEpoch(self):
        inSeconds = lambda s: ZuluTime(s).epoch
        self.assertEqual(0,          inSeconds('1970-01-01T00:00:00Z'))
        self.assertEqual(1,          inSeconds('1970-01-01T00:00:01Z'))
        self.assertEqual(-31535999,  inSeconds('1969-01-01T00:00:01Z'))
        self.assertEqual(1426596781, inSeconds('2015-03-17T12:53:01Z'))

    def testFromSecondsEpoch(self):
        fromSeconds = lambda s: ZuluTime.parseEpoch(s).zulu()
        self.assertEqual('1970-01-01T00:00:00Z', fromSeconds(0))
        self.assertEqual('1970-01-01T00:00:00Z', fromSeconds(0.001))
        self.assertEqual('1970-01-01T00:00:01Z', fromSeconds(1))
        self.assertEqual('1969-01-01T00:00:01Z', fromSeconds(-31535999))
        self.assertEqual('2015-03-17T12:53:01Z', fromSeconds(1426596781))

    def testSorting(self):
        t4 = ZuluTime('2013-11-22T15:00:00Z')
        t2 = ZuluTime('2013-11-21T15:00:00Z')
        t5 = ZuluTime('2013-11-29T15:00:00Z')
        t1 = ZuluTime('2013-11-20T15:00:00Z')
        t3 = ZuluTime('2013-11-22T10:00:00Z')
        zuluTimes = [t1,t2,t3,t4,t5]
        shuffle(zuluTimes)
        self.assertNotEqual([t1,t2,t3,t4,t5], zuluTimes)
        self.assertEqual([t1,t2,t3,t4,t5], sorted(zuluTimes))

    def testAncient(self):
        x = ZuluTime('1658')
        self.assertEqual('1658-01-01T00:00:00Z', x.zulu())
        self.assertEqual('1658-01-01 01:00:00', x.local())
        self.assertEqual('1658-01-01T00:00:00 UTC', x.iso8601())
        self.assertEqual('16580101000000', x.iso8601basic())
        self.assertEqual(-9845712000, x.epoch)
        self.assertEqual('Tue, 01 Jan 1658 00:00:00 +0000', x.rfc2822())
        self.assertEqual("Tue, 01 Jan 1658 00:00:00 GMT", x.rfc1123())
        self.assertEqual("Tue Jan 01 00:00:00 UTC 1658", x.javaDefaultFormat())

    def assertEqualsPointInTime(self, a, b):
        self.assertTrue(a.equalsPointInTime(b), "%s !equalsPointInTime %s" % (a, b))
