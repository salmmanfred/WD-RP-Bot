import unittest
import asyncio


class CommandTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_loop = asyncio.get_event_loop()

    def test_sleep(self):
        return


if __name__ == '__main__':
    unittest.main()
