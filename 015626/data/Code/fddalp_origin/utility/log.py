import logging,sys,os

class VoidLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass


def add_file_logger(name, level=None, file_name=None, mode='a',
                    format_str ='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    lazy_mode=False, void=False):
    if void:  # multiprocessing dummy
        return VoidLogger()
    logger = logging.getLogger(name)
    if lazy_mode:
        return logger
    if level is not None:
        logger.setLevel(level)
    else:
        if not logger.hasHandlers():
            logger.setLevel(logging.DEBUG)
    if file_name is not None:
        _dirname = os.path.dirname(file_name)
        if len(_dirname) != 0 and not os.path.exists(_dirname):
            os.makedirs(_dirname)
        file_handler = logging.FileHandler(file_name, mode=mode)
        file_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(file_handler)
    else:
        if not logger.hasHandlers():
            # defaults to screen
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(logging.Formatter(format_str))
            logger.addHandler(stream_handler)
    return logger


#logger = add_file_logger('CustomDescriptor', level=logging.DEBUG,
#                         file_name=os.path.join('W:/zhangf', 'CustomDescriptor.log'))
#logger.warning('Calculating Factor: %s - %s' % (20180101, 20190101))