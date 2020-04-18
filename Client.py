import os
import psutil
import flask_restful
import platform
import getmac
import requests


class CpuDetails:
    def __init__(self):
        pass

    def cpu_utilization_procentage(self):
        return psutil.cpu_percent(interval=5)

    def cpu_type(self):
        return platform.processor()


class MemoryDetails:
    def __init__(self):
        pass

    def ram_usage(self):
        return psutil.virtual_memory().used / 1000000000

    def memory_utilization_procentage(self):
        return psutil.virtual_memory()[2]


class ProcessDetails:
    def __init__(self):
        pass

    def get_running_processes(self):
        running_programs = []
        pid = []
        name = []
        cpu_percent = []
        memory_percent = []
        for running_program in psutil.process_iter():
            infoDict = running_program.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])
            running_programs.append(infoDict)
            pid.append(infoDict["pid"])
            name.append(infoDict["name"])
            cpu_percent.append(infoDict["cpu_percent"])
            memory_percent.append(infoDict["memory_percent"])
        print(running_programs)
        return running_programs, pid, name, cpu_percent, memory_percent


def computer_mac_address():
    return getmac.get_mac_address()


def main():
    ProcessDetail = ProcessDetails()
    CpuDetail = CpuDetails()
    MemoryDetail = MemoryDetails()
    index = 0
    status_code = 200
    response_content = ""
    address_link = 'http://192.168.1.181:5000/computers/verify_login'
    response = requests.get(address_link)
    response_content = response.content.decode()
    status_code = response.status_code
    print(status_code == 200)
    print(status_code)
    print(response_content)
    computer_id = ""
    send_request_to = ""
    if status_code == 200:
        while computer_id == "":
            send_request_to = "http://192.168.1.181:5000/computers/"
            req_id = requests.post('http://192.168.1.181:5000/computers/verify_login',
                                   json={"MAC address: ": computer_mac_address()})
            computer_id = req_id.content.decode()
            print(computer_id)
            print(type(computer_id))
            if computer_id != "":
                send_request_to = send_request_to + str(computer_id)
        requests.post(send_request_to,
                      json={"CPU type: ": CpuDetail.cpu_type(), "Ram usage: ": MemoryDetail.ram_usage()})
        while True:
            requests.post(send_request_to, json={"running processes": ProcessDetail.get_running_processes()[0],
                                                 "CPU usage procentage": CpuDetail.cpu_utilization_procentage(),
                                                 "Memory usage procentage": MemoryDetail.memory_utilization_procentage(),
                                                 "task status pid": ProcessDetail.get_running_processes()[1],
                                                 "task status name": ProcessDetail.get_running_processes()[2],
                                                 "task status cpu percent": ProcessDetail.get_running_processes()[3],
                                                 "task status memory percent": ProcessDetail.get_running_processes()[4],
                                                 })


if __name__ == "__main__":
    main()
