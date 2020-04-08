
import os
import psutil
import flask_restful
import platform


class CpuDetails:
    def __init__(self):
        pass
    def utilization_procentage(self):
        return "CPU usage percentage: " + str(psutil.cpu_percent(interval=5))
    def cpu_type(self):
        return "CPU type: " + platform.processor()

class MemoryDetails:
    def __init__(self):
        pass
    def ram_usage(self):
        "Ram usage(in gb): " + str(psutil.virtual_memory().used/1000000000)
    def memory_utilization_procentage(self):
        return "Memory usage percentage: " + str(psutil.virtual_memory()[2])
class ProcessDetails:
    def __init__(self):
        pass
    def get_running_processes(self):
        running_programs = []
        for running_program in psutil.process_iter():
            running_programs.append(running_program.name())
        return running_programs


def main():
    pass


if __name__ == "__main__":
    main()