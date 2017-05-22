from django.core.management.base import BaseCommand, CommandError
import json
from tag.models import Tag
from account.models import User
from campaign.models import Campaign
from dateo.models import Dateo
from link.models import Link
from django.contrib.gis.geos import Point

class Command(BaseCommand):

  def handle(self, *args, **options) :

    # main tag, user
    mt = Tag.objects.get_or_create(tag="Neo")[0]
    user = User.objects.filter(email="rodrigoderteano@gmail.com")[0]
    print "USER: ", user

    # crear tags
    tagNames = ['SaludYBienestar', 'DefensaDeDerechos', 'MejorEmpleabilidad', 'ParticipacionCiudadana', 'EducacionSuperiorTecnica']
    tags = {}
    for tname in tagNames:
      tags[tname] = Tag.objects.get_or_create(tag=tname)[0]

    # crear campaign

    #c = Campaign()
    #c.user = user
    #c.main_tag = mt
    #c.name = "Neo test"
    #c.short_description = "un test de neo"
    #c.long_description = "test de neo"
    #c.mission = "mission aqui"
    #c.information_destiny = "uso publico"
    #c.client_domain = "datea.pe"
    #c.save()
    #c.secondary_tags.add(*tags.values())
    #c.save()
    c = Campaign.objects.filter(name="Neo test")[0]

    # crear dateos
    # 1. importar data
    f = open('./datea_api/apps/api/management/commands/organizaciones.json')
    sdata = f.read()
    f.close()

    dateoData = json.loads(sdata);

    for dData in dateoData:
      d = Dateo()
      d.user = user
      d.published = True
      d.content = dData['content']
      d.client_domain = 'datea.pe'
      if dData['link'] and dData['link']['url']:
        d.link = Link.objects.get_or_create(title=dData['name'], url=dData['link']['url'], user=user)[0]
      d.position = Point(dData['position']['x'], dData['position']['y'])
      d.address = dData['address'][:255]
      d.campaign = c
      d.country = 'Peru'
      d.save()
      d.tags.add(mt)
      d.tags.add(tags[dData['tags'].replace('#', '')])
      d.save()
      print d
