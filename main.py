from hotClaimer.hotClaimer import HotClaimer
import logging
import time
import argparse
import glob
import re
import os
import random


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.WARNING,  # Set the logging level
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',  # Date format
                        handlers=[logging.StreamHandler()])  # Log to the console

    parser = argparse.ArgumentParser(description="CLI tool to claim hot token in telegram")
    parser.add_argument("-a", "--add", type=int, required=False, help="specify the number of accounts to add")
    args = parser.parse_args()

    sessions_dir = 'sessions'
    if args.add:
        # Log into new accounts
        for i in range(args.add):
            list_of_files = glob.glob(f'{sessions_dir}/*.pkl')
            if len(list_of_files) == 0:
                number = 1
            else:
                latest_file = max(list_of_files, key=os.path.getmtime)
                regex = re.compile("ac([0-9]*)")
                number = int(regex.findall(latest_file)[0]) + 1
            acc = HotClaimer("ac" + str(number), sessions_dir)
            acc.close()
    else:
        # Claim on all accounts in sessions folder
        list_of_files = glob.glob(f'{sessions_dir}/*.pkl')
        for filename in list_of_files:
            regex = re.compile("(ac[0-9]*)")
            account = regex.findall(filename)[0]
            acc = HotClaimer(account, sessions_dir)
            try:
                acc.claim()
            except Exception as E:
                logger.critical(f"Failed to claim on {account}: {str(E)}")
                acc.close()
                continue
            time.sleep(random.randint(5, 10))
            acc.close()


if __name__ == '__main__':
    main()
