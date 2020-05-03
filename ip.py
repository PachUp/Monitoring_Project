from scapy.all import *

MY_MAC = "50:3e:aa:4c:18:6b"

mac_add = []

def filter_mac(frame):
    return (Ether in frame) and (frame[Ether].dst == MY_MAC)


def print_source_address(frame):
    if len(mac_add) != 0
        for i in mac_add:
            if frame[Ether].src != i:
                mac_add.append(frame[Ether].src)
    print(mac_add)

def main():
    find_mac = sniff(count=5, lfilter=filter_mac, prn=print_source_address)

if __name__ == "__main__":
    main()