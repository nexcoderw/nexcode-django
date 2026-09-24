"""Recognising who sent a contact message."""

from django.test import RequestFactory, SimpleTestCase

from home.contact_sender import client_ip, describe_device, sender_details
from home.models import Contact


IPHONE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
IPAD = (
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
ANDROID_PHONE = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
)
ANDROID_TABLET = (
    "Mozilla/5.0 (Linux; Android 14; SM-X710) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
WINDOWS_EDGE = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
)
MAC_FIREFOX = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:127.0) Gecko/20100101 "
    "Firefox/127.0"
)
GOOGLEBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"


class DescribeDeviceTests(SimpleTestCase):
    def test_devices_are_recognised(self):
        cases = (
            (IPHONE, Contact.DeviceType.MOBILE, "Safari", "iOS"),
            (IPAD, Contact.DeviceType.TABLET, "Safari", "iPadOS"),
            (ANDROID_PHONE, Contact.DeviceType.MOBILE, "Chrome", "Android"),
            (ANDROID_TABLET, Contact.DeviceType.TABLET, "Chrome", "Android"),
            (WINDOWS_EDGE, Contact.DeviceType.DESKTOP, "Edge", "Windows"),
            (MAC_FIREFOX, Contact.DeviceType.DESKTOP, "Firefox", "macOS"),
        )

        for user_agent, device_type, browser, operating_system in cases:
            with self.subTest(browser=browser, os=operating_system):
                self.assertEqual(
                    describe_device(user_agent),
                    (device_type, browser, operating_system),
                )

    def test_crawlers_are_marked_as_bots(self):
        self.assertEqual(describe_device(GOOGLEBOT)[0], Contact.DeviceType.BOT)

    def test_missing_user_agent_is_unknown(self):
        self.assertEqual(
            describe_device(""),
            (Contact.DeviceType.UNKNOWN, "", ""),
        )


class ClientIpTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_proxy_address_is_preferred(self):
        request = self.factory.get(
            "/", HTTP_X_REAL_IP="203.0.113.9", REMOTE_ADDR="127.0.0.1"
        )

        self.assertEqual(client_ip(request), "203.0.113.9")

    def test_remote_address_is_used_without_a_proxy(self):
        request = self.factory.get("/", REMOTE_ADDR="198.51.100.4")

        self.assertEqual(client_ip(request), "198.51.100.4")

    def test_ipv6_addresses_are_kept(self):
        request = self.factory.get("/", HTTP_X_REAL_IP="2001:db8::1")

        self.assertEqual(client_ip(request), "2001:db8::1")

    def test_invalid_header_falls_back_to_remote_address(self):
        request = self.factory.get(
            "/", HTTP_X_REAL_IP="not-an-ip", REMOTE_ADDR="198.51.100.4"
        )

        self.assertEqual(client_ip(request), "198.51.100.4")

    def test_forwarded_for_is_not_trusted(self):
        # X-Forwarded-For can be set by the visitor; only nginx's
        # X-Real-IP (or the socket address) identifies the sender.
        request = self.factory.get(
            "/", HTTP_X_FORWARDED_FOR="1.2.3.4", REMOTE_ADDR="198.51.100.4"
        )

        self.assertEqual(client_ip(request), "198.51.100.4")

    def test_long_user_agents_are_truncated(self):
        request = self.factory.get("/", HTTP_USER_AGENT="x" * 2000)

        self.assertEqual(len(sender_details(request)["user_agent"]), 512)
