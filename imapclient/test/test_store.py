# Copyright (c) 2016, Menno Smits
# Released subject to the New BSD License
# Please see http://en.wikipedia.org/wiki/BSD_licenses

from __future__ import unicode_literals

import six
from mock import patch, sentinel, Mock

from imapclient import DELETED, SEEN, ANSWERED, FLAGGED, DRAFT, RECENT
from .imapclient_test import IMAPClientTest


class TestFlagsConsts(IMAPClientTest):

    def test_flags_are_bytes(self):
        for flag in DELETED, SEEN, ANSWERED, FLAGGED, DRAFT, RECENT:
            if not isinstance(flag, six.binary_type):
                self.fail("%r flag is not bytes" % flag)


class TestGmailLabels(IMAPClientTest):

    def setUp(self):
        super(TestGmailLabels, self).setUp()
        self.client._command_and_check = Mock()

    def test_get(self):
        with patch.object(self.client, 'fetch', autospec=True,
                          return_value={123: {b'X-GM-LABELS': [b'foo', b'bar']},
                                        444: {b'X-GM-LABELS': [b'foo']}}):
            out = self.client.get_gmail_labels(sentinel.messages)
            self.client.fetch.assert_called_with(sentinel.messages, [b'X-GM-LABELS'])
            self.assertEqual(out, {123: [b'foo', b'bar'],
                                   444: [b'foo']})

    def test_set(self):
        self.check(self.client.set_gmail_labels, b'X-GM-LABELS')

    def test_add(self):
        self.check(self.client.add_gmail_labels, b'+X-GM-LABELS')

    def test_remove(self):
        self.check(self.client.remove_gmail_labels, b'-X-GM-LABELS')

    def check(self, meth, expected_store_command):
        cc = self.client._command_and_check
        cc.return_value = [
            '11 (X-GM-LABELS (blah "f\\"o\\"o") UID 1)',
            '22 (X-GM-LABELS ("f\\"o\\"o") UID 2)',
            '11 (UID 1 FLAGS (dont))',
            '22 (UID 2 FLAGS (care))',
        ]
        resp = meth([1, 2], 'f"o"o')
        cc.assert_called_once_with(
            'store', b"1,2",
            expected_store_command,
            '("f\\"o\\"o")',
            uid=True)
        self.assertEqual(resp, {
            1: (b'blah', b'f"o"o'),
            2: (b'f"o"o',),
        })