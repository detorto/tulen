#!/usr/bin/python
# -*- coding: utf-8 -*-


# import vk

import urllib2
import requests

import pkgutil
import imp
import os

import threading
import json
import time

from vkuser import VkUser
import sys
import traceback
import io
from optparse import OptionParser
import yaml

import multiline_formatter
import logging

LOG_SETTINGS = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
    },
    'formatters': {
        'default': {
            '()': 'multiline_formatter.formatter.MultilineMessagesFormatter',
            'format': '[%(levelname)s] %(message)s'
        },
    },
    'loggers': {
        'tulen': {
            'level': 'DEBUG',
            'handlers': ['console', ]
        },
    }
}

logging.config.dictConfig(LOG_SETTINGS)
logger = logging.getLogger("tulen")


def process(config, testmode):
    def update_stat(stat, value):
        stats_file_path = config.get("stats_file", "statistics.yaml")

        try:
            f = yaml.load(open(stats_file_path))
        except:
            f = None

        if f:
            upd = f.get(stat, 0)
            upd += value
            f[stat] = upd
        else:
            f = {stat: 1}

        with io.open(stats_file_path, 'w', encoding='utf-8') as fo:
            fo.write(unicode(yaml.dump(f)))
        logger.info("Updated statistic: {} :+{}".format(stat, value))

    vkuser = VkUser(config, update_stat, testmode)
    logger.info("Created user api")
    logger.info("Starting processing... ")
    while True:
        try:
            vkuser.process_all_messages()
        except:
            logger.error("Something wrong while processin dialogs")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error("\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            if testmode:
                raise
            continue


def main():
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config",
                      help="configuration file to use", default="access.yaml", metavar="FILE.yaml")
    parser.add_option("-t", "--test", dest="testmode",
                      help="test mode", action="store_true", default=False)

    (options, args) = parser.parse_args()
    logger.info("*************Tulen vk.com bot****************")

    config = yaml.load(open(options.config))

    logger.info("Loaded configuration ")
    logger.info(yaml.dump(config))

    process(config, options.testmode)


if __name__ == '__main__':
    main()
