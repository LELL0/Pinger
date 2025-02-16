#!/usr/bin/python3

import subprocess
from colorama import Fore
import colorama
import sys
import argparse
from datetime import datetime
import platform

NUM_OF_LINES = 6

LOADING_FRAMES = ['[     ]', '[=    ]', '[==   ]', '[===  ]', '[==== ]', '[=====]', '[ ====]', '[  ===]', '[   ==]', '[    =]',
                  '[     ]', '[    =]', '[   ==]', '[  ===]', '[ ====]', '[=====]', '[==== ]', '[===  ]', '[==   ]', '[=    ]']

NUM_OF_LOADING_FRAMES = len(LOADING_FRAMES)


def check_os():
    if platform.system() == "Linux":
        return "Linux"
    elif platform.system() == "Windows":
        return "Windows"
    else:
        return "Unknown OS"


def get_time_now():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def prt(text: str, color="RESET", dynamic=False, end="\n"):
    color = color.upper()
    if color == "RESET":
        col = Fore.RESET
    elif color == "RED":
        col = Fore.RED
    elif color == "GREEN":
        col = Fore.GREEN
    elif color == "BLUE":
        col = Fore.BLUE
    elif color == "LIGHTMAGENTA_EX":
        col = Fore.LIGHTMAGENTA_EX
    elif color == "LIGHTRED_EX":
        col = Fore.LIGHTRED_EX
    elif color == "LIGHTBLACK_EX":
        col = Fore.LIGHTBLACK_EX
    if dynamic:
        print(f"{col}\r{text}\033[K{colorama.Style.RESET_ALL}", end=end)
    elif not dynamic:
        print(f"{col}{text}{colorama.Style.RESET_ALL}\033[K", end=end)
    print()
    sys.stdout.flush()


def print_data(reset_cursor, line, all_packets, time_now, total_disconnects, no_answer_yet, unreachable_packets_count, good_packets, ping, no_answer_yet_text, host_unreachable_text):
    print(reset_cursor, end="")
    prt(f"Ping Log => {line}", end="", color="LIGHTMAGENTA_EX")
    prt(f"Number Of Packets: {all_packets}  |   Date: {time_now}", end="", color="BLUE")
    prt(f"Errors: {total_disconnects}   |   {no_answer_yet_text}: {no_answer_yet}   |   {host_unreachable_text}: {unreachable_packets_count}", end="", color="RED", )
    prt(f"Good Packets: {good_packets}  |   Ping: {ping}", end="", color="GREEN")
    prt(f"Packet Loss: {round((total_disconnects/all_packets)*100,2)}%", end="", color="LIGHTMAGENTA_EX")
    prt(LOADING_FRAMES[all_packets % (NUM_OF_LOADING_FRAMES)], end="", color="LIGHTBLACK_EX")


def get_arguments():
    parser = argparse.ArgumentParser(prog="Pinger Program")

    parser.add_argument(
        "-c",
        "--count",
        help="stop after <count> replies (default is <><>)",
        required=False,
        default="0",
    )
    parser.add_argument(
        "-i",
        "--interval",
        help="seconds between sending each packet",
        required=False,
        default="1",
    )
    parser.add_argument(
        "-ip",
        "--ip-address",
        help="destination to ping",
        required=False,
        default="8.8.8.8",
    )
    parser.add_argument(
        "-S",
        "--size",
        help="use <size> as SO_SNDBUF socket option value",
        required=False,
        default="64",
    )

    args = parser.parse_args()
    return args.count, args.interval, args.ip_address, args.size


if __name__ == "__main__":

    count, interval, ip_address, size = get_arguments()

    os_type = check_os()

    if os_type == "Windows":
        command = ["ping", "-t", ip_address]
        good_packets_text = "Reply from"
        no_answer_yet_text = "Request timed out"
        host_unreachable_text = "Destination net unreachable"

    else:
        command = ["ping", "-O", "-S", size, "-i", interval, ip_address]
        good_packets_text = "bytes from"
        no_answer_yet_text = "no answer yet"
        host_unreachable_text = "Host Unreachable"

    if int(count) > 0:
        command.extend(["-c", count])

    output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(f"STARTED AT: {get_time_now()}"+"\n"*NUM_OF_LINES)
    all_packets = 0
    unreachable_packets_count = 0
    ping = 0
    pings_list = []
    pings_counter = 0
    reset_cursor = "\033[F" * NUM_OF_LINES
    time_now = "00/00/0000 00:00:00"
    no_answer_yet = 0
    total_disconnects = 0
    good_packets = 0
    try:
        for line in output.stdout:
            all_packets += 1
            line = line.strip()
            if host_unreachable_text in line:
                unreachable_packets_count += 1
                total_disconnects += 1
                ping = "NO CONNECTION"

            elif no_answer_yet_text in line:
                no_answer_yet += 1
                total_disconnects += 1
                ping = "NO CONNECTION"

            elif "General failure" in line:
                total_disconnects += 1
                ping = "NO CONNECTION"

            elif good_packets_text in line:
                good_packets += 1
                try:
                    pings_list.insert(
                        0, float(line.split("=")[-1].split(" ")[0]))
                    pings_list = pings_list[:10]
                    pings_counter += 1
                    ping = int(sum(pings_list) // len(pings_list))
                    time_now = get_time_now()
                except:
                    pass
            else:
                ping = ""

            print_data(reset_cursor, line, all_packets, time_now, total_disconnects, no_answer_yet,
                       unreachable_packets_count, good_packets, ping, no_answer_yet_text, host_unreachable_text)

    except KeyboardInterrupt:
        print(f"\rExited AT: {get_time_now()}")
        exit(0)
