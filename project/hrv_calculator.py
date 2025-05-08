import math


class HRVCalculator:
    def __init__(self):
        self.ppi_list = []

    def add_ppi(self, ppi_ms):
        """Add PPI in milliseconds"""
        self.ppi_list.append(ppi_ms)

    def calculate_hrv(self):
        valid_ppis = [p for p in self.ppi_list if 300 <= p <= 1500]
        if len(valid_ppis) < 2:
            return None

        mean_ppi = sum(valid_ppis) / len(valid_ppis)
        mean_hr = 60000 / mean_ppi

        variance = sum((p - mean_ppi) ** 2 for p in valid_ppis) / len(valid_ppis)
        sdnn = math.sqrt(variance)

        successive_diffs = [valid_ppis[i] - valid_ppis[i - 1] for i in range(1, len(valid_ppis))]
        rmssd = math.sqrt(sum(d ** 2 for d in successive_diffs) / len(successive_diffs))

        return {
            "mean_hr": round(mean_hr, 2),
            "mean_ppi": round(mean_ppi, 2),
            "sdnn": round(sdnn, 2),
            "rmssd": round(rmssd, 2),
            "sdnn": round(sdnn, 2)
        }

    def clear(self):
        self.ppi_list.clear()



