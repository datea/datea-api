#!/bin/bash

cd "${0%/*}"
cd ../../../

./manage.py build_solr_schema --configure-directory "../solr-6.6.3/server/solr/tester/conf" --reload-core true
