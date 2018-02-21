"""
Base module.

Provides base classes and functions used troughout the library.

"""

from collections import deque

DEFAULT_ENTRY_POINT = "default"

class Flow():
    """
    An abstract class used to represent a portion of program's control flow.

    Subclasses may override 'flow_before_events' and 'flow_after_events'
    methods to perform some tasks unrelated to events. When the flow needs to
    be changed, raise a ChangeFlow exception.
    """

    def __init__(self):
        self._entry_points = deque()
        self._event_sources = deque()
        self._event_handlers = deque()
        self._discard_events_flag = False

    #--------- flow control ---------#

    def execute(self, *args, entry_point_id=DEFAULT_ENTRY_POINT, **kwargs):
        """ Execute this flow, starting with given entry point. """
        found_an_entry_point = False
        for entry_id, method in self._entry_points:
            if entry_id == entry_point_id:
                found_an_entry_point = True
                method(*args, **kwargs)
                break
        if not found_an_entry_point:
            raise MissingEntryPoint(entry_point_id)
        while True:
            self.flow_before_events()
            self._process_events()
            self.flow_after_events()

    def flow_before_events(self):
        """ An action to be executed before processing any events. """
        pass

    def flow_after_events(self):
        """ An action to be executed after processing any events. """
        pass

    def register_entry_point(self, name, method):
        """
        Register 'method' as an entry point with name 'name'. It will be
        available later as a target for ChangeFlow exceptions and 'execute'.

        Raise ValueError if an entry point with this name is already
        registered.
        """
        for entry_point_name, _ in self._entry_points:
            if entry_point_name == name:
                raise ValueError(f"Entry point \"{name}\" is already registered")
        self._entry_points.append((name, method))

    #--------- event handling ---------#

    def register_event_source(self, source):
        """
        Register an event source. It should be a callable with zero arguments
        (a method is also acceptable), which should return None if there were
        no events, or an arbitrary object representing an event otherwise.
        """
        self._event_sources.append(source)

    def register_event_handler(self, event_filter, handler):
        """
        Register an event handler.

        The 'handler' argument should be a callable that takes a single
        arbitrary object as an argument, which will be supplied by an event
        source.

        The 'event_filter' argument should be a callable that takes a single
        argument and returns a boolean. It will receive an event from an event
        source as input, and should return truthy value if the received event
        should be handled by the associated handler.
        """
        self._event_handlers.append((event_filter, handler))

    def discard_events(self):
        """
        Discard any pending unprocessed events. Note that this will only work
        if registered event sources support discarding events.

        If called during event handling, will *not* interrupt it.
        """
        self._discard_events_flag = True

    #--------- hidden stuff ---------#

    def _process_events(self):
        """
        Process any events that were fired by the event sources on this flow.
        """
        for source in self._event_sources:
            try:
                event = source.get_event()
                self._process_event(event)
                if self._discard_events_flag:
                    break
            except NoEvent:
                pass
        if self._discard_events_flag:
            self._discard_events_flag = False
            for source in self._event_sources:
                source.discard_events()

    def _process_event(self, event):
        """ Process an event. """
        for event_filter, handler in self._event_handlers:
            if event_filter(event):
                handler(event)


class EventSource():
    """
    An abstract class representing an event source.

    Subclasses should override 'get_event' method, and may override
    'discard_events' method.
    """

    def get_event(self):
        """
        Produce an event or retrieve it from some other source.

        Throw NoEvent exception if there were no event.
        """
        raise NotImplementedError

    def discard_events(self):
        """
        Discard pending events.
        """
        pass


class ChangeFlow(Exception):
    """
    Throw such exception if the current program Flow needs to change.

    The first argument to the constructor should be the Flow object that will
    receive the control.

    Keyword-only argument 'entry_point' determines, which entry point of the
    target Flow object will be used, defaults to DEFAULT_ENTRY_POINT.
    
    The rest of positional and keyword-only arguments will be fed to the target
    entry point method/function.
    """

    def __init__(self, new_flow, *args, entry_point=DEFAULT_ENTRY_POINT, **kwargs):
        super().__init__("Uncaught ChangeFlow signal")
        self.new_flow = new_flow
        self.entry_point = entry_point
        self.args = args
        self.kwargs = kwargs


class NoEvent(Exception):
    """
    An event source should throw this if there were no event produced.
    """

    def __init__(self):
        super().__init__("Uncaught NoEvent signal")


class MissingEntryPoint(Exception):
    """ An exception to be thrown when a specified entry point doesn't exist. """

    def __init__(self, entry_point):
        super().__init__(f"Entry point \"{entry_point}\" does not exist")


def execute(flow, *args, entry_point=DEFAULT_ENTRY_POINT, **kwargs):
    """
    Start executing 'flow' using entry point 'entry_point' with positional
    and keyword arguments given by 'args' and 'kwargs' respectively, then
    proceed with executing whatever flows are requested by raising ChangeFlow
    exceptions.
    """
    while flow is not None:
        try:
            flow.execute(entry_point, *args, **kwargs)
        except ChangeFlow as change:
            flow = change.new_flow
            entry_point = change.entry_point
            args = change.args
            kwargs = change.kwargs
