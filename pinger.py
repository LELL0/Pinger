import subprocess
import argparse
from datetime import datetime


def get_time_now():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def print_data(
    reset_cursor,
    line,
    all_packets,
    time_now,
    total_disconnects,
    no_answer_yet,
    unreachable_packets_count,
    good_packets,
    ping,
):
    print(reset_cursor, end="")
    print(f"Ping Log => {line}")
    print(f"Number Of Packets: {all_packets}  |   Date: {time_now}")
    print(
        f"Errors: {total_disconnects}   |   No Answer: {no_answer_yet}   |   Host Unreachable: {unreachable_packets_count}",
    )
    print(f"Good Packets: {good_packets}  |   Ping: {ping}\033[K")


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
        default="0.2",
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


count, interval, ip_address, size = get_arguments()
command = ["ping", "-O", "-S", size, "-i", interval, ip_address]

if int(count) > 0:
    command.extend(["-c", count])

output = subprocess.Popen(
    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)
print(f"STARTED AT: {get_time_now()}\n\n\n\n")
all_packets = 0
unreachable_packets_count = 0
ping = 0
pings_sum = 0
reset_cursor = "\033[F" * 4
time_now = "00/00/0000 00:00:00"
no_answer_yet = 0
total_disconnects = 0
good_packets = 0
try:
    for line in output.stdout:
        all_packets += 1
        line = line.strip()

        if "Destination Host Unreachable" in line:
            unreachable_packets_count += 1
            total_disconnects += 1
            ping = "NO INTERNET"
        if "no answer yet" in line:
            no_answer_yet += 1
            total_disconnects += 1
            ping = "NO INTERNET"
        if "bytes from" in line:
            good_packets += 1
            try:
                pings_sum += float(line.split("=")[-1].split(" ")[0])
            except:
                pings_sum += 0
            if all_packets % 10 == 0:
                ping = int(pings_sum // 10)
                pings_sum = 0
                time_now = get_time_now()

        print_data(
            reset_cursor,
            line,
            all_packets,
            time_now,
            total_disconnects,
            no_answer_yet,
            unreachable_packets_count,
            good_packets,
            ping,
        )
except KeyboardInterrupt:
    print(f"\rExited AT: {get_time_now()}")
    exit(0)
