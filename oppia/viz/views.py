# oppia/viz/views.py

import datetime
import json
from itertools import izip_longest
from operator import itemgetter
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count, Sum, Q

from django.contrib.auth import (authenticate, logout, views)
from django.contrib.auth.models import User

from oppia.forms import DateDiffForm
from oppia.models import CourseDownload, Tracker, Course, ClientTracker, Section
from oppia.viz.models import UserLocationVisualization


def summary_view(request):
    if not request.user.is_staff:
         raise Http404

    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    if request.method == 'POST':
        form = DateDiffForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")              
    else:
        data = {}
        data['start_date'] = start_date
        form = DateDiffForm(initial=data)
    
    # User registrations
    user_registrations = User.objects.filter(date_joined__gte=start_date).\
                        extra(select={'month':'extract( month from date_joined )',
                                      'year':'extract( year from date_joined )'}).\
                        values('month', 'year').\
                        annotate(count=Count('id')).order_by('year', 'month')
    
    previous_user_registrations = User.objects.filter(date_joined__lt=start_date).count()

    # Unique or Repeated Clients

    clients = ClientTracker.objects.filter(end_time__gte=start_date). \
        extra(select={'month': 'extract( month from end_time )',
                      'year': 'extract( year from end_time )'}). \
        values('client__id', 'month', 'year'). \
        annotate(count=Count('client__id')).order_by('year', 'month')

    previous_clients = ClientTracker.objects.filter(start_time__lt=start_date).count()

    clients_count_dict = {}
    clients_count_list = []
    for client in clients:
        if clients_count_dict.has_key(str(client['year']) + str(client['month'])):
            if client['count'] == 1:
                clients_count_dict[str(client['year']) + str(client['month'])]['unique'] += 1
            else:
                clients_count_dict[str(client['year']) + str(client['month'])]['repeat'] += 1
        else:
            clients_count_dict[str(client['year']) + str(client['month'])] = {}
            clients_count_dict[str(client['year']) + str(client['month'])]['month'] = client['month']
            clients_count_dict[str(client['year']) + str(client['month'])]['year'] = client['year']
            if client['count'] == 1:
                clients_count_dict[str(client['year']) + str(client['month'])]['unique'] = 1
                clients_count_dict[str(client['year']) + str(client['month'])]['repeat'] = 0
            else:
                clients_count_dict[str(client['year']) + str(client['month'])]['repeat'] = 1
                clients_count_dict[str(client['year']) + str(client['month'])]['unique'] = 0
            clients_count_list.append(clients_count_dict[str(client['year']) + str(client['month'])])


    # Countries
    hits_by_country = UserLocationVisualization.objects.all().values('country_code', 'country_name').annotate(country_total_hits=Sum('hits')).order_by('-country_total_hits')
    total_hits = UserLocationVisualization.objects.all().aggregate(total_hits=Sum('hits'))
    total_countries = hits_by_country.count()
    
    i = 0
    country_activity = []
    other_country_activity = 0
    for c in hits_by_country:
        if i < 20:
            hits_percent = float(c['country_total_hits'] * 100.0 / total_hits['total_hits'])
            country_activity.append({'country_code':c['country_code'], 'country_name':c['country_name'], 'hits_percent':hits_percent })
        else:
            other_country_activity += c['country_total_hits']
        i += 1
    if i > 20:
        hits_percent = float(other_country_activity * 100.0 / total_hits['total_hits'])
        country_activity.append({'country_code':None, 'country_name':_('Other'), 'hits_percent':hits_percent })
        
    # Language
    hit_by_language = Tracker.objects.filter(user__is_staff=False).exclude(lang=None).values('lang').annotate(total_hits=Count('id')).order_by('-total_hits')
    total_hits = Tracker.objects.filter(user__is_staff=False).exclude(lang=None).aggregate(total_hits=Count('id'))
    
    i = 0
    languages = []
    other_languages = 0
    for hbl in hit_by_language:
        if i < 10:
            hits_percent = float(hbl['total_hits'] * 100.0 / total_hits['total_hits'])
            languages.append({'lang':hbl['lang'], 'hits_percent':hits_percent })
        else:
            other_languages += hbl['total_hits']
        i += 1
    if i > 10:
        hits_percent = float(other_languages * 100.0 / total_hits['total_hits'])
        languages.append({'lang':_('Other'), 'hits_percent':hits_percent })
        
    # Course Downloads
    course_downloads = CourseDownload.objects.filter(user__is_staff=False, download_date__gte=start_date).\
                        extra(select={'month':'extract( month from download_date )',
                                      'year':'extract( year from download_date )'}).\
                        values('month', 'year').\
                        annotate(count=Count('id')).order_by('year', 'month')
                        
    previous_course_downloads = CourseDownload.objects.filter(user__is_staff=False, download_date__lt=start_date).count()
    
    # Course Activity
    course_activity = Tracker.objects.filter(user__is_staff=False, submitted_date__gte=start_date).\
                        extra(select={'month':'extract( month from submitted_date )',
                                      'year':'extract( year from submitted_date )'}).\
                        values('month', 'year').\
                        annotate(count=Count('id')).order_by('year', 'month')
    
    previous_course_activity = Tracker.objects.filter(user__is_staff=False, submitted_date__lt=start_date).count()
                        
    last_month = datetime.datetime.now() - datetime.timedelta(days=31)
    hit_by_course = Tracker.objects.filter(user__is_staff=False, submitted_date__gte=last_month).exclude(course_id=None).values('course_id').annotate(total_hits=Count('id')).order_by('-total_hits')
    total_hits = Tracker.objects.filter(user__is_staff=False, submitted_date__gte=last_month).exclude(course_id=None).aggregate(total_hits=Count('id'))
    
    i = 0
    hot_courses = []
    other_course_activity = 0
    for hbc in hit_by_course:
        if i < 10:
            hits_percent = float(hbc['total_hits'] * 100.0 / total_hits['total_hits'])
            course = Course.objects.get(id=hbc['course_id'])
            hot_courses.append({'course':course, 'hits_percent':hits_percent })
        else:
            other_course_activity += hbc['total_hits']
        i += 1
    if i > 10:
        hits_percent = float(other_course_activity * 100.0 / total_hits['total_hits'])
        hot_courses.append({'course':_('Other'), 'hits_percent':hits_percent })

    tracker_methods = Tracker.objects.filter(course_id=13, type='page', submitted_date__gte=start_date).\
                        extra(select={'month':'extract( month from submitted_date )',
                                      'year':'extract( year from submitted_date )'}).\
                        values('month', 'year', 'section_title').\
                        annotate(count=Count('id')).annotate(acount=Count('section_title')). \
        order_by('year', 'month', 'section_title')

    tracker_dict = {}
    tracker_list = []

    for meth in tracker_methods:
        sec_title = json.loads(meth['section_title'])
        sec_title = sec_title['en']
        meth['section_title'] = sec_title
        key = str(str(meth['month']) + '-' + str(meth['year']))
        if tracker_dict.has_key(str(meth['month']) + '-' + str(meth['year'])):
            tracker_dict[key].append(meth)
        else:
            tracker_dict[key] = [meth]
            tracker_list.append(tracker_dict[key])
    sections_list = []
    if len(tracker_list) > 0:
        for track in tracker_list[0]:
            sections_list.append(track['section_title'])

    previous_tracker_methods = Tracker.objects.filter(course_id=13, type='page', submitted_date__lte=start_date).count()

    films_activity = Tracker.objects.filter(Q(course_id=13), Q(type='page'),
                                            Q(activity_title__icontains='Doctor Speaks') | 
                                            Q(activity_title__icontains='Real') | 
                                            Q(activity_title__icontains='Entertainment') | 
                                            Q(activity_title__icontains='TV')).values('activity_title', 'section_title').annotate(actCount=Count('activity_title'))
    activity_list = set()
    films_dict = {}
    for film in films_activity:
        act_title = json.loads(film['activity_title'])
        act_title = act_title['en']
        sec_title = json.loads(film['section_title'])
        sec_title = sec_title['en']
        activity_list.add(act_title)
        if films_dict.has_key(sec_title):

            films_dict[sec_title].append([act_title, film['actCount']])
        else:
            films_dict[sec_title] = [[act_title, film['actCount']]]

    sorted_film_dict = {}

    for key, value in films_dict.items():
        temp_act_list = set()
        for val in value:
            activity_list.discard(val[0])
            temp_act_list.add(val[0])
        for val in activity_list:
            value.append([val, 0])
            temp_act_list.add(val)
        activity_list.clear()
        activity_list = temp_act_list
        value = sorted(value, key=itemgetter(0))
        sorted_film_dict[key] = value
        activity_list = sorted(activity_list)
        activity_list = set(activity_list)

    films_completed = Tracker.objects.filter(Q(course_id=13), Q(type='page'),
                                             Q(activity_title__icontains='Doctor Speaks') |
                                             Q(activity_title__icontains='Real') |
                                             Q(activity_title__icontains='Entertainment') |
                                             Q(activity_title__icontains='TV')).order_by('section_title')
    films_completed_dict = {}
    for flim in films_completed:
        sec_title = json.loads(flim.section_title)
        sec_title = sec_title['en']
        if films_completed_dict.has_key(sec_title):
            if flim.completed == 0:
                films_completed_dict[sec_title]['partial'] += 1
            else:
                films_completed_dict[sec_title]['completed'] += 1
        else:
            films_completed_dict[sec_title] = {}
            if flim.completed == 0:
                films_completed_dict[sec_title]['partial'] = 1
                films_completed_dict[sec_title]['completed'] = 0
            else:
                films_completed_dict[sec_title]['partial'] = 0
                films_completed_dict[sec_title]['completed'] = 1
    sorted_sections = sorted(films_completed_dict.keys())
    films_final_list = []
    for f in sorted_sections:
        temp = {}
        temp['section'] = f
        values = films_completed_dict[f]
        temp['partial'] = values['partial']
        temp['completed'] = values['completed']
        films_final_list.append(temp)

    sessions = ClientTracker.objects.all().order_by('user__id')
    sessions_dict = {}
    for session in sessions:
        time_diff = session.end_time - session.start_time
        if sessions_dict.has_key(session.user.id):
            temp = sessions_dict[session.user.id]
            temp['count'] += 1
            temp['time'] += time_diff
            temp['clients'].add(session.client.id)
        else:
            temp_client = set([])
            temp_client.add(session.client.id)
            sessions_dict[session.user.id] = {'user': session.user.username, 'time': time_diff, 'count': 1,
                                              'clients': temp_client}
    for key, value in sessions_dict.items():
        temp = sessions_dict[key]
        temp['time'] /= temp['count']

    return render_to_response('oppia/viz/summary.html',
                              {'form': form,
                               'user_registrations': user_registrations,
                               'previous_user_registrations': previous_user_registrations,
                               'total_countries': total_countries,
                               'country_activity': country_activity,
                               'languages': languages,
                               'course_downloads': course_downloads,
                               'previous_course_downloads': previous_course_downloads,
                               'course_activity': course_activity,
                               'previous_course_activity': previous_course_activity,
                               'hot_courses': hot_courses,
                               'tracker_methods': tracker_list,
                               'sections_list': sections_list,
                               'films_activity': sorted_film_dict,
                               'activity_list': activity_list,
                               'clients_list': clients_count_list,
                               'previous_clients_list': previous_clients,
                               'sessions': sessions_dict,
                               'films_completed': films_final_list},
                              context_instance=RequestContext(request))

def map_view(request):
    return render_to_response('oppia/viz/map.html',
                              context_instance=RequestContext(request))
