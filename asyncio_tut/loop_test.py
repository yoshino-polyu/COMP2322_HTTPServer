# event loops + callback (is generator driver in the context of coroutine) + epoll (IO multiplexing is used in event loop)

# import asyncio
# import time
# async def get_html(url):
#     print("start get url")
#     await asyncio.sleep(2) # once reach, return a Future
#     print("end get url")

# if __name__ == "__main__":
#     start_time = time.time()
#     loop = asyncio.get_event_loop()
#     tasks = [get_html("http://www.imooc.com") for i in range(10)]
#     loop.run_until_complete(asyncio.wait(tasks))
#     print(time.time() - start_time)

#
# obtain the return value of coroutine
#

# import asyncio
# import time
# async def get_html(url):
#     print("start get url")
#     await asyncio.sleep(2) # once reach, return a Future
#     print("end get url")

# def callback(future):
#     print("send email to bobby")

# if __name__ == "__main__":
#     start_time = time.time()
#     loop = asyncio.get_event_loop() # one thread can only have one event loop
#     # get_future = asyncio.ensure_future(get_html("http://www.imooc.com")) # submit tasks to thread pool (i.e. the loop variable above)
#     # loop.run_until_complete(get_future) # run_until_complete can accpt Future, or coroutine

#     # or use 
#     task = loop.create_task(get_html("http://www.imooc.com"))
#     task.add_done_callback(callback)
#     loop.run_until_complete(task) # Task is the subclass of Future
#     print(task.result())

#
# wait vs gather
#