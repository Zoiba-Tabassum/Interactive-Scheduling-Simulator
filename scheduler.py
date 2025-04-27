def fcfs(process_list):
    # Sort by Arrival Time first
    process_list.sort(key=lambda x: x.arrival_time)

    current_time = 0
    for process in process_list:
        if current_time < process.arrival_time:
            current_time = process.arrival_time  # CPU is idle until the process arrives

        process.start_time = current_time
        process.finish_time = current_time + process.burst_time
        process.waiting_time = process.start_time - process.arrival_time
        process.turnaround_time = process.finish_time - process.arrival_time
        process.response_time = process.start_time - process.arrival_time

        current_time += process.burst_time

    return process_list

def sjf_non_preemptive(process_list):
    # Sort by arrival time first
    process_list.sort(key=lambda x: (x.arrival_time, x.burst_time))

    completed = []
    ready_queue = []
    current_time = 0
    processes = process_list.copy()

    while processes or ready_queue:
        # Move all processes that have arrived to ready_queue
        while processes and processes[0].arrival_time <= current_time:
            ready_queue.append(processes.pop(0))
        
        if ready_queue:
            # Sort ready_queue by burst_time (Shortest Job First)
            ready_queue.sort(key=lambda x: x.burst_time)
            current_process = ready_queue.pop(0)

            current_process.start_time = current_time
            current_process.finish_time = current_time + current_process.burst_time
            current_process.waiting_time = current_process.start_time - current_process.arrival_time
            current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
            current_process.response_time = current_process.start_time - current_process.arrival_time

            completed.append(current_process)
            current_time = current_process.finish_time
        else:
            # CPU is idle, jump to next process arrival
            if processes:
                current_time = processes[0].arrival_time

    return completed


def priority_non_preemptive(process_list):
    # Sort by arrival time first
    process_list.sort(key=lambda x: (x.arrival_time, x.priority))

    completed = []
    ready_queue = []
    current_time = 0
    processes = process_list.copy()

    while processes or ready_queue:
        # Move all processes that have arrived to ready_queue
        while processes and processes[0].arrival_time <= current_time:
            ready_queue.append(processes.pop(0))
        
        if ready_queue:
            # Sort ready_queue by priority (lower number = higher priority)
            ready_queue.sort(key=lambda x: x.priority)
            current_process = ready_queue.pop(0)

            current_process.start_time = current_time
            current_process.finish_time = current_time + current_process.burst_time
            current_process.waiting_time = current_process.start_time - current_process.arrival_time
            current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
            current_process.response_time = current_process.start_time - current_process.arrival_time

            completed.append(current_process)
            current_time = current_process.finish_time
        else:
            # CPU is idle, jump to next process arrival
            if processes:
                current_time = processes[0].arrival_time

    return completed

def round_robin(process_list, time_quantum):
    process_list.sort(key=lambda x: x.arrival_time)

    ready_queue = []
    completed = []
    current_time = 0
    processes = process_list.copy()

    while processes or ready_queue:
        # Move all processes that have arrived to ready_queue
        while processes and processes[0].arrival_time <= current_time:
            ready_queue.append(processes.pop(0))

        if ready_queue:
            current_process = ready_queue.pop(0)

            if current_process.start_time is None:
                current_process.start_time = current_time
                current_process.response_time = current_time - current_process.arrival_time

            execute_time = min(time_quantum, current_process.remaining_time)
            current_time += execute_time
            current_process.remaining_time -= execute_time

            # Move newly arrived processes into ready_queue during execution
            while processes and processes[0].arrival_time <= current_time:
                ready_queue.append(processes.pop(0))

            if current_process.remaining_time == 0:
                current_process.finish_time = current_time
                current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed.append(current_process)
            else:
                # If not finished, put it back to end of ready_queue
                ready_queue.append(current_process)
        else:
            if processes:
                current_time = processes[0].arrival_time

    return completed


def mlfq(process_list, q1=4, q2=8):
    process_list.sort(key=lambda x: x.arrival_time)

    completed = []
    queue1 = []
    queue2 = []
    queue3 = []

    current_time = 0
    processes = process_list.copy()

    while processes or queue1 or queue2 or queue3:
        # Move newly arrived processes to queue1
        while processes and processes[0].arrival_time <= current_time:
            queue1.append(processes.pop(0))

        if queue1:
            current_process = queue1.pop(0)
            execute_time = min(q1, current_process.remaining_time)
        elif queue2:
            current_process = queue2.pop(0)
            execute_time = min(q2, current_process.remaining_time)
        elif queue3:
            current_process = queue3.pop(0)
            execute_time = current_process.remaining_time  # FCFS no quantum
        else:
            if processes:
                current_time = processes[0].arrival_time
            continue

        if current_process.start_time is None:
            current_process.start_time = current_time
            current_process.response_time = current_time - current_process.arrival_time

        current_time += execute_time
        current_process.remaining_time -= execute_time

        # Move new arrivals during execution
        while processes and processes[0].arrival_time <= current_time:
            queue1.append(processes.pop(0))

        if current_process.remaining_time == 0:
            current_process.finish_time = current_time
            current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
            current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
            completed.append(current_process)
        else:
            # Move to lower queue
            if current_process in queue1:
                queue2.append(current_process)
            elif current_process in queue2:
                queue3.append(current_process)
            else:
                queue3.append(current_process)

    return completed
