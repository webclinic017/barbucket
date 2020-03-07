import time

max = 4

try:
    for i in range(max):
        print(i/0)
        time.sleep(1)

except KeyboardInterrupt:
    print('Interrupted by keyboard')

except ZeroDivisionError:
    print('Interrupted by dev by zero')

finally:
    print('after the exception')