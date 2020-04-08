
import os
import psutil
import flask_restful
import platform
import getmac
import requests

class CpuDetails:
    def __init__(self):
        pass
    def utilization_procentage(self):
        return psutil.cpu_percent(interval=5)
    def cpu_type(self):
        return platform.processor()

class MemoryDetails:
    def __init__(self):
        pass
    def ram_usage(self):
        return psutil.virtual_memory().used/1000000000
    def memory_utilization_procentage(self):
        return psutil.virtual_memory()[2]
class ProcessDetails:
    def __init__(self):
        pass
    def get_running_processes(self):
        running_programs = []
        for running_program in psutil.process_iter():
            running_programs.append(running_program.name())
        return running_programs


def computer_mac_address():
    return getmac.get_mac_address()


def main():
    ProcessDetail = ProcessDetails()
    CpuDetail = CpuDetails()
    MemoryDetail = MemoryDetails()
    print(MemoryDetail.ram_usage())
    req = requests.post('http://127.0.0.1:5000', json={"running processes": ProcessDetail.get_running_processes(), "CPU type: ": CpuDetail.cpu_type(), "Ram usage: ":MemoryDetail.ram_usage()})
    print(req.json())


if __name__ == "__main__":
    main()