import utime

class HistoryManager:
    def __init__(self, filename="history.txt"):
        self.filename = filename

    def save_record(self, data: dict):
        try:
            timestamp = utime.localtime()
            timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*timestamp[:6])
            line = f"{timestamp_str}|mean_hr:{data['mean_hr']},mean_ppi:{data['mean_ppi']},sdnn:{data['sdnn']},rmssd:{data['rmssd']},sns:{data.get('sns', 0.0)},pns:{data.get('pns', 0.0)}\n"
            with open(self.filename, "a") as f:
                f.write(line)
        except Exception as e:
            print("Error saving to history:", e)

    def load_all(self):
        records = []
        try:
            with open(self.filename, "r") as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split("|")
                    if len(parts) == 2:
                        timestamp = parts[0]
                        values = parts[1].split(",")
                        record = {"timestamp": timestamp}
                        for v in values:
                            k, val = v.split(":")
                            record[k.strip()] = val.strip()
                        records.append(record)
        except Exception as e:
            print("Error loading history:", e)
        return records



