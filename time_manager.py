def read_time_left():
    try:
        time_left = int(open("time_left.txt", "r").read().strip())
    except:
        time_left = 0
        open("time_left.txt", "w").write(str(time_left))
    return time_left


def write_time_left(time_left):
    open("time_left.txt", "w").write(str(time_left))
