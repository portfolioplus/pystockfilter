# -*- coding: utf-8 -*-
""" pystockfilter

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging
import os


class BaseHelper:
    """
    Helper class for logging and config parsing
    """

    @staticmethod
    def get_timezone():
        """
        Return configured timezone or europe berlin as default
        :return:
        """
        from pytz import timezone
        from os import environ
        if environ.get('TZ') is not None:
            return timezone(os.environ['TZ'])
        return timezone('Europe/Berlin')

    @staticmethod
    def setup_logger(name: str):
        """
        Setup the autotrader standard logger
        :param name: name of logger
        :return: instance of logger
        """
        logger = logging.getLogger(name)
        log_formatter = logging.Formatter(
            "%(asctime)s [%(filename)s:%(lineno)s - %(funcName)20s()]"
            " [%(levelname)-5.5s] %(message)s"
            )
        file_handler = logging.FileHandler(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         "..", "%s_broker.log" % name), mode='w')
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        logger.debug("Logging Setup successful")
        return logger
