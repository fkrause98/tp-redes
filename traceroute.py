#!/usr/bin/env python3
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import sr1
import sys
import pprint
import signal
from time import *

class Measurement:
    def __init__(self, ip, rtt, ttl):
        self.ip = ip
        self.rtt = rtt
        self.ttl = ttl

    def __repr__(self) -> str:
        return f"IP: {self.ip} | RTT: {self.rtt} | TTL: {self.ttl}"

# Global variable to track responses in case of early termination
global_responses = {}

def signal_handler(_x, _y):
    sys.exit(0)

def trace_route(up_to=25, times=30, mode="--trace"):
    global global_responses
    responses = {}
    global_responses = responses  # Make responses accessible to signal handler

    # ICMP message type 11 is 'time exceeded'
    # https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml#icmp-parameters-codes-11
    time_exceeded = 11
    echo = 0
    icmp_type = echo if mode == "--trace" else time_exceeded

    try:
        for i in range(times):
            print(f"Round {i+1}/{times}")
            for ttl in range(1, up_to):
                probe = IP(dst=sys.argv[1], ttl=ttl) / ICMP()
                t_i = time()
                ans = sr1(probe, verbose=False, timeout=0.8)
                t_f = time()
                rtt = (t_f - t_i)*1000
                if ans is not None:
                    if ans[ICMP].type == icmp_type:
                        if ttl not in responses:
                            responses[ttl] = []
                        responses[ttl].append((ans.src, rtt))
                        if ttl in responses:
                            print(ttl, responses[ttl])
    except KeyboardInterrupt:
        print("\n\nKeyboardInterrupt caught in trace_route! Processing data...")
        return responses

    return responses

def keep_relevant_ips_by_ttl(responses, ttls):
    ttl_to_ips = {}
    for ttl in range(1, ttls):
        if ttl in responses:
            ips_for_ttl = [ip for (ip, _) in responses[ttl]]
            relevant_ip = max(ips_for_ttl, key=ips_for_ttl.count)
            ttl_to_ips[ttl] = [Measurement(ip, rtt, ttl) for (ip, rtt) in responses[ttl] if ip == relevant_ip]
    return ttl_to_ips

def averages_for_ttls(data, ttls):
    averages = {}
    for ttl in range(1, ttls):
        if ttl in data:  # Fixed: was checking 'responses' instead of 'data'
            xs = [m.rtt for m in data[ttl]]
            avg_rtt = sum(xs)/len(xs)
            m = data[ttl][0]
            averages[ttl] = Measurement(m.ip, avg_rtt, ttl)  # Fixed: was using m.rtt instead of avg_rtt
    return averages

def in_between_rtts(averages, ttls):
    for ttl in range(1, ttls):
        if ttl in averages and ttl+1 in averages:
            for ttl_2 in range(ttl+1, ttls):
                if ttl_2 in averages:  # Added check to ensure ttl_2 exists
                    rtt_1 = averages[ttl].rtt
                    rtt_2 = averages[ttl_2].rtt
                    diff = rtt_1 - rtt_2
                    if diff > 0:
                        pprint.pp(f"RTT between {ttl} and {ttl_2}: {diff}")
                        break

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    mode = sys.argv[-1]
    ttls = 100

    print("Starting traceroute... Press Ctrl-C to stop")
    responses = trace_route(up_to=ttls, times=30, mode=mode)

    ttl_to_ips_and_times = keep_relevant_ips_by_ttl(responses, ttls)
    averages = averages_for_ttls(ttl_to_ips_and_times, ttls)
    in_between_rtts(averages, ttls)
