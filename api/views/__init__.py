import os
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue

    __import__(f'app.quickstart.views.{module[:-3]}', locals(), globals())

del module
