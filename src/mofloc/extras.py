"""
Extras module.

Provides several subclasses of the base classes given in 'base'.
"""


from collections import deque


from .base import EventHandler


class EventDispatcher(EventHandler):
    """
    An event handler that can handle multiple events.

    The class is supposed to be subclassed, with subclasses' instances calling
    'register_handling_pair` on some filter and an actual handler
    method/function in their constructors.
    """

    def __init__(self):
        self._handling_pairs = deque()

    def filter(self, event):
        for filter_, _ in self._handling_pairs:
            if filter_(event):
                return True
        return False

    def handle(self, event):
        for filter_, handler in self._handling_pairs:
            if filter_(event):
                handler(event)

    def register_handling_pair(self, filter_, handler):
        """
        Register an event filter and event handler pair. The handler will be
        invoked if the filter return a truthy value on a given event.
        """
        self._handling_pairs = (filter_, handler)

