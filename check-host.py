import sys
import argparse
import datetime
import io
import logging
from src.scripts.methods.http import http_part

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parser_error_trigger(error_info):
	print(datetime.datetime.now().strftime("%H:%M:%S"), "{ error } inf:", error_info)
	sys.exit(1)


def methods_part(args):
    try:
        if args.http:
            logging.debug("HTTP method selected.")
            from src.scripts.methods.http import http_part
            http_part(args)
        else:
            logging.error("No method selected.")
            sys.exit(1)
    except Exception as e:
        logging.exception("An error occurred in methods_part.")
        sys.exit(1)



def arg_parser_part():
	parser = argparse.ArgumentParser()
	parser.error = parser_error_trigger
	parser.add_argument("-t", "--target", required=True)
	parser.add_argument("--http", dest="http", action="store_true")
	return parser.parse_args()


if __name__ == '__main__':
	args = arg_parser_part()
	methods_part(args)