"""Module with translation functions."""
import gettext
import os

l10n_path = os.path.join(os.path.dirname(__file__), 'translation')

supported_languages = ['en', 'ru']

translations = dict()
for language in supported_languages:
    translations[language] = gettext.translation('l10n',
                                                 l10n_path,
                                                 fallback=True,
                                                 languages=[language])


def _(text, lang):
    """Translate text to some language."""
    return translations[lang].gettext(text)
