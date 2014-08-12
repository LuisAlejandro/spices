#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'standard'
        }
    },
    'loggers': {
        'condiment': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        }
    }
}
