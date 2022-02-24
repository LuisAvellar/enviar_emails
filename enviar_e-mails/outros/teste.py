import time
def rr():
    print("start: ")
    print("\r", end="")
    print("{:.1%}", end="")

def progression_bar(total_time=2):
    num_bar = 50
    sleep_intvl = total_time/num_bar
    print("start: ")
    for i in range(1,num_bar):
        print("\r", end="")
        print("{:.1%} ".format(i/num_bar), end="")
        time.sleep(sleep_intvl)
#
# progression_bar()

for i in range(1, 50):
    print("\r", end="")
    print(f"{i}", end="")
