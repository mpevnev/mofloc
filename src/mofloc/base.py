"""
Base module.

Provides base classes and functions used troughout the library.
"""

from collections import deque


#--------- base classes ---------#

class Flow():
    """
    A class used to represent a portion of program's control flow.

    When the flow needs to be changed, raise a ChangeFlow exception.

    When execution needs to stop, raise EndFlow exception.
    """

    def __init__(self):
        self._entry_points = {}
        self._event_sources = deque()
        self._event_handlers = deque()
        self._preactions = deque()
        self._postactions = deque()
        self._on_exception = {}
        self._on_termination = deque()
        self._discard_events_flag = False

    #--------- flow control ---------#

    def _execute(self, entry_point_id, *args, **kwargs):
        """ Execute this flow, starting with given entry point. """
        if self._entry_points:
            if entry_point_id not in self._entry_points:
                raise MissingEntryPoint(self, entry_point_id)
            did_entry_point = False
        else:
            did_entry_point = True
        while True:
            try:
                if not did_entry_point:
                    self._entry_points[entry_point_id](*args, **kwargs)
                    did_entry_point = True
                for action in self._preactions:
                    action()
                has_events = self._process_events()
                for action, must_have_event in self._postactions:
                    if not has_events and must_have_event:
                        continue
                    action()
            except (ChangeFlow, EndFlow) as e:
                self.run_termination_actions()
                raise e
            except BaseException as e:
                for typetuple, cleanup in self._on_exception.items():
                    if isinstance(e, typetuple):
                        cleanup(e)
                raise e

    def register_entry_point(self, name, method):
        """
        Register 'method' as an entry point with name 'name'. It will be
        available later as a target for ChangeFlow exceptions and 'execute'.

        'name' should be a hashable object.

        Raise ValueError if an entry point with this name is already
        registered.
        """
        if name in self._entry_points:
            raise ValueError(f"Entry point \"{name}\" is already registered")
        self._entry_points[name] = method

    def redefine_entry_point(self, name, method):
        """
        Change the method associated with an entry point given by 'name', or
        create an association if it doesn't already exist.

        'name' should be a hashable object.
        """
        self._entry_points[name] = method

    def delete_entry_point(self, name):
        """
        Remove a registered entry point.
        """
        try:
            del self._entry_points[name]
        except KeyError:
            pass

    #--------- termination control ---------#

    def register_exception_action(self, exception_or_tuple, action):
        """
        Register an action to be run when an exception of a given type or
        given types is raised. ChangeFlow and EndFlow cannot be handled in this
        manner, however.

        Exception action will receive the raised exception as its only
        argument.
        """
        self._on_exception[exception_or_tuple] = action

    def register_termination_action(self, action):
        """
        Register an action to be run if this flow terminates normally.
        """
        self._on_termination.append(action)

    def run_termination_actions(self):
        """ Run all registered termination actions. """
        for term in self._on_termination:
            term()

    #--------- event handling ---------#

    def process_event(self, event):
        """ Process an event. """
        res = False
        for handler in self._event_handlers:
            if handler(event):
                res = True
        return res

    def register_event_source(self, source):
        """
        Register an event source. It should be a callable with zero arguments
        (a method is also acceptable), which should return an event object on
        each invokation, or raise a NoEvent exceptions if there is no pending
        event.
        """
        self._event_sources.append(source)

    def register_event_handler(self, handler):
        """
        Register an event handler.

        'handler' should be a callable of a single argument, the event it
        should handle. If the handler can't handle the event, it should return
        False, otherwise it should do something and return True.
        """
        self._event_handlers.append(handler)

    def register_preevent_action(self, action):
        """
        Register 'action' as an action to be run before processing any events.
        It should be a callable with no arguments.

        An action registered this way will be run every time the flow checks
        for events.

        Notice the asymmetry between pre-event and post-event actions:
        pre-event actions are run whether or not there are events pending,
        post-event actions may be marked as requiring a pending event to run.
        """
        self._preactions.append(action)

    def register_postevent_action(self, action, must_have_event=False):
        """
        Register 'action' as an action to be run after processing all events.

        It should be a callable with no arguments.

        An action registered this way will be run every time the flow checks
        for events.

        If 'must_have_event' is truthy, execute the action only if there is a
        pending event. If it's falsey, execute it in either case.

        Notice the asymmetry between pre-event and post-event actions:
        pre-event actions are run whether or not there are events pending,
        post-event actions may be marked as requiring a pending event to run.
        """
        self._postactions.append((action, must_have_event))

    def discard_events(self):
        """
        Discard any pending unprocessed events. Note that this will only work
        if registered event sources support discarding events.

        If called during handing an event, handling will stop after the event
        that's being handled currently is finished.
        """
        self._discard_events_flag = True

    #--------- hidden stuff ---------#

    def _process_events(self):
        """
        Process any events that were fired by the event sources on this flow.

        Return True if an event was processed, False otherwise.
        """
        processed = False
        for source in self._event_sources:
            try:
                event = source.get_event()
                processed_this_event = self.process_event(event)
                processed = processed or processed_this_event
                if self._discard_events_flag:
                    break
            except NoEvent:
                pass
        if self._discard_events_flag:
            self._discard_events_flag = False
            for source in self._event_sources:
                source.discard_events()
        return processed



class EventSource():
    """
    An abstract class representing an event source.

    Subclasses must override 'get_event', and may override 'discard_events',
    'stop' and 'restart' methods.
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

    def stop(self):
        """ Stop producing events. """
        pass

    def restart(self):
        """
        Restart the event source. An override of this should undo what a call
        to 'stop' has done.
        """
        pass


#--------- exceptions ---------#

class ChangeFlow(Exception):
    """
    Throw an exception of this type if the current program Flow needs to
    change.

    'new_flow' should be the Flow object that will receive the control.

    'entry_point' determines which entry point of the target Flow object will
    be used.

    The rest of positional and keyword arguments will be fed to the target
    entry point method/function.
    """

    def __init__(self, new_flow, entry_point, *args, **kwargs):
        super().__init__("Uncaught ChangeFlow signal")
        self.new_flow = new_flow
        self.entry_point = entry_point
        self.args = args
        self.kwargs = kwargs


class EndFlow(Exception):
    """
    Throw an exception of this type if flow execution needs to stop,
    immediately.

    'return_value' will be returned by the enclosing 'execute'.
    """

    def __init__(self, return_value=None):
        super().__init__("Uncaught EndFlow signal")
        self.return_value = return_value


class NoEvent(Exception):
    """
    An event source should throw this if there is no pending event.
    """

    def __init__(self):
        super().__init__("Uncaught NoEvent signal")


class MissingEntryPoint(Exception):
    """ An exception to be thrown when a specified entry point doesn't exist. """

    def __init__(self, flow, entry_point):
        super().__init__(f"Entry point \"{entry_point}\" does not exist in the flow {flow}")


#--------- main functions ---------#

def execute(flow, entry_point, *args, **kwargs):
    """
    Start executing 'flow' using entry point 'entry_point' with positional
    and keyword arguments given by 'args' and 'kwargs' respectively, then
    proceed with executing whatever flows are requested by raising ChangeFlow
    exceptions.

    Execution ends if any invoked flow raises a EndFlow exception, and the
    function returns the value passed to the terminating exception.
    """
    while True:
        try:
            flow._execute(entry_point, *args, **kwargs)
        except ChangeFlow as change:
            flow = change.new_flow
            entry_point = change.entry_point
            args = change.args
            kwargs = change.kwargs
        except EndFlow as end:
            return end.return_value
