import threading
import time 

print("Hello")

t0 = time.time()

def square(num):
    print(f"Square: {num*num}")
    time.sleep(1)
    

def cube(num):
    print(f"Cube: {num*num*num}")
    time.sleep(1)
    

first_thread = threading.Thread(target=square, args=(4,))
second_thread = threading.Thread(target=cube, args=(4,))

first_thread.start()
second_thread.start()
t1 = time.time() - t0

print("anana")

first_thread.join()
second_thread.join()
t2 = time.time() - t0




print(f"t0 : {t0-t0} | t1 : {round(t1,4)} | t2 : {round(t2,4)}")