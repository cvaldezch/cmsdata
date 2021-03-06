#!/usr/bin/env python

import json
import time, urllib2
from bs4 import BeautifulSoup

from django.views.generic import View
from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

from cmsdata.apps.home import forms

from cmsdata.apps.home.models import *


class JSONResponseMixin(object):
    def render_to_json_response(self, context, **response_kwargs):
        return HttpResponse(
            self.convert_context_to_json(context),
            content_type='application/json',
            mimetype='application/json',
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        return simplejson.dumps(context, encoding='utf-8')

class JSONDescription_Materials(View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            name = Materials.objects.values('matname').filter(matname__icontains=request.GET.get('description')).distinct('matname').order_by('matname')
            context['mats'] = [{'name': x['matname']} for x in name]
            context['status'] = True
        except ObjectDoesNotExist:
            context['status'] = False
        return HttpResponse(simplejson.dumps(context), mimetype='application/json')

class JSONMeter_Materials(View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            meter = Materials.objects.values('matmet').filter(matname__icontains=request.GET['description']).distinct('matmet').order_by('matmet')
            context['meter'] = [{'meter': x['matmet']} for x in meter]
            context['status'] = True
        except ObjectDoesNotExist:
            context['status'] = False
        return HttpResponse(simplejson.dumps(context), mimetype='application/json')

class JSONSummary_Materials(View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            summ = Materials.objects.filter(matname__icontains=request.GET.get('description'), matmet__icontains=request.GET.get('meter'))[:1]
            context['mats'] = [{'materiales_id': x.materiales_id, 'matname': x.matname, 'matmet': x.matmet, 'unit': x.unit_id} for x in summ]
            context['status'] = True
        except ObjectDoesNotExist:
            context['status'] = False
        return HttpResponse(simplejson.dumps(context), mimetype='application/json')

class JSONCode_Materials(View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            summ = Materials.objects.get(pk__exact=request.GET.get('code'))
            context['mats'] = {'materiales_id': summ.materiales_id, 'matname': summ.matname, 'matmet': summ.matmet, 'unit': summ.unit_id}
            context['status'] = True
        except ObjectDoesNotExist:
            context['status'] = False
        return HttpResponse(simplejson.dumps(context), mimetype='application/json')

class JSONSave_DocumentInDetails(View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            response = HttpResponse()
            response['content_type'] = 'application/json'
            response['mimetype'] = 'application/json'
            context = {}
            try:
                # search materials exists
                counter = DetDocumentIn.objects.filter(entry_id__exact=request.POST.get('entry'), materials_id=request.POST.get('materials')).aggregate(counter=Count('materials'))
                if counter['counter'] > 0:
                    qu = DetDocumentIn.objects.get(entry_id__exact=request.POST.get('entry'), materials_id=request.POST.get('materials'))
                    quantity = qu.quantity
                    form = forms.addDocumentInDetailsForm(request.POST, instance=qu)
                    if form.is_valid():
                        add = form.save(commit=False)
                        add.quantity = (quantity + add.quantity)
                        add.save()
                        context['status'] = True
                    else:
                        context['status'] = False
                else:
                    form = forms.addDocumentInDetailsForm(request.POST)
                    if form.is_valid():
                        form.save()
                        context['status'] = True
                    else:
                        context['status'] = False
            except ObjectDoesNotExist:
                context['status'] = False
            response.write(simplejson.dumps(context))
            return response

class JSONEdit_DocumentEntryDetails(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            context = {}
            try:
                # Recover object to edit
                obj = DetDocumentIn.objects.get(pk=request.POST.get('id'), materials_id=request.POST.get('materials'), serie_id=request.POST.get('serie'))
                obj.quantity = request.POST.get('quantity')
                obj.save()
                context['status'] = True
            except ObjectDoesNotExist:
                context['status'] = False
            return self.render_to_json_response(context, **kwargs)

class JSONDelete_DocumentEntryDetails(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            context = {}
            try:
                obj = DetDocumentIn.objects.get(pk=request.POST.get('id'), materials_id=request.POST.get('materials'), serie_id=request.POST.get('serie'))
                obj.delete()
                context['status'] = True
            except ObjectDoesNotExist:
                context['status'] = False
            return self.render_to_json_response(context, **kwargs)

class JSONFinish_DocumentEntry(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            context = {}
            try:
                obj = DocumentIn.objects.get(pk__exact=request.POST.get('entry'))
                obj.status = 'CO'
                obj.save()
                context['status'] = True
            except Exception, e:
                context['status'] = False
            return self.render_to_json_response(context, **kwargs)

class JSONList_DocumentInDetails(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse()
        response['content_type'] = 'application/json'
        context = {}
        try:
            details = DetDocumentIn.objects.filter(entry_id__exact=request.GET.get('entry')).order_by('materials__matname')
            context['list'] = [{'id': x.id, 'materiales_id': x.materials_id, 'quantity': x.quantity, 'matname': x.materials.matname, 'matmet': x.materials.matmet, 'matunit': x.materials.unit_id} for x in details]
            context['status'] = True
        except ObjectDoesNotExist:
            context['status'] = False
        response.write(simplejson.dumps(context))
        return response

class JSONSave_DocumentOutputDetails(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            context = {}
            try:
                # search materials exists
                counter = DetDocumentOut.objects.filter(serie_id__exact=request.POST.get('serie'), materials_id=request.POST.get('materials')).aggregate(counter=Count('materials'))
                if counter['counter'] > 0:
                    qu = DetDocumentOut.objects.get(serie_id__exact=request.POST.get('serie'), materials_id=request.POST.get('materials'))
                    quantity = qu.quantity
                    form = forms.addDocumentOutDetailsForm(request.POST, instance=qu)
                    if form.is_valid():
                        add = form.save(commit=False)
                        add.quantity = (quantity + add.quantity)
                        add.save()
                        context['status'] = True
                    else:
                        context['status'] = False
                else:
                    form = forms.addDocumentOutDetailsForm(request.POST)
                    if form.is_valid():
                        form.save()
                        context['status'] = True
                    else:
                        context['status'] = False
            except ObjectDoesNotExist:
                context['status'] = False
            return self.render_to_json_response(context, **kwargs)

class JSONEdit_DocumentOutputDetails(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            context = {}
            try:
                # Recover object to edit
                obj = DetDocumentOut.objects.get(pk=request.POST.get('id'), materials_id=request.POST.get('materials'), serie_id=request.POST.get('serie'))
                obj.quantity = request.POST.get('quantity')
                obj.save()
                context['status'] = True
            except ObjectDoesNotExist:
                context['status'] = False
            return self.render_to_json_response(context, **kwargs)

class JSONDelete_DocumentOutputDetails(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            context = {}
            try:
                obj = DetDocumentOut.objects.get(pk=request.POST.get('id'), materials_id=request.POST.get('materials'), serie_id=request.POST.get('serie'))
                obj.delete()
                context['status'] = True
            except ObjectDoesNotExist:
                context['status'] = False
            return self.render_to_json_response(context, **kwargs)

class JSONFinish_DocumentOutput(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            context = {}
            try:
                obj = DocumentOut.objects.get(pk__exact=request.POST.get('serie'))
                obj.status = 'CO'
                obj.save()
                context['status'] = True
            except Exception, e:
                context['status'] = False
            return self.render_to_json_response(context, **kwargs)

class JSONList_DocumentOutputDetails(JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            details = DetDocumentOut.objects.filter(serie_id__exact=request.GET.get('serie')).order_by('materials__matname')
            context['list'] = [{'id': x.id, 'materiales_id': x.materials_id, 'quantity': x.quantity, 'matname': x.materials.matname, 'matmet': x.materials.matmet, 'matunit': x.materials.unit_id} for x in details]
            context['status'] = True
        except ObjectDoesNotExist:
            context['status'] = False
        return self.render_to_json_response(context, **kwargs)


class JsonSunatData(View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            url = 'http://www.sunat.gob.pe/w/wapS01Alias?ruc=%s'%(request.GET.get('ruc'))
            data = parseSunat(url)
            if data != 'Nothing':
                soup = BeautifulSoup(data)
                for x in soup.find_all('small'):
                    tag = BeautifulSoup(x.__str__())
                    #print tag
                    conditional = tag.body.small.contents[0].string
                    if conditional.endswith('Ruc. '):
                        res = tag.body.small.contents[1]
                        res = res.split('-',1)
                        context['ruc'] = res[0].strip()
                        context['reason'] = res[1].strip()
                    if conditional.startswith('Direcci'):
                        context['address'] = tag.body.small.contents[2].string
                    if conditional.startswith('Tipo.'):
                        context['type'] = tag.body.small.contents[2]
                    if conditional.startswith('Tel'):
                        context['phone'] = tag.body.small.contents[2]
                    if conditional.startswith('DNI'):
                        context['dni'] = tag.body.small.contents[1].string[3:]
                    context['status'] = True
            else:
                context['status'] = False
        except Exception, e:
            contet['status'] = False
        return HttpResponse(simplejson.dumps(context), mimetype="application/json")

def parseSunat(url):
    try:
        req = urllib2.Request(url)
        return urllib2.urlopen(req).read()
    except Exception:
        return "Nothing"