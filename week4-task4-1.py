from filefifo import Filefifo

SAMPLE_RATE = 250  # Hz
NUM_HEART_RATES = 20  # Change this to at least 20 for your assignment

fifo = Filefifo(10, name='capture_250Hz_03.txt')

# Initialize sliding window
s1 = fifo.get()
s2 = fifo.get()
s3 = fifo.get()

last_peak_index = None  # Start with no peak
current_index = 2
heart_rates = []

moving_avg_window = [s1, s2, s3]

while len(heart_rates) < NUM_HEART_RATES:
    prev = s1
    curr = s2
    next = s3

    avg = sum(moving_avg_window) / len(moving_avg_window)

    # Debug info
#    print(f"[DEBUG] index={current_index}, val={curr}, avg={avg:.2f}")

    is_peak = (
        curr > avg * 1.03 and
        curr > 10000 and
        curr > prev and
        curr > next
    )

    if is_peak:
        time_ms = current_index * 1000 / SAMPLE_RATE
        interval = current_index - last_peak_index if last_peak_index is not None else None

        if last_peak_index is not None and 62 <= interval <= 500:
            bpm = int(60 * SAMPLE_RATE / interval)
            heart_rates.append(bpm)
            print(f"--> Peak accepted! val={curr}, time={time_ms:.2f}ms, BPM={bpm:.1f}")
        elif last_peak_index is not None:
            print(f"Rejected peak: interval={interval}")
        else:
            print(f"--> First peak detected at {time_ms:.2f}ms (no BPM yet)")

        last_peak_index = current_index

    # Slide window
    s1, s2 = s2, s3
    try:
        s3 = fifo.get()
    except:
        break  # end of file
    current_index += 1

    # Update moving average window
    moving_avg_window.append(s3)
    if len(moving_avg_window) > 30:
        moving_avg_window.pop(0)

# Final output
print("\nCollected Heart Rates (BPM):", heart_rates)

