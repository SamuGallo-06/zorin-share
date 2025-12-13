import gettext
import locale
import os

# Determine the directory of the translations
LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
DOMAIN = 'zorin-share'

# Set system locale
locale.setlocale(locale.LC_ALL, '')

# Set up gettext
try:
    lang = gettext.translation(DOMAIN, LOCALE_DIR, fallback=True)
    lang.install()
    _ = lang.gettext
except:
    # Fallback in case translation files are missing
    print("Warning: Translation files not found. Using default messages.")
    def _(message):
        return message