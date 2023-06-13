DOIT_CONFIG = {"default_tasks": ["html"]}

def task_extract():
    return {
        'actions': [
            'pybabel extract -o ./source/l10n.pot ./source/bot.py',
            ],
        'targets': [
            'l10n.pot',
            ],
        }


def task_update():
    return {
        'actions': [
            'pybabel update -D l10n -d ./source/translation -l en -i ./source/l10n.pot',
            ],
        'task_dep': [
            'extract',
            ],
        }


def task_compile():
    return {
        'actions': [
            'pybabel compile -D l10n -d ./source/translation -l en',
            ],
        'task_dep': [
            'update',
            ],
        'targets': [
            'l10n.mo',
            ],
        }


def task_l10n():
    return {
        'actions': [],
        'task_dep': [
            'compile',
            ],
        }


def task_test():
    return {
        'actions': [
            'python3 source/tests.py',
            ],
        }


def task_html():
    return {
        'actions': [
            'sphinx-build -M html docs/source docs/build',
            ],
        }


def task_runbot():
    return {
        'actions': [
            'python3 source/bot.py',
            ],
        }
