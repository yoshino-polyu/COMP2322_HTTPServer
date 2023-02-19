# def coroutine(func):
#     def start(*args, **kwargs):
#         cr = func(*args, **kwargs)
#         cr.next()
#         return cr
#     return start

# @coroutine
def pro():
    yield 1
    
if __name__ == '__main__':
    g = pro()
    print(next(g))