GPS / Real
time

import serial
import pynmea2

# Open the serial port (adjust port as needed)
ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)

print("?? Reading GPS data... Press Ctrl+C to stop.\n")

try:
    while True:
        line = ser.readline().decode('ascii', errors='replace').strip()

        if line.startswith('$'):
            print("RAW:", line)

        try:
            msg = pynmea2.parse(line)

            # Handle GGA sentence (contains altitude and location)
            if isinstance(msg, pynmea2.types.talker.GGA):
                print("?? GGA Sentence (Fix Info):")
                print(f"?? Latitude: {msg.latitude} {msg.lat_dir}")
                print(f"?? Longitude: {msg.longitude} {msg.lon_dir}")
                print(f"? UTC Time: {msg.timestamp}")
                print(f"? Fix Quality: {msg.gps_qual} (1 = GPS fix)")
                print(f"??? Satellites Used: {msg.num_sats}")

                # Altitude
                if msg.altitude:
                    print(f"?? Altitude: {msg.altitude} {msg.altitude_units}")
                else:
                    print("?? Altitude data not available.")

                # Google Maps link
                if msg.latitude and msg.longitude:
                    maps_link = f"https://www.google.com/maps?q={msg.latitude},{msg.longitude}"
                    print(f"?? Google Maps: {maps_link}")

                print("-" * 35)

            # Handle RMC sentence (contains location, speed, date)
            elif isinstance(msg, pynmea2.types.talker.RMC):
                print("?? RMC Sentence (Recommended Minimum Data):")
                print(f"?? Latitude: {msg.latitude} {msg.lat_dir}")
                print(f"?? Longitude: {msg.longitude} {msg.lon_dir}")
                print(f"? UTC Time: {msg.timestamp}")
                print(f"?? Date: {msg.datestamp}")
                print(f"?? Status: {msg.status} (A = Active)")
                print(f"?? Speed: {msg.spd_over_grnd} knots")
                print(f"?? Track Angle: {msg.true_course}")

                # Google Maps link
                if msg.latitude and msg.longitude:
                    maps_link = f"https://www.google.com/maps?q={msg.latitude},{msg.longitude}"
                    print(f"?? Google Maps: {maps_link}")

                print("-" * 35)

        except pynmea2.ParseError as e:
            print("? Parse error:", e)

except KeyboardInterrupt:
    print("?? Program stopped by user.")

finally:
    ser.close()
    print("?? Serial port closed.")


