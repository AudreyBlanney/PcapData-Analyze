#!/usr/bin/python
import os,logging, logging.handlers

LOG_FILENAME = '/home/bai/assets/log/debug.log'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1024, backupCount=8)

logger.addHandler(handler)
