#!/usr/bin/env python
import os
import sys
# from settings.base import CODE_ROOT
import settings.base


sys.path.insert(0, os.path.join(settings.base.CODE_ROOT, 'apps'))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
