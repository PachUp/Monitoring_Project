from time import sleep

def compare_cpu_times():
    sum = 0
    idle = 0
    count = 0
    with open('/proc/stat') as f:
        for i in f.readline().strip().split()[1:]:
            count = count + 1
            sum = sum + int(i)
            if count == 4:
                idle = int(i)
    return sum,idle
while True:
    last_total, last_idle = compare_cpu_times()
    sleep(5)
    total, idle = compare_cpu_times()
    current_idle, current_sum = idle - last_idle, total - last_total
    utilisation = 100.0 * (1.0 - current_idle / current_sum)
    print(utilisation)
    print(type(utilisation))