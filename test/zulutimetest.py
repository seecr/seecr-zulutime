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

from unittest import TestCase
from os import popen

from seecr.zulutime import ZuluTime, TimeError, UTC, Local

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

    def testRaiseExceptionOnUnknownFormat(self):
        try:
            ZuluTime("this is no valid time")
            self.fail()
        except TimeError, e:
            self.assertEquals("Format unknown", str(e))

    def testFormatIso8601(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 +0200")
        self.assertEquals("1995-11-20T19:12:08 UTC", t.iso8601())

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

    def testSubtractSeconds(self):
        t = ZuluTime('2013-11-22T15:00:00Z')
        self.assertEquals('2013-11-22T14:59:00Z', t.add(seconds=-60).zulu())
        self.assertEquals('2013-11-22T15:00:00Z', t.zulu())

    def testLocal(self):
        t = ZuluTime('2013-11-22T15:00:00Z')
        self.assertEquals('2013-11-22 16:00:00', t.local())

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
        self.assertEquals(1, inSeconds('1970-01-01T00:00:01Z'))
        self.assertEquals(-31535999, inSeconds('1969-01-01T00:00:01Z'))
        self.assertEquals(1426596781, inSeconds('2015-03-17T12:53:01Z'))
