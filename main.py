#!/usr/bin/env python3


# A NTP server that work not normally
# It gitter a lot
# 1 second NTP time is 1 hour in real


from socket import socket, AF_INET, SOCK_DGRAM
from time import sleep, time
from datetime import datetime, timedelta, timezone
import struct
from threading import Thread

class NtpServer:
    def __init__(
        self,
        port: int = 123,
        slowdown_factor: int = 3600,
        tai_time_start : int = datetime(2025, 4, 16, tzinfo=timezone.utc).timestamp()
    ) :
        self.__enable = False
        self.__port = port
        self.__slowdown_factor = slowdown_factor
        self.__tai_time_start = tai_time_start
        self.__thd : Thread = None

    def start(self):
        self.__enable = True
        self.__thd = Thread(target=self.__run)
        self.__thd.start()
    
    def stop(self):
        self.__enable = False
        self.__thd.join()

    def __run(self):
        def __build_response(ntp_time: int):
            # NTP packet structure
            # LI, VN, Mode, Stratum, Poll, Precision
            # Root Delay, Root Dispersion, Reference ID
            # Reference Timestamp, Originate Timestamp
            # Receive Timestamp, Transmit Timestamp

            packet = bytearray(48)
            packet[0] = 0b00100100                                  # LI = 0, VN = 4, Mode = 3
            packet[1] = 1                                           # Stratum = 1
            packet[2] = 4                                           # Poll = 4
            packet[3] = 0xFA                                        # Precision = -6
            packet[4:8] = struct.pack("!I", 0)                      # Root Delay
            packet[8:12] = struct.pack("!I", 0)                     # Root Dispersion
            packet[12:16] = struct.pack("!I", 0)                    # Reference ID

                                                                    # Timestamps (NTP format - secondes since 1900)
            packet[16:24] = struct.pack("!Q", (ntp_time << 32))     # Reference Timestamp
            packet[24:32] = struct.pack("!Q", (ntp_time << 32))     # Originate Timestamp
            packet[32:40] = struct.pack("!Q", (ntp_time << 32))     # Receive Timestamp
            packet[40:48] = struct.pack("!Q", (ntp_time << 32))     # Transmit Timestamp

            return bytes(packet)
        
        def __get_ntp_time():
            reference_time = datetime(1900, 1, 1, tzinfo=timezone.utc)
            tai_now = datetime.now(timezone.utc).timestamp()

            elapsed_time = tai_now - self.__tai_time_start
            # Slow down the time by the slowdown factor
            slowed_time = elapsed_time / self.__slowdown_factor

            # Calculate the new NTP time
            ntp_time = self.__tai_time_start + slowed_time

            ntp_time = int(ntp_time - reference_time.timestamp())

            return ntp_time


        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(("", self.__port))
        while self.__enable:
            try:
                data, addr = sock.recvfrom(1024)
                ntp_time = __get_ntp_time()
                response = __build_response(ntp_time)
                sock.sendto(response, addr)
            except Exception as e:
                print(f"Error: {e}")
        sock.close()

if __name__ == "__main__":
    try:
        server = NtpServer()
        server.start()
        print("NTP Server started")
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Stopping NTP Server...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.stop()
        print("NTP Server stopped")
        
