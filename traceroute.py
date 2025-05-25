#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Any, Dict
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import sr1
import sys
import pprint
import signal
from time import time

@dataclass
class Measurement:
    ip: str
    rtt: float
    ttl: int
    def __repr__(self) -> str:
        return f"IP: {self.ip} | RTT: {self.rtt} | TTL: {self.ttl}"

type Measurements = list[Measurement]

def signal_handler(_x: Any, _y: Any) -> None:
    sys.exit(0)

def trace_route(max_ttl: int = 25, times: int = 30, mode: str ="--trace") -> Dict[int, Measurements]:
    responses: Dict[int, Measurements] = {}

    # ICMP message type 11 is 'time exceeded'
    # https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml#icmp-parameters-codes-11
    time_exceeded = 11
    echo = 0
    icmp_type = echo if mode == "--trace" else time_exceeded

    try:
        for i in range(times):
            print(f"Round {i+1}/{times}")
            for ttl in range(1, max_ttl):
                probe = IP(dst=sys.argv[1], ttl=ttl) / ICMP()
                t_i = time()
                # Use 5 seconds like traceroute's default
                ans = sr1(probe, verbose=False, timeout=5)
                t_f = time()
                rtt = (t_f - t_i)*1000
                if ans is not None:
                    print(f"Response type {ans[ICMP].type}")
                    if ans[ICMP].type == icmp_type:
                        m = Measurement(ip=ans.src, ttl=ttl, rtt=rtt)
                        if ttl not in responses:
                            responses[ttl] = []
                        responses[ttl].append(m)
                        if ttl in responses:
                            print(ttl, m)
    except KeyboardInterrupt:
        print("\n\nKeyboardInterrupt caught in trace_route! Processing data...")
        return responses

    return responses

# Since at any time we can have distinct routes for a same ttl,
# we will simply keep the IP that has been reached the most,
# and use it as a representative for the matching TTL.
def keep_relevant_ips_by_ttl(responses: Dict[int, Measurements], max_ttl: int) -> Dict[int, Measurements]:
    ttl_to_ips = {}
    for ttl in range(1, max_ttl):
        if ttl in responses:
            ips_for_ttl = [m.ip for m in responses[ttl]]
            relevant_ip = max(ips_for_ttl, key=ips_for_ttl.count)
            ttl_to_ips[ttl] = [measure for measure in responses[ttl] if measure.ip == relevant_ip]
    return ttl_to_ips

def averages_for_ttls(data: dict[int, Measurements], ttls: int) -> Dict[int, Measurement]:
    averages: Dict[int, Measurement] = {}
    for ttl in range(1, ttls):
        if ttl in data:
            xs = [m.rtt for m in data[ttl]]
            avg_rtt = sum(xs)/len(xs)
            m = data[ttl][0]
            averages[ttl] = Measurement(m.ip, avg_rtt, ttl)
    return averages

def print_in_between_diffs(averages: Dict[int, Measurement], ttls: int) -> None:
    for ttl in range(1, ttls):
        if ttl in averages and ttl+1 in averages:
            for ttl_2 in range(ttl+1, ttls):
                if ttl_2 in averages:
                    m_1 = averages[ttl]
                    m_2 = averages[ttl_2]
                    diff = m_1.rtt - m_2.rtt
                    pprint.pp(f"RTT between {m_1.ip} (TTL={ttl}) and {m_2.ip} (TTL={ttl_2}): {diff}")
                    break

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    mode = sys.argv[-1]
    ttls = 25

    print("Starting traceroute... Press Ctrl-C to stop")
    responses = trace_route(max_ttl=ttls, times=3, mode=mode)

    ttl_to_ips_and_times = keep_relevant_ips_by_ttl(responses, ttls)
    averages = averages_for_ttls(ttl_to_ips_and_times, ttls)
    print_in_between_diffs(averages, ttls)
