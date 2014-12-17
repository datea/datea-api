from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

class Command(BaseCommand):
	help = "clear django's cache"

	def handle(self, *args, **options):
		cache.clear()
		self.stdout.write("cache cleared")	
