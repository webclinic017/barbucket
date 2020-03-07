import time

max = 10

try:
    for i in range(max):
        print(i)
        time.sleep(1)

except KeyboardInterrupt:
    print('Interrupted')