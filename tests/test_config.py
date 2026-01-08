import unittest
from unittest import mock

from core.config import HostSetting


class TestHostSetting(unittest.TestCase):
    def test_iteration_bits_out_of_range_raises(self) -> None:
        with self.assertRaises(ValueError):
            HostSetting(kernel_source="kernel", iteration_bits=-1)
        with self.assertRaises(ValueError):
            HostSetting(kernel_source="kernel", iteration_bits=256)

    def test_iteration_bytes_rounds_up(self) -> None:
        self.assertEqual(
            HostSetting(kernel_source="kernel", iteration_bits=1).iteration_bytes, 1
        )
        self.assertEqual(
            HostSetting(kernel_source="kernel", iteration_bits=9).iteration_bytes, 2
        )

    def test_generate_key32_appends_zero_padding(self) -> None:
        with mock.patch("core.config.secrets.token_bytes", return_value=b"\xAB" * 31):
            setting = HostSetting(kernel_source="kernel", iteration_bits=8)

        self.assertEqual(setting.iteration_bytes, 1)
        self.assertEqual(len(setting.key32), 32)
        self.assertEqual(setting.key32[-1], 0)
        self.assertTrue(all(b == 0xAB for b in setting.key32[:-1]))

    def test_increase_key32_advances_by_iteration_bits(self) -> None:
        setting = HostSetting(kernel_source="kernel", iteration_bits=8)
        setting.key32 = bytearray(32)

        setting.increase_key32()

        expected = (1 << setting.iteration_bits).to_bytes(32, "big")
        self.assertEqual(setting.key32, bytearray(expected))

    def test_increase_key32_handles_zero_iteration_bytes(self) -> None:
        setting = HostSetting(kernel_source="kernel", iteration_bits=0)
        setting.key32 = bytearray(32)

        setting.increase_key32()

        expected = (1 << setting.iteration_bits).to_bytes(32, "big")
        self.assertEqual(setting.key32, bytearray(expected))


if __name__ == "__main__":
    unittest.main()
