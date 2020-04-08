
import os
import psutil


def main():
    print("First code commit!")
    while True:
        print("CPU percentage: ", end="")
        print(psutil.cpu_percent(interval=5))

if __name__ == "__main__":
    main()