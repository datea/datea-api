#!/bin/bash

../../../manage.py build_solr_schema > schema.xml
cp schema.xml ../../../../solr-4.7.1/example/solr/collection1/conf/
echo "OK"
