import math

class HRVCalculator:
    def __init__(self, sample_rate=250):
        self.sample_rate = sample_rate
        self.ppi_list = []  # PPI intervals (in ms)

    def add_ppi(self, interval_samples):
        """ Add new interval (in samples) """
        ppi_ms = (interval_samples * 1000) / self.sample_rate  # Convert to milliseconds
        self.ppi_list.append(ppi_ms)

    def calculate_hrv(self):
        """ Calculate Mean HR, Mean PPI, SDNN, RMSSD """
        filtered = [p for p in self.ppi_list if 300 <= p <= 1500]
        if len(filtered) < 2:
            return None

        mean_ppi = sum(self.ppi_list) / len(self.ppi_list)  # ms
        mean_hr = 60000 / mean_ppi  # bpm

        # SDNN (Standard Deviation of NN intervals)
        variance = sum((ppi - mean_ppi)**2 for ppi in self.ppi_list) / len(self.ppi_list)
        sdnn = math.sqrt(variance)

        # RMSSD (Root Mean Square of Successive Differences)
        successive_diffs = [(self.ppi_list[i] - self.ppi_list[i-1]) for i in range(1, len(self.ppi_list))]
        rmssd = math.sqrt(sum(diff**2 for diff in successive_diffs) / len(successive_diffs))

        return {
            "mean_hr": round(mean_hr, 2),
            "mean_ppi": round(mean_ppi, 2),
            "sdnn": round(sdnn, 2),
            "rmssd": round(rmssd, 2),
            "sample_count": len(self.ppi_list)
        }

    def clear(self):
        """ Clear stored intervals """
        self.ppi_list = []

