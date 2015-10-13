Datea
=====

Django based backend for Datea.

Datea is a corwdsourcing and civic engagement platform to create and visualize citizen reports (dateos) in maps, picture galleries, timelines and charts. It's mail goal is to allow citizens to share and visualize useful information for any purpose. It's flexibel, hashtag based structure allows anyone to create a map, timeline or gallery just by creating a report (dateo) using a hashtag. Furthermore, report iniciatives can be created by organizations such as NGOs, local governments and activists, which allow them to campaign for certain issues in order to obtain useful information from citizens (dateros).

If you are interested in using or contributing to this project, or want to know a litle bit more about us or the plattform, please feel free to contact us at contacto@datea.pe or via gitter (datea-gitter channel). For special a deployment or new feature, we also provide commercial support.

##Datea Api

This repo contains the server backend with all the endpoints necessary for the client apps (see other repos). It's based upong a bundle of tools and services, which makes it powerful, but complex to replicate and install. That's why we'd rather recommend using the existing API at https://api.datea.io/api/v2/ (read about the endpoints in the doc dir)

##Installation

1. Service dependencies 
Datea needs the following services: django, postgres 2.x with postgis, memcached, rabbitmq, apache solr 4.x.
On a production environment, Datea will run with gunicorn and a server like nginx.

On a Debian/Ubuntu machine it means something like: apt-get install postgresql-server postgresql-client postgis memcached rabbitmq python-pip

2. clone this repo:
  git clone https://github.com/datea/datea-api.git
  
3. Create python environment and install dependencies
  - If you don't have virtualenv installed: pip install virtualenv
  - virtualenv --no-site-packages env
  - source env/bin/activate
  - cd datea-api
  - pip install -r datea_api/requirements/requirements.txt
  
4. Configure DB with postgresql
  - create a db: createdb datea
  - activate postgis: 
    - psql datea
    - create extension postgis;
  - cd datea_api
  - create local settings: cp local_settings_template.py local_settings.py
  - edit your local_settings.py and add your DB configurations (and other stuff). You can override other things from settings.py there if you like.

5. Sync DB
  - in root dir of repo: python manage.py migrate

6. Configure search engine with apache solr
  - download the latest 4.x version: cd somewhere; wget http://apache.xfree.com.ar/lucene/solr/4.10.4/solr-4.10.4.tgz
  - oh and for this you'll need java! Install Java Runtime Environment (JRE) version 1.7 or higher
  - tar xzf solr-4.10.4.tgz
  - copy datea's schema into solr: cp <path to datea>/datea_api/requirements/solr/schema.xml  solr-4.10.4/example/solr/collection1/conf/
  - run solr: cd solr-4.10.4/example/; java -jar start.jar

7. Run memcached:
  - if not being run by the system already, open a terminal an run: memcached

8. Run dev server in other terminal:
  - cd <path to datea root>
  - python manage.py runserver

9. Run rabbitmq (messaging system used by celery to queue tasks):
  - As with memcached, if this service is not being run already, run: rabbitmq-server (this may require special priviledges)

9. Run async tasks with celery (in new terminal)
 - cd <path to datea> 
 - ../env/bin/celery -A datea_api worker -l info

That should be it for a dev environment. If anything pops up, contact us on the datea-gitter channel or at contacto@datea.pe. There's a lot we probably didn't cover in this brief introduction. If you plan to develop or use this repo, help us make a better documentation.

## Endpoints
This service is already running at https://api.datea.io. We encourage you to use it instead of having your own, and help us make it better. Take a look at the individual endpoints documentation in the doc folder.

## License
GNU AFFERO PUBLIC LICENSE, see attached LICENSE file for details

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
