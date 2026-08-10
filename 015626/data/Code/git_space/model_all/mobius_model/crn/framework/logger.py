import logging


class Logger(object):
    def __init__(self, file_path, save_info, show_info):
        self.logger = logging.getLogger(name=file_path)
        self.formatter = logging.Formatter(fmt='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.logger.setLevel(logging.INFO)
        self.logger.handlers = []
        if save_info:
            fh = logging.FileHandler(file_path, mode='w')
            fh.setLevel(logging.INFO)
            fh.setFormatter(self.formatter)
            self.logger.addHandler(fh)
        if show_info:
            sh = logging.StreamHandler()
            sh.setLevel(logging.INFO)
            sh.setFormatter(self.formatter)
            self.logger.addHandler(sh)

    def print(self, text):
        self.logger.info(text)
        return None
