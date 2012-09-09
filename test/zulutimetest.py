from unittest import TestCase
from os import popen

from seecr.zulutime import ZuluTime, TimeError, UTC, Local, ISO8601, RFC2822, ZULU

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
            self.assertEquals("Time zone unknown, use tz=", str(e))

        t = ZuluTime("Mon, 20 Nov 1995 21:12:08", tz=UTC)
        self.assertEquals(21, t.hour)
        self.assertEquals(20, t.day)

    def testConversionFromLocalTimeInWinter(self):
        # test only works in Central Europe ;-(
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08", tz=Local)
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
        t = ZuluTime("Mon, 21 Jul 1996 21:12:08", tz=Local)
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
            t = ZuluTime("this is no valid time")
            self.fail()
        except TimeError, e:
            self.assertEquals("Format unknown", str(e))

    def testFormatIso8601(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 +0200")
        f = t.iso8601()
        self.assertEquals("1995-11-20T19:12:08 UTC", f)

    def testFormatZulu(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 +0200")
        f = t.format(ZULU)
        self.assertEquals("1995-11-20T19:12:08Z", f)

    def testFormatRfc2822(self):
        t = ZuluTime("1995-11-20T19:12:08Z")
        f = t.format(RFC2822)
        self.assertEquals("Mon, 20 Nov 1995 19:12:08 +0000", f)

    def testFormatWithTimeZone(self):
        t = ZuluTime("2007-06-11T15:30:00Z")
        f = t.format(RFC2822, timezone=Local)
        self.assertEquals("Mon, 11 Jun 2007 17:30:00 +0200", f)
        f = t.format(ISO8601, timezone=Local)
        self.assertEquals("2007-06-11T17:30:00 CEST", f)

    def testUnsafeFormatsRaiseException(self):
        t = ZuluTime("2007-06-11T15:30:00Z")
        try:
            f = t.format("%H:%M:%S", timezone=Local)
            self.fail()
        except TimeError, e:
            self.assertEquals("Format does not include timezone.", str(e))
        self.assertRaises(TimeError, lambda:  t.format(ZULU, timezone=Local))

    def testDiplayString(self):
        t = ZuluTime("Mon, 20 Nov 1995 21:12:08 +0200")
        s = t.display("%H:%M:%S")
        self.assertEquals("19:12:08", s)
