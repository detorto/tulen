#!/usr/bin/python
# -*- coding: utf-8 -*-


#import vk

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

def process(config, testmode):
    
    def update_stat(stat, value):
        
        stats_file_path = config.get("stats_file", "statistics.yaml");
        
        try:
            f = yaml.load(open(stats_file_path))
        except:
            f = None
        
        
        if f:
            upd = f.get(stat, 0)
            upd += value;   
            f[stat] = upd
        else:
            f = {stat:1}
        
        with io.open(stats_file_path, 'w', encoding='utf-8') as fo:
            fo.write(unicode(yaml.dump(f)))
        



    print "Creating user api... "
    vkuser = VkUser(config, update_stat, testmode)

    print "Starting processing... "
    while True:
        try:
            vkuser.process_all_messages()
        except:
            print "Something wrong while processin dialogs [{}]"
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            if testmode:
                raise


def main():
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config",
                        help="configuration file to use", default="access.yaml", metavar="FILE.yaml")
    parser.add_option("-t", "--test", dest="testmode",
                        help="test mode", action="store_true", default=False)


    (options, args) = parser.parse_args()
    print "*************Tulen vk.com bot****************"

    config = yaml.load(open(options.config));

    print "Loaded configuration"
    
    print yaml.dump(config)
    if options.testmode:
        print "TEST MODE"
    process(config, options.testmode)
    
if __name__ == '__main__':
    main()

