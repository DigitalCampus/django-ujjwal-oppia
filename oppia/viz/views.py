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
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django.contrib.auth import (authenticate, logout, views)
from django.contrib.auth.models import User

from oppia.forms import DateDiffForm, DateRangeIntervalForm
from oppia.models import Tracker, Course, ClientTracker, Section, Client, Activity
from oppia.viz.models import UserLocationVisualization


def summary_view(request):
    if not request.user.is_staff:
        raise Http404

    start_date = timezone.now()  - datetime.timedelta(days=365)
    if request.method == 'POST':
        form = DateDiffForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
    else:
        data = {}
        data['start_date'] = start_date
        form = DateDiffForm(initial=data)

    # User registrations
    user_registrations = User.objects.filter(date_joined__gte=start_date). \
        extra(select={'month': 'extract( month from date_joined )',
                      'year': 'extract( year from date_joined )'}). \
        values('month', 'year'). \
        annotate(count=Count('id')).order_by('year', 'month')

    previous_user_registrations = User.objects.filter(date_joined__lt=start_date).count()
    #----------------------------------------------------------------------------------------
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
    hits_by_country = UserLocationVisualization.objects.all().values('country_code', 'country_name').annotate(
        country_total_hits=Sum('hits')).order_by('-country_total_hits')
    total_hits = UserLocationVisualization.objects.all().aggregate(total_hits=Sum('hits'))
    total_countries = hits_by_country.count()

    i = 0
    country_activity = []
    other_country_activity = 0
    for c in hits_by_country:
        if i < 20:
            hits_percent = float(c['country_total_hits'] * 100.0 / total_hits['total_hits'])
            country_activity.append(
                {'country_code': c['country_code'], 'country_name': c['country_name'], 'hits_percent': hits_percent})
        else:
            other_country_activity += c['country_total_hits']
        i += 1
    if i > 20:
        hits_percent = float(other_country_activity * 100.0 / total_hits['total_hits'])
        country_activity.append({'country_code': None, 'country_name': _('Other'), 'hits_percent': hits_percent})

    # Language
    hit_by_language = Tracker.objects.filter(user__is_staff=False).exclude(lang=None).values('lang').annotate(
        total_hits=Count('id')).order_by('-total_hits')
    total_hits = Tracker.objects.filter(user__is_staff=False).exclude(lang=None).aggregate(total_hits=Count('id'))

    i = 0
    languages = []
    other_languages = 0
    for hbl in hit_by_language:
        if i < 10:
            hits_percent = float(hbl['total_hits'] * 100.0 / total_hits['total_hits'])
            languages.append({'lang': hbl['lang'], 'hits_percent': hits_percent})
        else:
            other_languages += hbl['total_hits']
        i += 1
    if i > 10:
        hits_percent = float(other_languages * 100.0 / total_hits['total_hits'])
        languages.append({'lang': _('Other'), 'hits_percent': hits_percent})

    # Course Downloads
    course_downloads = Tracker.objects.filter(user__is_staff=False, submitted_date__gte=start_date, type='download' ).\
                        extra(select={'month':'extract( month from submitted_date )',
                                      'year':'extract( year from submitted_date )'}).\
                        values('month','year').\
                        annotate(count=Count('id')).order_by('year','month')
                        
    previous_course_downloads = Tracker.objects.filter(user__is_staff=False, submitted_date__lt=start_date, type='download' ).count()

    # Course Activity
    course_activity = Tracker.objects.filter(user__is_staff=False, submitted_date__gte=start_date). \
        extra(select={'month': 'extract( month from submitted_date )',
                      'year': 'extract( year from submitted_date )'}). \
        values('month', 'year'). \
        annotate(count=Count('id')).order_by('year', 'month')

    previous_course_activity = Tracker.objects.filter(user__is_staff=False, submitted_date__lt=start_date).count()

    last_month = timezone.now() - datetime.timedelta(days=31)
    hit_by_course = Tracker.objects.filter(user__is_staff=False, submitted_date__gte=last_month).exclude(
        course_id=None).values('course_id').annotate(total_hits=Count('id')).order_by('-total_hits')
    total_hits = Tracker.objects.filter(user__is_staff=False, submitted_date__gte=last_month).exclude(
        course_id=None).aggregate(total_hits=Count('id'))

    i = 0
    hot_courses = []
    other_course_activity = 0
    for hbc in hit_by_course:
        if i < 10:
            hits_percent = float(hbc['total_hits'] * 100.0 / total_hits['total_hits'])
            course = Course.objects.get(id=hbc['course_id'])
            hot_courses.append({'course': course, 'hits_percent': hits_percent})
        else:
            other_course_activity += hbc['total_hits']
        i += 1
    if i > 10:
        hits_percent = float(other_course_activity * 100.0 / total_hits['total_hits'])
        hot_courses.append({'course': _('Other'), 'hits_percent': hits_percent})

    #method mixes
    tracker_methods = Tracker.objects.filter(course_id=13, type='page', submitted_date__gte=start_date). \
        extra(select={'month': 'extract( month from submitted_date )',
                      'year': 'extract( year from submitted_date )'}). \
        values('month', 'year', 'section_title'). \
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
                                            Q(activity_title__icontains='TV')).values('activity_title',
                                                                                      'section_title').annotate(
        actCount=Count('activity_title'))
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


def user_registrations_view(request):
    if not request.user.is_staff:
        raise Http404

    registrations = []

    start_date = timezone.now() - datetime.timedelta(days=31)
    end_date = timezone.now()
    interval = 'days'
    if request.method == 'POST':
        form = DateRangeIntervalForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = form.cleaned_data.get("end_date")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            interval = form.cleaned_data.get("interval")
    else:
        data = {}
        data['start_date'] = start_date
        data['end_date'] = end_date
        data['interval'] = interval
        form = DateRangeIntervalForm(initial=data)

    if interval == 'days':
        no_days = (end_date - start_date).days + 1

        for i in range(0, no_days, +1):
            temp = start_date + datetime.timedelta(days=i)
            day = temp.strftime("%d")
            month = temp.strftime("%m")
            year = temp.strftime("%Y")
            count = User.objects.filter(date_joined__year=year, date_joined__month=month,
                                        date_joined__day=day).count()

            registrations.append([temp.strftime("%d %b %Y"), count])
    else:
        delta = relativedelta(months=+1)

        no_months = 0
        tmp_date = start_date
        while tmp_date <= end_date:
            tmp_date += delta
            no_months += 1

        for i in range(0, no_months, +1):
            temp = start_date + relativedelta(months=+i)
            month = temp.strftime("%m")
            year = temp.strftime("%Y")
            count = User.objects.filter(date_joined__month=month, date_joined__year=year).count()

            registrations.append([temp.strftime("%b %Y"), count])

    previous_user_registrations = User.objects.filter(date_joined__lt=start_date).count()
    return render_to_response('oppia/viz/user-registrations.html',
                              {'form': form,
                               'user_registrations': registrations,
                               'interval': interval,
                               'previous_user_registrations': previous_user_registrations},
                              context_instance=RequestContext(request))


def activity_by_country_view(request):
    if not request.user.is_staff:
        raise Http404

    # Countries
    hits_by_country = UserLocationVisualization.objects.all().values('country_code', 'country_name').annotate(
        country_total_hits=Sum('hits')).order_by('-country_total_hits')
    total_hits = UserLocationVisualization.objects.all().aggregate(total_hits=Sum('hits'))
    total_countries = hits_by_country.count()

    i = 0
    country_activity = []
    other_country_activity = 0
    for c in hits_by_country:
        if i < 20:
            hits_percent = float(c['country_total_hits'] * 100.0 / total_hits['total_hits'])
            country_activity.append(
                {'country_code': c['country_code'], 'country_name': c['country_name'], 'hits_percent': hits_percent})
        else:
            other_country_activity += c['country_total_hits']
        i += 1
    if i > 20:
        hits_percent = float(other_country_activity * 100.0 / total_hits['total_hits'])
        country_activity.append({'country_code': None, 'country_name': _('Other'), 'hits_percent': hits_percent})

    # Language
    hit_by_language = Tracker.objects.filter(user__is_staff=False).exclude(lang=None).values('lang').annotate(
        total_hits=Count('id')).order_by('-total_hits')
    total_hits = Tracker.objects.filter(user__is_staff=False).exclude(lang=None).aggregate(total_hits=Count('id'))

    i = 0
    languages = []
    other_languages = 0
    for hbl in hit_by_language:
        if i < 10:
            hits_percent = float(hbl['total_hits'] * 100.0 / total_hits['total_hits'])
            languages.append({'lang': hbl['lang'], 'hits_percent': hits_percent})
        else:
            other_languages += hbl['total_hits']
        i += 1
    if i > 10:
        hits_percent = float(other_languages * 100.0 / total_hits['total_hits'])
        languages.append({'lang': _('Other'), 'hits_percent': hits_percent})

    return render_to_response('oppia/viz/activity-by-country.html',
                              {'total_countries': total_countries,
                               'country_activity': country_activity,
                               'languages': languages},
                              context_instance=RequestContext(request))


def course_activity_view(request):
    if not request.user.is_staff:
        raise Http404

    course_activity = []

    start_date = timezone.now() - datetime.timedelta(days=31)
    end_date = timezone.now()
    interval = 'days'
    if request.method == 'POST':
        form = DateRangeIntervalForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = form.cleaned_data.get("end_date")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            interval = form.cleaned_data.get("interval")
    else:
        data = {}
        data['start_date'] = start_date
        data['end_date'] = end_date
        data['interval'] = interval
        form = DateRangeIntervalForm(initial=data)

    if interval == 'days':
        no_days = (end_date - start_date).days + 1

        for i in range(0, no_days, +1):
            temp = start_date + datetime.timedelta(days=i)
            day = temp.strftime("%d")
            month = temp.strftime("%m")
            year = temp.strftime("%Y")
            count = Tracker.objects.filter(user__is_staff=False, submitted_date__year=year,
                                           submitted_date__month=month, submitted_date__day=day).count()

            course_activity.append([temp.strftime("%d %b %Y"), count])
    else:
        delta = relativedelta(months=+1)

        no_months = 0
        tmp_date = start_date
        while tmp_date <= end_date:
            tmp_date += delta
            no_months += 1

        for i in range(0, no_months, +1):
            temp = start_date + relativedelta(months=+i)
            month = temp.strftime("%m")
            year = temp.strftime("%Y")
            count = Tracker.objects.filter(user__is_staff=False, submitted_date__year=year,
                                           submitted_date__month=month).count()

            course_activity.append([temp.strftime("%b %Y"), count])

    previous_course_activity = Tracker.objects.filter(user__is_staff=False, submitted_date__lt=start_date).count()

    last_month = timezone.now() - datetime.timedelta(days=31)
    hit_by_course = Tracker.objects.filter(user__is_staff=False, submitted_date__gte=last_month).exclude(
        course_id=None).values('course_id').annotate(total_hits=Count('id')).order_by('-total_hits')
    total_hits = Tracker.objects.filter(user__is_staff=False, submitted_date__gte=last_month).exclude(
        course_id=None).aggregate(total_hits=Count('id'))

    i = 0
    hot_courses = []
    other_course_activity = 0
    for hbc in hit_by_course:
        if i < 10:
            hits_percent = float(hbc['total_hits'] * 100.0 / total_hits['total_hits'])
            course = Course.objects.get(id=hbc['course_id'])
            hot_courses.append({'course': course, 'hits_percent': hits_percent})
        else:
            other_course_activity += hbc['total_hits']
        i += 1
    if i > 10:
        hits_percent = float(other_course_activity * 100.0 / total_hits['total_hits'])
        hot_courses.append({'course': _('Other'), 'hits_percent': hits_percent})
    return render_to_response('oppia/viz/course-activity.html',
                              {'form': form,
                               'course_activity': course_activity,
                               'previous_course_activity': previous_course_activity,
                               'interval': interval,
                               'hot_courses': hot_courses},
                              context_instance=RequestContext(request))


def course_downloads_view(request):
    if not request.user.is_staff:
        raise Http404

    course_downloads = []

    start_date = timezone.now() - datetime.timedelta(days=31)
    end_date = timezone.now()
    interval = 'days'
    if request.method == 'POST':
        form = DateRangeIntervalForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = form.cleaned_data.get("end_date")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            interval = form.cleaned_data.get("interval")
    else:
        data = {}
        data['start_date'] = start_date
        data['end_date'] = end_date
        data['interval'] = interval
        form = DateRangeIntervalForm(initial=data)

    if interval == 'days':
        no_days = (end_date - start_date).days + 1

        for i in range(0, no_days, +1):
            temp = start_date + datetime.timedelta(days=i)
            day = temp.strftime("%d")
            month = temp.strftime("%m")
            year = temp.strftime("%Y")
            count = CourseDownload.objects.filter(user__is_staff=False, download_date__year=year,
                                                  download_date__month=month,
                                                  download_date__day=day).count()

            course_downloads.append([temp.strftime("%d %b %Y"), count])
    else:
        delta = relativedelta(months=+1)

        no_months = 0
        tmp_date = start_date
        while tmp_date <= end_date:
            tmp_date += delta
            no_months += 1

        for i in range(0, no_months, +1):
            temp = start_date + relativedelta(months=+i)
            month = temp.strftime("%m")
            year = temp.strftime("%Y")
            count = CourseDownload.objects.filter(user__is_staff=False, download_date__month=month,
                                                  download_date__year=year).count()

            course_downloads.append([temp.strftime("%b %Y"), count])

    previous_course_downloads = CourseDownload.objects.filter(user__is_staff=False,
                                                              download_date__lt=start_date).count()

    return render_to_response('oppia/viz/course-downloads.html',
                              {'form': form,
                               'course_downloads': course_downloads,
                               'interval': interval,
                               'previous_course_downloads': previous_course_downloads, },
                              context_instance=RequestContext(request))


def films_for_method_view(request):
    if not request.user.is_staff:
        raise Http404

    start_date = timezone.now() - datetime.timedelta(days=365)
    if request.method == 'POST':
        form = DateDiffForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
    else:
        data = {}
        data['start_date'] = start_date
        form = DateDiffForm(initial=data)

    films_activity = Tracker.objects.filter(Q(course_id=13), Q(type='page'),
                                            Q(activity_title__icontains='Doctor Speaks') |
                                            Q(activity_title__icontains='Real') |
                                            Q(activity_title__icontains='Entertainment') |
                                            Q(activity_title__icontains='TV')).values('activity_title',
                                                                                      'section_title').annotate(
        actCount=Count('activity_title'))
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
    films_all_dict = {}
    for flim in films_completed:
        sec_title = json.loads(flim.section_title)
        sec_title = sec_title['en']
        act = json.loads(flim.activity_title)
        act = act['en']
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
        full_title = act + '_' + sec_title
        if full_title in films_all_dict:
            if flim.completed == 0:
                films_all_dict[full_title]['partial'] += 1
            else:
                films_all_dict[full_title]['completed'] += 1
        else:
            films_all_dict[full_title] = {}
            films_all_dict[full_title]['section'] = sec_title
            films_all_dict[full_title]['activity'] = act
            if flim.completed == 0:
                films_all_dict[full_title]['partial'] = 1
                films_all_dict[full_title]['completed'] = 0
            else:
                films_all_dict[full_title]['partial'] = 0
                films_all_dict[full_title]['completed'] = 1
    sorted_sections = sorted(films_completed_dict.keys())
    films_final_list = []
    for f in sorted_sections:
        temp = {}
        temp['section'] = f
        values = films_completed_dict[f]
        temp['partial'] = values['partial']
        temp['completed'] = values['completed']
        films_final_list.append(temp)
    return render_to_response('oppia/viz/films-for-method.html',
                              {'form': form,
                               'films_activity': sorted_film_dict,
                               'activity_list': activity_list,
                               'films_completed': films_final_list,
                               'all_films': films_all_dict},
                              context_instance=RequestContext(request))


def method_mixes_view(request):
    if not request.user.is_staff:
        raise Http404

    tracker_methods = []
    tracker_dict = {}
    tracker_list = []

    sections_list = []

    trackers = Tracker.objects.filter(course_id=13, type='page').values('section_title'). \
        annotate(count=Count('section_title')).order_by('section_title')
    for track in trackers:
        sec_title = json.loads(track['section_title'])
        sec_title = sec_title['en']
        sections_list.append(sec_title)

    start_date = timezone.now() - datetime.timedelta(days=31)
    end_date = timezone.now()
    interval = 'days'
    if request.method == 'POST':
        form = DateRangeIntervalForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = form.cleaned_data.get("end_date")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            interval = form.cleaned_data.get("interval")
    else:
        data = {'start_date': start_date, 'end_date': end_date, 'interval': interval}
        form = DateRangeIntervalForm(initial=data)

    if interval == 'days':
        no_days = (end_date - start_date).days + 1

        for i in range(0, no_days, +1):
            temp = start_date + datetime.timedelta(days=i)
            day = temp.strftime("%d")
            month = temp.strftime("%m")
            year = temp.strftime("%Y")
            trackers = Tracker.objects.filter(course_id=13, type='page', submitted_date__year=year,
                                              submitted_date__month=month, submitted_date__day=day). \
                values('section_title').annotate(count=Count('section_title')).order_by('section_title')

            count = trackers.count()
            for meth in trackers:
                sec_title = json.loads(meth['section_title'])
                sec_title = sec_title['en']
                meth['section_title'] = sec_title
                key = temp.strftime("%d %b %Y")
                meth['date'] = key
                if key in tracker_dict.keys():
                    tracker_dict[key].append(meth)
                else:
                    tracker_dict[key] = [meth]
                    tracker_list.append(tracker_dict[key])
            if count == 0:
                temp_dict = {}
                key = temp.strftime("%d %b %Y")
                temp_dict[key] = []
                for sec in sections_list:
                    temp_dict[key].append({'count': count, 'section_title': sec, 'date': key})
                tracker_list.append(temp_dict[key])

            tracker_methods.append([temp.strftime("%d %b %Y"), count])
    else:
        delta = relativedelta(months=+1)

        no_months = 0
        tmp_date = start_date
        while tmp_date <= end_date:
            tmp_date += delta
            no_months += 1

        for i in range(0, no_months, +1):
            temp = start_date + relativedelta(months=+i)
            month = temp.strftime("%m")
            year = temp.strftime("%Y")
            trackers = Tracker.objects.filter(course_id=13, type='page', submitted_date__year=year,
                                              submitted_date__month=month).values('section_title') \
                .annotate(count=Count('section_title')).order_by('section_title')
            count = trackers.count()

            for meth in trackers:
                sec_title = json.loads(meth['section_title'])
                sec_title = sec_title['en']
                meth['section_title'] = sec_title
                key = temp.strftime("%d %b %Y")
                meth['date'] = key
                if key in tracker_dict.keys():
                    tracker_dict[key].append(meth)
                else:
                    tracker_dict[key] = [meth]
                    tracker_list.append(tracker_dict[key])
            if count == 0:
                temp_dict = {}
                key = temp.strftime("%d %b %Y")
                temp_dict[key] = []
                for sec in sections_list:
                    temp_dict[key].append({'count': count, 'section_title': sec, 'date': key})
                tracker_list.append(temp_dict[key])

            tracker_methods.append([temp.strftime("%d %b %Y"), count])

    return render_to_response('oppia/viz/method-mixes.html',
                              {'form': form,
                               'tracker_methods': tracker_list,
                               'sections_list': sections_list,
                               'interval': interval},
                              context_instance=RequestContext(request))


def clients_view(request):
    if not request.user.is_staff:
        raise Http404

    start_date = timezone.now() - datetime.timedelta(days=365)
    if request.method == 'POST':
        form = DateDiffForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
    else:
        data = {}
        data['start_date'] = start_date
        form = DateDiffForm(initial=data)

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
        temp_avg = temp['time'] / temp['count']
        temp['time'] = '%ihrs: %imin: %isec' % (((temp_avg.days * 24) + temp_avg.seconds // 3600),
                                                (temp_avg.seconds // 60) % 60, temp_avg.seconds % 60)

    # clients graphs on all filters

    clients_age_range = [{'<20': 0}, {'21-25': 0}, {'26-30': 0}, {'30-40': 0}, {'>40': 0}]
    clients_life_stage = {'adolescent': 0, 'newlymarried': 0, 'pregnant': 0,
                          'onechild': 0, 'unwantedpregnancy': 0, 'twoormorechildren': 0}
    clients_marital_status = {'yes': 0, 'no': 0}
    clients_using_method = {'yes': 0, 'no': 0}

    all_clients = Client.objects.all()

    for cl in all_clients:
        #categorizing based on age
        if cl.age < 20:
            clients_age_range[0]['<20'] += 1
        elif 20 < cl.age <= 25:
            clients_age_range[1]['21-25'] += 1
        elif 26 <= cl.age < 30:
            clients_age_range[2]['26-30'] += 1
        elif 30 < cl.age < 40:
            clients_age_range[3]['30-40'] += 1
        else:
            clients_age_range[4]['>40'] += 1

        #categorizing life stage
        lstage = cl.life_stage.lower()
        if lstage == 'adolescent':
            clients_life_stage['adolescent'] += 1
        elif lstage == 'newlymarried' or lstage == 'newly married':
            clients_life_stage['newlymarried'] += 1
        elif lstage == 'pregnant':
            clients_life_stage['pregnant'] += 1
        elif lstage == 'onechild' or lstage == 'one child':
            clients_life_stage['onechild'] += 1
        elif lstage == 'unwantedpregnancy' or lstage == 'unwanted pregnancy':
            clients_life_stage['unwantedpregnancy'] += 1
        else:
            clients_life_stage['twoormorechildren'] += 1

        if cl.marital_status.lower() == 'yes':
            clients_marital_status['yes'] += 1
        else:
            clients_marital_status['no'] += 1

        if cl.using_method != None and cl.using_method.lower() == 'yes':
            clients_using_method['yes'] += 1
        else:
            clients_using_method['no'] += 1

    return render_to_response('oppia/viz/unique-repeat-clients.html',
                              {'form': form,
                               'clients_list': clients_count_list,
                               'previous_clients_list': previous_clients,
                               'clients_age_range': clients_age_range,
                               'clients_life_stage': clients_life_stage,
                               'clients_marital_status': clients_marital_status,
                               'clients_using_method': clients_using_method,
                               'sessions': sessions_dict},
                              context_instance=RequestContext(request))


