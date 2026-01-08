import json
import tempfile
import unittest
from pathlib import Path

from base58 import b58encode
from nacl.signing import SigningKey

from core.utils.crypto import get_public_key_from_private_bytes, save_keypair


class TestCrypto(unittest.TestCase):
    def test_get_public_key_from_private_bytes(self) -> None:
        pv_bytes = bytes(range(1, 33))
        expected_pubkey = b58encode(bytes(SigningKey(pv_bytes).verify_key)).decode()

        self.assertEqual(get_public_key_from_private_bytes(pv_bytes), expected_pubkey)

    def test_save_keypair_writes_json(self) -> None:
        pv_bytes = bytes([7] * 32)

        with tempfile.TemporaryDirectory() as tmpdir:
            pubkey = save_keypair(pv_bytes, tmpdir)
            path = Path(tmpdir) / f"{pubkey}.json"

            self.assertTrue(path.exists())
            payload = json.loads(path.read_text())
            self.assertEqual(payload[:32], list(pv_bytes))
            self.assertEqual(len(payload), 64)


if __name__ == "__main__":
    unittest.main()
