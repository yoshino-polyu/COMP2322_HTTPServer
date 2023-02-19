# accepts data sent to it and writes to a socket, fd, etc.
def writer():
    """A coroutine that writes data send to it to fd, socket, etc."""
    while True:
        w = (yield)
        print('>> ', w)

"""
The wrapper needs to accept the data that is sent to it (obviously) 
and should also handle the StopIteration when the for loop is exhausted. 
Evidently just doing for x in coro: yield x won't do. Here is a version that works.
"""
def writer_wrapper(coro):
    coro.send(None)  # prime the coro
    while True:
        try:
            x = (yield)  # Capture the value that's sent
            coro.send(x)  # and pass it to the writer
        except StopIteration:
            pass
# Or, we could do this.
# def writer_wrapper(coro):
#     yield from coro

w = writer()
wrap = writer_wrapper(w)
wrap.send(None)  # "prime" the coroutine
for i in range(4):
    wrap.send(i)

