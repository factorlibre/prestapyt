import unittest
from unittest import mock
from xml.etree import ElementTree

from prestapyt import PrestaShopWebServiceDict, PrestaShopWebServiceError

PRODUCT = b"<prestashop><product><id>1</id><weight>2.5</weight></product></prestashop>"
ERROR = (
    b"<prestashop><errors><error><code>85</code>"
    b"<message>Validation error</message></error></errors></prestashop>"
)


def response(status=200, content=PRODUCT):
    return mock.Mock(status_code=status, content=content, headers={})


class TestPatch(unittest.TestCase):
    def setUp(self):
        self.ws = PrestaShopWebServiceDict("https://shop.test", "KEY")
        self.request = mock.patch.object(self.ws.client, "request").start()
        self.addCleanup(mock.patch.stopall)

    def test_patch_sends_only_given_fields(self):
        self.request.return_value = response()
        res = self.ws.patch("products", 1, {"product": {"id": 1, "weight": 2.5}})
        method, url = self.request.call_args.args
        self.assertEqual((method, url), ("PATCH", "https://shop.test/api/products/1"))
        sent = ElementTree.fromstring(self.request.call_args.kwargs["data"])
        self.assertEqual(
            {child.tag: child.text for child in sent.find("product")},
            {"id": "1", "weight": "2.5"},
        )
        self.assertEqual(res["prestashop"]["product"]["weight"], "2.5")

    def test_patch_error_raised(self):
        self.request.return_value = response(status=400, content=ERROR)
        with self.assertRaises(PrestaShopWebServiceError) as caught:
            self.ws.patch("products", 1, {"product": {"id": 1}})
        self.assertEqual(caught.exception.error_code, 400)


if __name__ == "__main__":
    unittest.main()
