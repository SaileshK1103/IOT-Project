from filefifo import Filefifo

SAMPLE_RATE = 250
NUM_SAMPLES = 5000


data = Filefifo(10, name='capture_250Hz_03.txt')
samples = [data.get() for _ in range(NUM_SAMPLES)]


peaks = []
for i in range(1, len(samples) - 1):
    if samples[i - 1] <= samples[i] and samples[i + 1] < samples[i]:
        peaks.append(i)


print("Found peaks at sample indices:", peaks)

if len(peaks) >= 4:
    print("\nShowing first 3 peak-to-peak intervals:")
    for i in range(1, 4):
        interval_samples = peaks[i] - peaks[i - 1]
        interval_seconds = interval_samples / SAMPLE_RATE
        frequency = 1 / interval_seconds
        print(f"Peak {i-1} to {i}: {interval_samples} samples, "
              f"{interval_seconds:.3f} sec, Frequency ≈ {frequency:.2f} Hz")
else:
    print(f"\n⚠ Not enough peaks found ({len(peaks)}). Try increasing NUM_SAMPLES.")