# this file will be launched first when the package (__main__.py) starts executing

# does not import any relative modules, just calls pygame.init() to prepare video system to be used in constants.py
# (it will be able to obtain a display size)

__all__ = ()

import pygame

pygame.init()
# call pygame.mixer.init() here if there are sounds in the app
