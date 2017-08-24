import xml.etree.ElementTree as etree
import argparse
import glob

VERSION = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tenhou MJLog decoder. Ver %s. By Xdestiny."%(VERSION))
    parser.add_argument("-f", "--folder", help="Log folder")
    parser.add_argument("-r", "--regex", default = "*.mjlog", help="Regex")
    args = parser.parse_args()

    if args.format == None:
        args.format = args.Format
    
    print("Log folder = %s"%(args.folder))
    print("regex = %s"%(args.regex))

    files = glob.glob(args.folder + "/" + args.regex)
    for f in files:
        events = etree.parse(open(f)).getroot()
