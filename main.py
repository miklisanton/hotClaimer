from hotClaimer.hotClaimer import HotClaimer
import logging
import argparse
import glob
import re
import os
import time


def add_accounts(number, sessions_dir):
    for i in range(number):
        list_of_files = glob.glob(f'{sessions_dir}/*.pkl')
        if len(list_of_files) == 0:
            number = 1
        else:
            latest_file = max(list_of_files, key=os.path.getmtime)
            regex = re.compile("ac([0-9]*)")
            number = int(regex.findall(latest_file)[0]) + 1
        acc = HotClaimer("ac" + str(number), sessions_dir)
        acc.close()


def multiple_claim(sessions_dir, logger, retry=3):
    list_of_files = glob.glob(f'{sessions_dir}/*.pkl')
    for filename in list_of_files:
        regex = re.compile("(ac[0-9]*)")
        account = regex.findall(filename)[0]
        claimed = False
        for i in range(retry):
            acc = None
            try:
                acc = HotClaimer(account, sessions_dir)
                acc.claim()
                logger.warning(f'Claimed hot for {account}')
                claimed = True
                break
            except Exception as E:
                logger.critical(
                        f"Failed to claim on {account}, retrying: {str(E)}")
            finally:
                if acc:
                    acc.close()

        if not claimed:
            logger.critical(
                    f"Failed to claim on {account} after {retry} retries")


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.WARNING,  # Set the logging level
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.StreamHandler()])

    parser = argparse.ArgumentParser(
            description="CLI tool to claim hot token in telegram")
    parser.add_argument("-a",
                        "--add",
                        type=int,
                        required=False,
                        help="specify the number of accounts to add")
    parser.add_argument("-s",
                        "--sessions",
                        type=str,
                        default="sessions",
                        help="specify directory to store sessions")
    args = parser.parse_args()

    sessions_dir = args.sessions
    if args.add:
        # Log into new accounts
        add_accounts(args.add, sessions_dir)
    else:
        # Claim on all accounts in sessions folder
        multiple_claim(sessions_dir, logger)


if __name__ == '__main__':
    main()
