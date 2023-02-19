# https://stackoverflow.com/questions/9708902/in-practice-what-are-the-main-uses-for-the-yield-from-syntax-in-python-3-3
def reader():
    """A generator that fakes a read from a file, socket, etc."""
    for i in range(4):
        yield '<< %s' % i

def reader_wrapper(g):
    # Manually iterate over data produced by reader
    for v in g:
        yield v

# Instead of manually iterating over reader(), we can just yield from it.
# def reader_wrapper(g):
#     yield from g

wrap = reader_wrapper(reader())
for i in wrap:
    print(i)


# # Result
# << 0
# << 1
# << 2
# << 3

