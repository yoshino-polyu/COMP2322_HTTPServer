import asyncio

#
# call soon, call later, call at
#
# how to stop the loop
def callback(sleep_times):
    print("sleep {} success".format(sleep_times))
def stoploop(loop):
    loop.stop()
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.call_soon(callback, 2)
    loop.call_soon(stoploop, loop)
    loop.run_forever()
