# coding=utf-8
import glob
import threading
import os
import psutil
import flask_restful
import platform
import getmac
import requests
from time import sleep
if platform.system() == "Windows":
    from ctypes import *
    import ctypes
    from ctypes import byref
    from ctypes import Structure, Union
    from ctypes.wintypes import *

    LONGLONG = ctypes.c_longlong
    HQUERY = HCOUNTER = HANDLE
    pdh = ctypes.windll.pdh


    class PDH_Counter_Union(Union):
        _fields_ = [('longValue', LONG),
                    ('doubleValue', ctypes.c_double),
                    ('largeValue', LONGLONG),
                    ('AnsiStringValue', LPCSTR),
                    ('WideStringValue', LPCWSTR)
                    ]


    class PDH_FMT_COUNTERVALUE(Structure):
        _fields_ = [('CStatus', DWORD),
                    ('union', PDH_Counter_Union)]


    g_cpu_usage = 0

    class CpuWindowsUsagePercentage:
        def __init__(self):
            super(CpuWindowsUsagePercentage, self).__init__()
            self.hQuery = HQUERY()
            self.hCounter = HCOUNTER()
            pdh.PdhOpenQueryW(None,
                              0,
                              byref(self.hQuery))
            pdh.PdhAddCounterW(self.hQuery,
                               u'''\\Processor(_Total)\\% Processor Time''',
                               0,
                               byref(self.hCounter))

        def getCPUUsage(self):
            long_dt = 0x00000100 #because long is 4bytes
            pdh.PdhCollectQueryData(self.hQuery)
            ctypes.windll.kernel32.Sleep(1000)
            pdh.PdhCollectQueryData(self.hQuery)

            counter_type = DWORD(0)
            value = PDH_FMT_COUNTERVALUE()
            pdh.PdhGetFormattedCounterValue(self.hCounter,
                                            long_dt,
                                            byref(counter_type),
                                            byref(value))

            return value.union.longValue

        def run(self):
            global g_cpu_usage
            g_cpu_usage = self.getCPUUsage()
            return g_cpu_usage

class CpuLinuxUsagePercentage:
    def compare_cpu_times(self):
        sum = 0
        idle = 0
        count = 0
        with open('/proc/stat') as f:
            for i in f.readline().strip().split()[1:]:
                count = count + 1
                sum = sum + int(i)
                if count == 4:
                    idle = int(i)
        return sum, idle
    def __init__(self):
        pass
    def return_cpu_percent(self):
        last_total, last_idle = self.compare_cpu_times()
        sleep(5)
        total, idle = self.compare_cpu_times()
        current_idle, current_sum = idle - last_idle, total - last_total
        utilisation = 100.0 * (1.0 - current_idle / current_sum)
        return utilisation


if platform.system() == "Windows":
    class MemoryWindowsStatus(Structure):
        _fields_ = [
            ("dwLength", c_ulong),
            ("dwMemoryLoad", c_ulong),
            ("ullTotalPhys", c_ulonglong),
            ("ullAvailPhys", c_ulonglong),
            ("ullTotalPageFile", c_ulonglong),
            ("ullAvailPageFile", c_ulonglong),
            ("ullTotalVirtual", c_ulonglong),
            ("ullAvailVirtual", c_ulonglong),
            ("sullAvailExtendedVirtual", c_ulonglong),
        ]

        def __init__(self):
            self.dwLength = sizeof(self)  # איתחול dwLength אחרת זה לא עובד טוב
            super().__init__()

class MemoryLinuxStatus:
    def memory_usage_percentage(self):
        with open('/proc/meminfo') as f:
            memory_info = f.readlines()
            mem_total = int(memory_info[0].split()[1])
            mem_free = int(memory_info[1].split()[1])
            utilisation = 100.0 * (1.0 - mem_free / mem_total)
            utilisation = round(utilisation)
            return utilisation


class CpuDetails:
    def __init__(self):
        pass

    def cpu_utilization_procentage(self):
        if platform.system() == "Windows":
            cpu_usage = CpuWindowsUsagePercentage()
            print(type(cpu_usage.run()))
            return cpu_usage.run()
        elif platform.system() == "Linux":
            cpu_usage = CpuLinuxUsagePercentage()
            print(type(cpu_usage))
            return round(cpu_usage.return_cpu_percent())

    def cpu_type(self):
        return platform.processor()


class MemoryDetails:
    def __init__(self):
        pass

    def ram_usage(self):
        return psutil.virtual_memory().used / 1000000000

    def memory_utilization_procentage(self):
        if platform.system() == "Windows":
            memory_usage = MemoryWindowsStatus()
            windll.kernel32.GlobalMemoryStatusEx(byref(memory_usage))
            return memory_usage.dwMemoryLoad
            # return psutil.virtual_memory()[2]
        elif platform.system() == "Linux":
            memory_usage = MemoryLinuxStatus()
            return memory_usage.memory_usage_percentage()


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
        return running_programs, pid, name, cpu_percent, memory_percent


class SendToServer:
    def __init__(self, send_request_to):
        self.send_request_to = send_request_to

    def send_computer_details(self, ProcessDetail, CpuDetail, MemoryDetail):
        while True:
            requests.post(self.send_request_to, json={"CPU usage procentage": CpuDetail.cpu_utilization_procentage(),
                                                    "Memory usage procentage": MemoryDetail.memory_utilization_procentage(),
                                                    "running processes": ProcessDetail.get_running_processes()[0]
                                                    })
    def send_dir_files(self):
        while True:
            print("In a loop!")
            last_content = ""
            dir_url = self.send_request_to + "/get-dir"
            print(dir_url)
            dir_content = requests.post(dir_url)
            print("going to be sent " + dir_content.content.decode())
            if dir_content.content.decode() != "Not found":
                print("content: " + dir_content.content.decode())
                try:
                    dir_items = os.listdir(dir_content.content.decode())
                except:
                    dir_items = ["Not found"]
                requests.get(dir_url, json={"dir list": dir_items})
            upload = requests.get(self.send_request_to + "/get-name")
            file_to_read = upload.content.decode()
            print("upload: " + file_to_read)
            if file_to_read != "" and file_to_read != b"":
                file_bytes = b""
                if upload is not None and upload != "":
                    try:
                        with open(file_to_read, "rb") as r:
                                file_bytes = r.read()
                    except:
                        file_bytes = ""
                    try:
                        requests.get(self.send_request_to + "/write-file", data=file_bytes,timeout=1)
                    except requests.exceptions.ReadTimeout:
                        pass

            sleep(1)


def computer_mac_address():
    return getmac.get_mac_address()


def main():
    ProcessDetail = ProcessDetails()
    CpuDetail = CpuDetails()
    MemoryDetail = MemoryDetails()
    index = 0
    status_code = 200
    response_content = ""
    address_link = 'http://127.0.0.1:5000/computers/verify_login'
    response = requests.get(address_link)
    response_content = response.content.decode()
    status_code = response.status_code
    print(status_code)
    computer_id = ""
    send_request_to = ""
    print(computer_mac_address())
    if status_code == 200:
        while computer_id == "":
            send_request_to = "http://127.0.0.1:5000/computers"
            req_id = requests.post('http://127.0.0.1:5000/computers/verify_login',
                               json={"mac_address": computer_mac_address()})
            computer_id = req_id.content.decode()
            print("computer id: " + computer_id)
            print(type(computer_id))
            if computer_id != "":
                send_request_to = send_request_to + "/" + computer_id
        requests.post(send_request_to,
                      json={"CPU type: ": CpuDetail.cpu_type(), "Ram usage: ": MemoryDetail.ram_usage()})
        requests.post(send_request_to + "/inital-call")
        
        try:
            send_to_server = SendToServer(send_request_to)
            send_computer_details = threading.Thread(target=send_to_server.send_computer_details, args=[ProcessDetail, CpuDetail, MemoryDetail])
            send_dir_files = threading.Thread(target=send_to_server.send_dir_files)
            send_computer_details.setDaemon(True)
            send_dir_files.start()
            send_computer_details.start()
        except(KeyboardInterrupt, SyntaxError):
            print("Bye!")
            exit(1)

if __name__ == "__main__":
    main()
