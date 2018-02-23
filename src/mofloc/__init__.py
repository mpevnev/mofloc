"""

Modular Flow Control.

The library provides a way to split a program's control flow into blocks and to
handle events occuring in such blocks without resorting to things like
explicitly keeping track of program's state.

To use the library, you need to subclass the Flow class. Define methods you
want to use as entry points, and register them as such in the constructor using 
'register_entry_point' method. After that, you will be able to raise ChangeFlow
exceptions (the constructor is 
> (new_flow, entry_point_name, *entry_point_args, **entry_point_kwargs))
to change the flow currently being executed. You can do this anywhere inside
event handlers (more about them below) and entry points. To begin execution,
use 'execute' function:
> execute(starting_flow, entry_point, *entry_point_args, **entry_point_kwargs)

You can also register event sources and event handlers. To create an event
source, subclass EventSource class. Override 'get_event(self)' method: it
should return an event object produced by the source or raise a NoEvent
exception if there is none. Once you have such a class, instantiate it and
use 'register_event_source(self, source)' method of the Flow class to bind it
to a Flow object. To create an event handler, subclass EventHandler class:
override 'filter(self, event)', which should return a truthy value if 'event'
should be handled by the handler, and 'handle(self, event)', which will handle
the event. After that, instantiate your class and bind the instance of it to
a Flow object via 'register_event_handler(self, handler)'.

"""

from mofloc.base import *
from mofloc.extras import *
