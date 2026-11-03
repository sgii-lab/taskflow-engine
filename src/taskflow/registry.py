from taskflow.handlers.system import SystemReportHandler


class HandlerRegistry:
    """
    Maintains available task handlers.
    """

    def __init__(self):
        self._handlers = {}

        self.register("system_report", SystemReportHandler)

    def register(self, name, handler_class):

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Handler name cannot be empty")

        if name in self._handlers:
            raise ValueError(f"Handler already registered: {name}")

        self._handlers[name] = handler_class

    def get(self, name):

        handler_class = self._handlers.get(name)

        if handler_class is None:
            raise ValueError(f"Unknown handler: {name}")

        return handler_class()

    def available(self):
        return list(self._handlers.keys())