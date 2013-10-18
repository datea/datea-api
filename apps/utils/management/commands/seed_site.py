# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print "Running ..."
        site = Site(name="datea", domain="datea.pe")
        site.save()
        print "Done."
