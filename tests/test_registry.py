import unittest

from taskflow.registry import HandlerRegistry
from taskflow.handlers.system import SystemReportHandler


class TestHandlerRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = HandlerRegistry()

    def test_default_handler_is_registered(self):
        self.assertIn(
            "system_report",
            self.registry.available()
        )

    def test_get_returns_handler_instance(self):
        handler = self.registry.get("system_report")

        self.assertIsInstance(handler, SystemReportHandler)

    def test_register_custom_handler(self):
        class CustomHandler:
            pass

        self.registry.register("custom", CustomHandler)

        handler = self.registry.get("custom")

        self.assertIsInstance(handler, CustomHandler)

    def test_duplicate_registration_is_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.register(
                "system_report",
                SystemReportHandler
            )

    def test_empty_handler_name_is_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.register("", SystemReportHandler)

    def test_unknown_handler_is_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.get("does_not_exist")


if __name__ == "__main__":
    unittest.main()
