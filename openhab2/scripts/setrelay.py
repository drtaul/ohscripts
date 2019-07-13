#!/usr/bin/env python

# there is a relay control card available
# FTDI:FT245R USB FIFO:A7033HHG


from pylibftdi import BitBangDevice, FtdiError
from syslog import syslog
import argparse
import sys

relaytable = { 'lslights' : 0, 'igate' : 1 }
stvalues = { 'ON' : 1, 'OFF' : 0, 'on' : 1, 'off' : 0, '0' : 0, '100' : 1}

def main():
    ap = argparse.ArgumentParser()
    syslog(": %s " % ' '.join(sys.argv))
    ap.add_argument('relayname', type=str, choices=relaytable.keys())
    ap.add_argument('setting', type=str, choices=stvalues.keys())
    args = ap.parse_args()
    relay_bit = relaytable[args.relayname]
    relay_st = stvalues[args.setting]
    rmsg = "FAIL" 
    with BitBangDevice('A7033HHG') as bb:
        bitmask = 1 << relay_bit
        current_bits = bb.port
        current_state = (current_bits & bitmask) >> relay_bit
        if current_state != relay_st:
            wrok = False
            rtrycnt = 0
            if relay_st == 0:
                while not wrok and rtrycnt < 3:
                    try:
                        bb.port = current_bits & ~(bitmask)
                        wrok = True
                        syslog("Set %s to %s" % (args.relayname, "off"))
                        rmsg = "OFF"
                    except FtdiError as error:
                        rtrycnt += 1
                        syslog("Failed to set %s to %s" % (args.relayname, "off"))
            else:
                while not wrok and rtrycnt < 3:
                    try:
                        bb.port = current_bits | bitmask
                        wrok = True
                        syslog("Set %s to %s" % (args.relayname, "on"))
                        rmsg = "ON"
                    except FtdiError as error:
                        rtrycnt += 1
                        syslog("Failed to set %s to %s" % (args.relayname, "on"))
        else:
            rmsg = "ON"
            if relay_st == 0:
                rmsg = "OFF"
    rc = 0
    if rmsg == "FAIL":
        rc = 1
    print rmsg
    return rc

if __name__ == '__main__':
    main()
