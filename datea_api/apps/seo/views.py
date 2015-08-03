# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.text import Truncator
from django.utils.html import strip_tags
import os

from datea_api.apps.account.models import User
from datea_api.apps.tag.models import Tag
from datea_api.apps.dateo.models import Dateo
from datea_api.apps.campaign.models import Campaign

app_url = 'http://datea.pe'
api_img_url = 'http://api.datea.io'

default_meta = {
	'title': 'Datea - Todos somos dateros',
	'description': 'Comparte y visualiza datos útiles con tu comunidad.',
	'image_url' : app_url+'/static/images/logo-large.png',
	'url': 'http://datea.pe'
}

def default(request):
	return render_to_response('seo/seo-base.html', default_meta, context_instance=RequestContext(request))

def signin(request):
	ctx = default_meta.copy()
	ctx.update({
		'title': "Datea | Ingresa", 
		'description': "Ingresa a tu cuenta en Datea."
	})
	return render_to_response('seo/seo-base.html', ctx, context_instance=RequestContext(request))

def acerca(request):
	ctx = default_meta.copy()
	ctx.update({
		'title': "Datea | Ingresa", 
		'description': "Ingresa a tu cuenta en Datea.",
		'url': app_url+'/acerca'
	})
	return render_to_response('seo/acerca.html', ctx, context_instance=RequestContext(request))

def home(request):
	ctx = default_meta.copy()
	return render_to_response('seo/seo-base.html', ctx, context_instance=RequestContext(request))

def tag_detail(request, tag):
	tag = Tag.objects.get(tag=tag)
	ctx = default_meta.copy()
	ctx.update({
		'title': 'Datea | dateos en #'+tag.tag, 
		'description': "Visualiza dateos con el hashtag #"+tag.tag+" en Datea.",
		'url': app_url+'/tag/'+tag.tag
	})
	return render_to_response('seo/seo-base.html', ctx, context_instance=RequestContext(request))

def dateo_detail(request, username, dateo_id):
	dateo = Dateo.objects.get(pk=dateo_id)
	ctx = default_meta.copy()
	ctx.update({
		'title': dateo.user.username+u' dateó en #'+ ', #'.join([tag.tag for tag in dateo.tags.all()]), 
		'description': Truncator( strip_tags(dateo.content) ).chars(140).replace("\n",' '),
		'url': app_url+'/'+dateo.user.username+'/dateos/'+str(dateo.id)
	})
	if dateo.images.count() > 0:
		ctx['image_url'] = api_img_url + dateo.images.all()[0].get_thumb('image_thumb_large')

	ctx['dateo'] = dateo

	return render_to_response('seo/dateo.html', ctx, context_instance=RequestContext(request))


def dateo_detail2(request, mapeo_id, dateo_id):
	dateo = Dateo.objects.get(pk=dateo_id)
	ctx = default_meta.copy()
	ctx.update({
		'title': dateo.user.username+u' dateó en #'+ ', #'.join([tag.tag for tag in dateo.tags.all()]), 
		'description': Truncator( strip_tags(dateo.content) ).chars(140).replace("\n",' '),
		'url': app_url+'/'+dateo.user.username+'/dateos/'+str(dateo.id)
	})
	if dateo.images.count() > 0:
		ctx['image_url'] = api_img_url + dateo.images.all()[0].get_thumb('image_thumb_large')

	ctx['dateo'] = dateo

	return render_to_response('seo/dateo.html', ctx, context_instance=RequestContext(request))


def dateo_by_id(request, dateo_id):
	dateo = Dateo.objects.get(pk=dateo_id)
	ctx = default_meta.copy()
	ctx.update({
		'title': dateo.user.username+u' dateó en #'+ ', #'.join([tag.tag for tag in dateo.tags.all()]), 
		'description': Truncator( strip_tags(dateo.content) ).chars(140).replace("\n",' '),
		'url': app_url + '/' + dateo.user.username+'/dateos/'+str(dateo.id)
	})
	if dateo.images.count() > 0:
		ctx['image_url'] = api_img_url + dateo.images.all()[0].get_thumb('image_thumb_large')

	ctx['dateo'] = dateo

	return render_to_response('seo/dateo.html', ctx, context_instance=RequestContext(request))


def campaign_detail(request, username, slug):
	try:
		campaign = Campaign.objects.get(user__username=username, slug=slug)
		ctx = default_meta.copy()
		ctx.update({
			'title': '#'+campaign.main_tag.tag+', '+campaign.name + ' | Datea', 
			'description': campaign.short_description,
			'url': app_url+'/'+campaign.user.username+'/'+campaign.slug
		})
		if campaign.image:
			ctx['image_url'] = api_img_url + campaign.image.get_thumb('image_thumb_large')

		ctx['campaign'] = campaign

		return render_to_response('seo/campaign.html', ctx, context_instance=RequestContext(request))
	except:
		return default(request)

def campaign_by_id(request, campaign_id):
	campaign = Campaign.objects.get(pk=campaign_id)
	ctx = default_meta.copy()
	ctx.update({
		'title': campaign.name + ' | Datea', 
		'description': campaign.short_description,
		'url': app_url + '/' + campaign.user.username+'/'+campaign.slug
	})
	if campaign.image:
		ctx['image_url'] = api_img_url + campaign.image.get_thumb('image_thumb_large')

	ctx['campaign'] = campaign

	return render_to_response('seo/campaign.html', ctx, context_instance=RequestContext(request))

def profile_detail(request, username):
	try:
		user = User.objects.get(username=username)
		ctx = default_meta.copy()
		ctx.update({
			'title' : "Perfil datero de "+user.username,
			'description' : 'Chequea los dateos e iniciativas de '+user.username+ ' en Datea.',
			'url': app_url + '/' + user.username
		})
		if user.image:
			ctx['image_url'] = api_img_url + user.image.get_thumb('profile_image_large')

		ctx['user'] = user

		return render_to_response('seo/profile.html', ctx, context_instance=RequestContext(request))
	except:
		return default(request)




