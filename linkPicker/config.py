import os
import sys


ICONS_PATH = os.path.join(os.path.dirname(__file__), 'icons')
if not os.path.isdir(ICONS_PATH):
    raise FileNotFoundError(f"The icons directory does not exist: '{ICONS_PATH}'")


alignHorizontallyIcon = os.path.join(ICONS_PATH, 'alignHorizontallyIcon.png')
alignVerticallyIcon   = os.path.join(ICONS_PATH, 'alignVerticallyIcon.png')
pythonLogo            = os.path.join(ICONS_PATH, 'pythonLogo2.png')
mirrorIcon            = os.path.join(ICONS_PATH, 'mirrorIcon.png')
blackCursorIcon       = os.path.join(ICONS_PATH, 'blackCursor.png')
greenCursorIcon       = os.path.join(ICONS_PATH, 'greenCursor.png')