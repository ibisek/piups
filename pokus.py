
import sys
import argparse


def showBatteryVoltage():
    print("BATTERY VOLTAGE")


def showIfOnBattery():
    print("on battery? nevim :P");


def showVersion():
    print("showVersion()")


def showTimeOnBattery():
    print("showTimeOnBattery()")


def doShutdown(timeout=None):
    print("doShutdown(%s)" % timeout)


def parseArguments():
    if len(sys.argv) > 1:
        cmd = str(sys.argv[1]).lower()
        if cmd == 'batt':
            showBatteryVoltage()
        elif cmd == 'onbatt':
            showIfOnBattery()
        elif cmd == 'ver':
            showVersion()
        elif cmd == 'time':
            showTimeOnBattery()
        elif cmd == 'halt':
            if len(sys.argv) == 3:
                doShutdown(int(sys.argv[2]))
            else:
                doShutdown()
    else:
        print('## raspiUps ## control script\n usage: pokus.py [batt] [onbatt] [ver] [time] [halt {SS}]')


def parseArguments2():
    parser = argparse.ArgumentParser(description='raspiUPS control script')
    parser.add_argument('-batt', '--batteryVoltage', help='shows battery voltage [V]', action='store_true', required=False)
    parser.add_argument('-onbatt', '--onBattery', help='shows whether we run on battery (1) or on external power (0)', action='store_true', required=False)
    parser.add_argument('-ver', '--version', help='shows UPS version in form of hw.sw', action='store_true', required=False)
    parser.add_argument('-time', '--timeOnBattery', help='shows run time on battery or 0 if powered from external source', action='store_true', required=False)
    parser.add_argument('-halt', '--shutdown', help='initiate UPS shutdown in defined time (default 30s)', action='append_const', dest='shutdown', const='30')

    args = parser.parse_args()
    # args = parser.parse_args(['-halt', '20'])
    # args = parser.parse_args(['-batt'])
    # args = parser.parse_args(['-onbatt'])
    print(args)

    if args.batteryVoltage:
        showBatteryVoltage()

    elif args.onBattery:
        showIfOnBattery()

    elif args.version:
        showVersion()

    elif args.timeOnBattery:
        showTimeOnBattery()

    elif args.shutdown:
        doShutdown()

    else:
        parser.print_help()


if __name__ == "__main__":
    # parseArguments2()
    parseArguments()
