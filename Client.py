
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
        return psutil.virtual_memory().used/1000000000
    def memory_utilization_procentage(self):
        return psutil.virtual_memory()[2]
class ProcessDetails:
    def __init__(self):
        pass
    def get_running_processes(self):
        running_programs = ""
        for running_program in psutil.process_iter():
            if len(running_programs) == 0:
                running_programs = running_program.name()
            else:
                running_programs = running_programs + ',' + running_program.name()
        return running_programs


def computer_mac_address():
    return getmac.get_mac_address()


def main():
    ProcessDetail = ProcessDetails()
    CpuDetail = CpuDetails()
    MemoryDetail = MemoryDetails()
    index = 0
    status_code = 200
    page_content = ""
    req_link = 'http://192.168.1.181:5000/computers/verify_login'
    page = requests.get(req_link)
    page_content = page.content.decode()
    status_code = page.status_code
    print(status_code == 200)
    print(status_code)
    print(page_content)
    computer_id = ""
    send_all_req = ""
    if status_code == 200:
        while computer_id == "":
            send_all_req = "http://192.168.1.181:5000/computers/"
            req = requests.post('http://192.168.1.181:5000/computers/verify_login', json={"MAC address: ": computer_mac_address()})
            computer_id = req.content.decode()
            print(computer_id)
            print(type(computer_id))
            if computer_id != "":
                send_all_req = send_all_req + str(computer_id)
        requests.post(send_all_req, json={"CPU type: ": CpuDetail.cpu_type(), "Ram usage: ":MemoryDetail.ram_usage()})
        while True:
            requests.post(send_all_req, json={"running processes": ProcessDetail.get_running_processes(), "CPU usage procentage": CpuDetail.cpu_utilization_procentage(), "Memory usage procentage": MemoryDetail.memory_utilization_procentage()})


if __name__ == "__main__":
    main()