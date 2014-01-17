#!/bin/bash

../../../manage.py build_solr_schema > schema.xml
python fix_solr_schema.py
cp schema.xml ../../../../solr-4.6.0/example/solr/collection1/conf/
echo "OK"
