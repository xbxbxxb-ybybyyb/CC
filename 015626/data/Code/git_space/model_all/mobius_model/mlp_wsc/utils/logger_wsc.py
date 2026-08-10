import os
import logging


class LoggerMyself:
    logging_level_dict = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }

    def __init__(self, filename, logging_path, level='INFO', fmt='%(levelname)s --- %(asctime)s --- %(message)s',
                 dt_fmt='%Y-%m-%d %H:%M:%S'):
        self.logger = logging.getLogger(filename)
        fmt_str = logging.Formatter(fmt, datefmt=dt_fmt)
        self.logger.setLevel(self.logging_level_dict[level])

        self.sh = logging.StreamHandler()
        self.sh.setFormatter(fmt_str)

        if not os.path.exists(logging_path):
            os.makedirs(logging_path)
        self.fh = logging.FileHandler(os.path.join(logging_path, filename))
        self.fh.setFormatter(fmt_str)

    def set_outputs(self, outputs):
        assert outputs in ['stdout', 'file', 'both']
        self.logger.handlers = list()
        if outputs == 'stdout':
            self.logger.addHandler(self.sh)
        elif outputs == 'file':
            self.logger.addHandler(self.fh)
        else:
            self.logger.addHandler(self.fh)
            self.logger.addHandler(self.sh)

    def info(self, message, outputs='both'):
        self.set_outputs(outputs)
        self.logger.info(message)

    def error(self, message, outputs='both'):
        self.set_outputs(outputs)
        self.logger.error(message)

    def exception(self, message, outputs='both'):
        self.set_outputs(outputs)
        self.logger.exception(message)
