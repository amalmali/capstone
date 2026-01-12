# gps_reader.py

import serial
import pynmea2

class GPSReader:
    def __init__(self, port, baud_rate):
        self.ser = serial.Serial(port, baud_rate, timeout=1)

    def read_point(self):
        """Return latitude and longitude from GPS."""
        while True:
            line = self.ser.readline().decode("ascii", errors="replace")
            if line.startswith("$GPGGA") or line.startswith("$GPRMC"):
                try:
                    msg = pynmea2.parse(line)
                    if msg.latitude and msg.longitude:
                        return msg.latitude, msg.longitude
                except pynmea2.ParseError:
                    continue

    def close(self):
        self.ser.close()
