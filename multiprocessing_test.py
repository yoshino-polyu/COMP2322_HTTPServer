import multiprocessing
import time

# def get_html(n):
#     time.sleep(n)
#     print("sub_process success")
#     return n

# if __name__ == "__main__":
#     process = multiprocessing.Process(target=get_html, args=(2,))
#     print(process.pid) # before we start the process pid = None
#     process.start()
#     print(process.pid)
#     process.join()


#
# process communication through  Manager().Queue()
#

# from multiprocessing import Manager

# def producer(queue):
#     queue.put("!!!!!a")
#     time.sleep(2)

# def consumer(queue):
#     time.sleep(2)
#     data = queue.get()
#     print("consume {}".format(data))

# def get_html(n):
#     time.sleep(n)
#     print("sub_process success")
#     return n

# if __name__ == "__main__":
#     # use the thread pool
#     queue = Manager().Queue(10)
#     pool = multiprocessing.Pool(2)
    
#     pool.apply_async(producer, args=(queue,))
#     pool.apply_async(consumer, args=(queue,))

#     pool.close()
#     pool.join()



#
# process communication through Pipe
# Pipe is faster than Queue. 
#

# from multiprocessing import Pipe

# def producer(pipe):
#     pipe.send("bobby")

# def consumer(pipe):
#     print(Pipe.recv())

# def get_html(n):
#     time.sleep(n)
#     print("sub_process success")
#     return n

# if __name__ == "__main__":
#     # pipe can only be used between two pipes
#     receive_pipe, send_pipe = Pipe()
#     my_producer = multiprocessing.Process(target=producer,args=(send_pipe,))
#     my_consumer = multiprocessing.Process(target=consumer,args=receive_pipe,)
    
#     my_producer.start()
#     my_consumer.start()

#     my_producer.join()
#     my_consumer.join()

