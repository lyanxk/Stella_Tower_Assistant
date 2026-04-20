from __future__ import annotations

import unittest

from stellatowerassistant.core.runtime.events import EventStore


class EventStoreTestCase(unittest.TestCase):
    def test_emit_adds_recent_event(self) -> None:
        store = EventStore(limit=5)
        store.emit("hello", scope="test")
        recent = store.recent(1)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].message, "hello")
        self.assertEqual(recent[0].scope, "test")


if __name__ == "__main__":
    unittest.main()
