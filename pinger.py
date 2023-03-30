from icmplib import ICMPv6Socket, ICMPv4Socket, ICMPRequest, is_ipv6_address, TimeoutExceeded, ICMPLibError, ICMPError
from time import sleep
import csv
from datetime import datetime


def ping_log(address, count=4, interval=1, timeout=2):
    # A payload of 56 bytes is used by default. You can modify it using
    # the 'payload_size' parameter of your ICMP request.

    # We detect the socket to use from the specified IP address
    if is_ipv6_address(address):
        sock = ICMPv6Socket(privileged=False)
    else:
        sock = ICMPv4Socket(privileged=False)

    logfile = open("pinglog.csv", mode="a")
    logfile_writer = csv.writer(logfile)

    for sequence in range(count):
        # We create an ICMP request
        request = ICMPRequest(
            destination=address,
            id=1,
            sequence=sequence)

        try:
            # We send the request
            sock.send(request)

            # We are awaiting receipt of an ICMP reply
            reply = sock.receive(request, timeout)

            # We received a reply
            # We display some information
            print(f'  {reply.bytes_received} bytes from '
                  f'{reply.source}: ', end='')

            # We throw an exception if it is an ICMP error message
            reply.raise_for_status()

            # We calculate the round-trip time and we display it
            round_trip_time = (reply.time - request.time) * 1000

            print(f'icmp_seq={sequence} '
                  f'time={round(round_trip_time, 3)} ms')

            # Write to log file
            logfile_writer.writerow([datetime.now(), "Ok", round(round_trip_time, 3)])
            
            # We wait before continuing
            if sequence < count - 1:
                sleep(interval)

        except TimeoutExceeded:
            # The timeout has been reached
            print(f'  Request timeout for icmp_seq {sequence}')
            # Write to log file
            logfile_writer.writerow([datetime.now(), "Timeout", 0])

        except ICMPError as err:
            # An ICMP error message has been received
            print(err)

        except ICMPLibError:
            # All other errors
            print('  An error has occurred.')
        finally:
            logfile.flush()
    logfile.close()


ping_log("8.8.8.8", count=50)