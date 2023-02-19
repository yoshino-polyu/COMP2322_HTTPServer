class SpamException(Exception):
    pass

"""
Let's make it more complicated. What if our writer needs to handle exceptions? 
Let's say the writer handles a SpamException and it prints *** if it encounters one.
"""
def writer():
    while True:
        try:
            w = (yield)
        except SpamException:
            print('***')
        else:
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

# What if we don't change writer_wrapper? Does it work? Let's try
w = writer()
wrap = writer_wrapper(w)
wrap.send(None)  # "prime" the coroutine
for i in [0, 1, 2, 'spam', 4]:
    if i == 'spam':
        wrap.throw(SpamException)
    else:
        wrap.send(i)

# Expected Result
# >>  0
# >>  1
# >>  2
# ***
# >>  4

# Actual Result
# >>  0
# >>  1
# >>  2
# Traceback (most recent call last):
#   ... redacted ...
#   File ... in writer_wrapper
#     x = (yield)
# __main__.SpamException

"""
Um, it's not working because x = (yield) just raises the exception and everything comes to a crashing halt. 
Let's make it work, but manually handling exceptions and sending them or throwing them into the sub-generator (writer)
"""
def writer_wrapper(coro):
    """Works. Manually catches exceptions and throws them"""
    coro.send(None)  # prime the coro
    while True:
        try:
            try:
                x = (yield)
            except Exception as e:   # This catches the SpamException
                coro.throw(e)
            else:
                coro.send(x)
        except StopIteration:
            pass

# But so does this! Do the same job as above
# def writer_wrapper(coro):
#     yield from coro
# The yield from transparently handles sending the values or throwing values into the sub-generator.

