#!/usr/bin/python
from subprocess import Popen
from os.path import join as joinPath

solrDir = '/Users/rod/datea/solr-6.6.3'
run = True

mc   = Popen('memcached')
rmq  = Popen('rabbitmq-server')
solr = Popen(['./bin/solr','start','-f'], cwd=joinPath(solrDir))
#clry = Popen(['env/bin/celery -A datea_api worker -l info &

while run:
  if raw_input("Type q to quit: ") == 'q':
    run = False
    mc.kill()
    rmq.kill()
    solr.kill()
    #clry.kill()
