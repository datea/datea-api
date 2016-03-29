#!/usr/bin/python
from subprocess import Popen
from os.path import join as joinPath

solrDir = '/Users/rod/datea/solr-4.10.4'
run = True

mc   = Popen('memcached')
rmq  = Popen('rabbitmq-server')
solr = Popen(['java','-jar','start.jar'], cwd=joinPath(solrDir, 'example'))
#clry = Popen(['env/bin/celery -A datea_api worker -l info &

while run:
  if raw_input("Type q to quit: ") == 'q':
    run = False
    mc.kill()
    rmq.kill()
    solr.kill()	
