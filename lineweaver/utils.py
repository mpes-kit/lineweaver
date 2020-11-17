#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


def cvfloat(input):
    """ Convert to float while ignoring None.
    """

    if input is None:
        return None
    else:
        return float(input)