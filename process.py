class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time  # For preemptive algorithms
        self.priority = priority
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None

    def __repr__(self):
        return f"PID:{self.pid} AT:{self.arrival_time} BT:{self.burst_time} P:{self.priority}"
