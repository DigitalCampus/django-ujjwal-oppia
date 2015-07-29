# coding=utf-8
# oppia/views.py
import datetime
import json
import shutil
import os
import oppia
import tablib

from dateutil.relativedelta import relativedelta

from django import forms
from django.views.generic import FormView
from django.conf import settings
from django.contrib.auth import (authenticate, logout, views)
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q, Count, F
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from oppia.forms import UploadCourseStep1Form, UploadCourseStep2Form, ScheduleForm, DateRangeForm, DateRangeIntervalForm
from oppia.forms import ActivityScheduleForm, CohortForm, ClientFilterForm, ClientConversionFilterForm
from oppia.models import Course, Tracker, Tag, CourseTag, Schedule, Client, ClientTracker
from oppia.models import ActivitySchedule, Activity, Cohort, Participant, Points, CourseDownload
from oppia.quiz.models import Quiz, QuizAttempt, QuizAttemptResponse
from oppia.viz.models import UserLocationVisualization

from uploader import handle_uploaded_file


def server_view(request):
    return render_to_response('oppia/server.html',
                              {'settings': settings},
                              content_type="application/json",
                              context_instance=RequestContext(request))


def home_view(request):
    activity = []
    interval = ''
    if request.user.is_authenticated():
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
                count = Tracker.objects.filter(course__isnull=False, course__is_draft=False, user__is_staff=False,
                                               course__is_archived=False, tracker_date__day=day,
                                               tracker_date__month=month, tracker_date__year=year).count()
                activity.append([temp.strftime("%d %b %Y"), count])
        else:
            delta = relativedelta(months=+1)

            no_months = 0
            tmp_date = start_date
            while tmp_date <= end_date:
                print tmp_date
                tmp_date += delta
                no_months += 1

            for i in range(0, no_months, +1):
                temp = start_date + relativedelta(months=+i)
                month = temp.strftime("%m")
                year = temp.strftime("%Y")
                count = Tracker.objects.filter(course__isnull=False, course__is_draft=False, user__is_staff=False,
                                               course__is_archived=False, tracker_date__month=month,
                                               tracker_date__year=year).count()
                activity.append([temp.strftime("%b %Y"), count])
    else:
        form = None
    leaderboard = Points.get_leaderboard(10)
    clients = Client.objects.all()
    clients = Client.objects.all().order_by('id')
    clientsDict = {}
    for client in clients:
        if client.adapted_method != "":
            splits = client.adapted_method.split("_")
            client.adapted_method = splits[0]
            client.lastmodified_date = splits[1].split(" ")[0]
        clientsDict[client.id] = [client, []]
    clientTrackers = ClientTracker.objects.all().order_by('client__id')
    for tracker in clientTrackers:
        val = clientsDict[tracker.client_id][1]
        val.append(tracker)

    users = User.objects.all()
    user_set = []
    for user in users:
        user_set.append((user.id, user.username))
    return render_to_response('oppia/home.html',
                              {'form': form,
                               'clients': clientsDict,
                               'recent_activity': activity,
                               'leaderboard': leaderboard,
                               'interval': interval,
                               'user_set': user_set},
                              context_instance=RequestContext(request))


def course_view(request):
    if request.user.is_staff:
        course_list = Course.objects.filter(is_archived=False).order_by('title')
    else:
        course_list = Course.objects.filter(is_draft=False, is_archived=False).order_by('title')
    startdate = datetime.datetime.now()
    for course in course_list:
        course.activity = []
        for i in range(7, -1, -1):
            temp = startdate - datetime.timedelta(days=i)
            day = temp.strftime("%d")
            month = temp.strftime("%m")
            year = temp.strftime("%Y")

            count = Tracker.objects.filter(course=course, user__is_staff=False, tracker_date__day=day,
                                           tracker_date__month=month, tracker_date__year=year).count()
            course.activity.append([temp.strftime("%d %b %Y"), count])
    tag_list = Tag.objects.all().order_by('name')
    return render_to_response('oppia/course/course.html', {'course_list': course_list, 'tag_list': tag_list},
                              context_instance=RequestContext(request))


def tag_courses_view(request, id):
    if request.user.is_staff:
        course_list = Course.objects.filter(is_archived=False, coursetag__tag_id=id).order_by('title')
    else:
        course_list = Course.objects.filter(is_draft=False, is_archived=False, coursetag__tag_id=id).order_by('title')
    startdate = datetime.datetime.now()
    for course in course_list:
        course.activity = []
        for i in range(7, -1, -1):
            temp = startdate - datetime.timedelta(days=i)
            day = temp.strftime("%d")
            month = temp.strftime("%m")
            year = temp.strftime("%Y")

            count = Tracker.objects.filter(course=course, user__is_staff=False, tracker_date__day=day,
                                           tracker_date__month=month, tracker_date__year=year).count()
            course.activity.append([temp.strftime("%d %b %Y"), count])
    tag_list = Tag.objects.all().order_by('name')
    return render_to_response('oppia/course/course.html',
                              {'course_list': course_list, 'tag_list': tag_list, 'current_tag': id},
                              context_instance=RequestContext(request))


def terms_view(request):
    return render_to_response('oppia/terms.html', {'settings': settings}, context_instance=RequestContext(request))


def upload_step1(request):
    if settings.OPPIA_STAFF_ONLY_UPLOAD is True and not request.user.is_staff:
        return render_to_response('oppia/upload-staff-only.html', {'settings': settings},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        form = UploadCourseStep1Form(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass
            extract_path = settings.COURSE_UPLOAD_DIR + 'temp/' + str(request.user.id) + '/'
            course = handle_uploaded_file(request.FILES['course_file'], extract_path, request)
            if course:
                shutil.rmtree(extract_path)
                return HttpResponseRedirect(reverse('oppia_upload2', args=[course.id]))  # Redirect after POST
            else:
                shutil.rmtree(extract_path, ignore_errors=True)
                os.remove(settings.COURSE_UPLOAD_DIR + request.FILES['course_file'].name)
    else:
        form = UploadCourseStep1Form()  # An unbound form

    return render(request, 'oppia/upload.html', {'form': form, 'title': _(u'Upload Course - step 1')})


def upload_step2(request, course_id):
    if settings.OPPIA_STAFF_ONLY_UPLOAD is True and not request.user.is_staff:
        return render_to_response('oppia/upload-staff-only.html', {'settings': settings},
                                  context_instance=RequestContext(request))

    course = Course.objects.get(pk=course_id)

    if request.method == 'POST':
        form = UploadCourseStep2Form(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass
            is_draft = form.cleaned_data.get("is_draft")
            if course:
                #add the tags
                tags = form.cleaned_data.get("tags").strip().split(",")
                is_draft = form.cleaned_data.get("is_draft")
                if len(tags) > 0:
                    course.is_draft = is_draft
                    course.save()
                    for t in tags:
                        try:
                            tag = Tag.objects.get(name__iexact=t.strip())
                        except Tag.DoesNotExist:
                            tag = Tag()
                            tag.name = t.strip()
                            tag.created_by = request.user
                            tag.save()
                        # add tag to course
                        try:
                            ct = CourseTag.objects.get(course=course, tag=tag)
                        except CourseTag.DoesNotExist:
                            ct = CourseTag()
                            ct.course = course
                            ct.tag = tag
                            ct.save()
                return HttpResponseRedirect('success/')  # Redirect after POST
    else:
        form = UploadCourseStep2Form(initial={'tags': course.get_tags(),
                                              'is_draft': course.is_draft, })  # An unbound form

    return render(request, 'oppia/upload.html', {'form': form, 'title': _(u'Upload Course - step 2')})


def recent_activity(request, id):
    course = check_can_view(request, id)

    start_date = datetime.datetime.now() - datetime.timedelta(days=31)
    end_date = datetime.datetime.now()
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

    dates = []
    if interval == 'days':
        no_days = (end_date - start_date).days + 1

        for i in range(0, no_days, +1):
            temp = start_date + datetime.timedelta(days=i)
            day = temp.strftime("%d")
            month = temp.strftime("%m")
            year = temp.strftime("%Y")
            count_objs = Tracker.objects.filter(course=course, tracker_date__day=day, tracker_date__month=month,
                                                tracker_date__year=year).values('type').annotate(total=Count('type'))
            count_activity = {'page': 0, 'quiz': 0, 'media': 0, 'resource': 0, 'monitor': 0, 'total': 0}
            for co in count_objs:
                if co['type'] in count_activity:
                    count_activity[co['type']] = count_activity[co['type']] + co['total']
                    count_activity['total'] = count_activity['total'] + co['total']
                else:
                    count_activity[co['type']] = 0
                    count_activity[co['type']] = count_activity[co['type']] + co['total']
                    count_activity['total'] = count_activity['total'] + co['total']

            dates.append([temp.strftime("%d %b %y"), count_activity])
    else:
        delta = relativedelta(months=+1)
        no_months = 0
        tmp_date = start_date
        while tmp_date <= end_date:
            print tmp_date
            tmp_date += delta
            no_months += 1

        for i in range(0, no_months, +1):
            temp = start_date + relativedelta(months=+i)
            month = temp.strftime("%m")
            year = temp.strftime("%Y")
            count_objs = Tracker.objects.filter(course=course, tracker_date__month=month,
                                                tracker_date__year=year).values('type').annotate(total=Count('type'))
            count_activity = {'page': 0, 'quiz': 0, 'media': 0, 'resource': 0, 'monitor': 0, 'total': 0}
            for co in count_objs:
                if co['type'] in count_activity:
                    count_activity[co['type']] = count_activity[co['type']] + co['total']
                    count_activity['total'] = count_activity['total'] + co['total']
                else:
                    count_activity[co['type']] = 0
                    count_activity[co['type']] = count_activity[co['type']] + co['total']
                    count_activity['total'] = count_activity['total'] + co['total']

            dates.append([temp.strftime("%b %y"), count_activity])

    leaderboard = Points.get_leaderboard(10, course)
    nav = get_nav(course, request.user)
    return render_to_response('oppia/course/activity.html',
                              {'course': course,
                               'form': form,
                               'nav': nav,
                               'data': dates,
                               'interval': interval,
                               'leaderboard': leaderboard},
                              context_instance=RequestContext(request))


def recent_activity_detail(request, id):
    course = check_owner(request, id)

    start_date = datetime.datetime.now() - datetime.timedelta(days=31)
    end_date = datetime.datetime.now()
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = form.cleaned_data.get("end_date")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            trackers = Tracker.objects.filter(course=course, tracker_date__gte=start_date,
                                              tracker_date__lte=end_date).order_by('-tracker_date')
        else:
            trackers = Tracker.objects.filter(course=course).order_by('-tracker_date')
    else:
        data = {}
        data['start_date'] = start_date
        data['end_date'] = end_date
        form = DateRangeForm(initial=data)
        trackers = Tracker.objects.filter(course=course).order_by('-tracker_date')

    paginator = Paginator(trackers, 25)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        tracks = paginator.page(page)
        for t in tracks:
            t.data_obj = []
            try:
                data_dict = json.loads(t.data)
                for key, value in data_dict.items():
                    t.data_obj.append([key, value])
            except ValueError:
                pass
            t.data_obj.append(['agent', t.agent])
            t.data_obj.append(['ip', t.ip])
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)

    nav = get_nav(course, request.user)
    return render_to_response('oppia/course/activity-detail.html',
                              {'course': course,
                               'form': form,
                               'nav': nav,
                               'page': tracks, },
                              context_instance=RequestContext(request))


def export_tracker_detail(request, id):
    course = check_owner(request, id)

    headers = (
    'Date', 'UserId', 'Type', 'Activity Title', 'Section Title', 'Time Taken', 'IP Address', 'User Agent', 'Language')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    trackers = Tracker.objects.filter(course=course).order_by('-tracker_date')
    for t in trackers:
        try:
            data_dict = json.loads(t.data)
            if 'lang' in data_dict:
                lang = data_dict['lang']
            else:
                lang = ""
            data.append((t.tracker_date.strftime('%Y-%m-%d %H:%M:%S'), t.user.id, t.type, t.get_activity_title(),
                         t.get_section_title(), t.time_taken, t.ip, t.agent, lang))
        except ValueError:
            data.append((
            t.tracker_date.strftime('%Y-%m-%d %H:%M:%S'), t.user.id, t.type, "", "", t.time_taken, t.ip, t.agent, ""))

    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=export.xls"

    return response


def schedule(request, course_id):
    course = check_owner(request, course_id)
    schedules = Schedule.objects.filter(course=course)
    return render_to_response('oppia/course/schedules.html', {'course': course, 'schedules': schedules, },
                              context_instance=RequestContext(request))


def schedule_add(request, course_id):
    course = check_owner(request, course_id)
    ActivityScheduleFormSet = formset_factory(ActivityScheduleForm, extra=0)

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        formset = ActivityScheduleFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            schedule = Schedule()
            schedule.course = course
            schedule.title = form.cleaned_data.get("title").strip()
            schedule.default = form.cleaned_data.get("default")
            schedule.created_by = request.user

            # remvoe any existing default for this schedule
            if schedule.default:
                Schedule.objects.filter(course=course).update(default=False)

            schedule.save()

            for f in formset:
                act_sched = ActivitySchedule()
                start_date = f.cleaned_data.get("start_date")
                end_date = f.cleaned_data.get("end_date")
                digest = f.cleaned_data.get("digest")
                if start_date is not None:
                    act_sched = ActivitySchedule()
                    act_sched.schedule = schedule
                    act_sched.start_date = start_date
                    act_sched.end_date = end_date
                    act_sched.digest = digest.strip()
                    act_sched.save()
            return HttpResponseRedirect('../saved/')
    else:
        activities = Activity.objects.filter(section__course=course)
        initial = []
        section = None
        start_date = datetime.datetime.now()
        end_date = datetime.datetime.now() + datetime.timedelta(days=7)
        for a in activities:
            if a.section != section:
                section = a.section
                start_date = start_date + datetime.timedelta(days=7)
                end_date = end_date + datetime.timedelta(days=7)
            data = {}
            data['title'] = a.title
            data['digest'] = a.digest
            data['section'] = a.section.title
            data['start_date'] = start_date
            data['end_date'] = end_date
            initial.append(data)
            form = ScheduleForm()
        formset = ActivityScheduleFormSet(initial=initial)

    return render(request, 'oppia/schedule-form.html', {'form': form, 'formset': formset, 'course': course, })


def schedule_edit(request, course_id, schedule_id):
    course = check_owner(request, course_id)
    schedule = Schedule.objects.get(pk=schedule_id)
    ActivityScheduleFormSet = formset_factory(ActivityScheduleForm, extra=0)
    activities = Activity.objects.filter(section__course=course)

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        formset = ActivityScheduleFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            schedule.title = form.cleaned_data.get("title").strip()
            schedule.default = form.cleaned_data.get("default")
            schedule.lastupdated_date = datetime.datetime.now()

            # remove any existing default for this schedule
            if schedule.default:
                Schedule.objects.filter(course=course).update(default=False)

            schedule.save()

            # remove all the old schedule Activities
            ActivitySchedule.objects.filter(schedule=schedule).delete()

            for f in formset:
                act_sched = ActivitySchedule()
                start_date = f.cleaned_data.get("start_date")
                end_date = f.cleaned_data.get("end_date")
                digest = f.cleaned_data.get("digest")
                if start_date is not None:
                    act_sched = ActivitySchedule()
                    act_sched.schedule = schedule
                    act_sched.start_date = start_date
                    act_sched.end_date = end_date
                    act_sched.digest = digest.strip()
                    act_sched.save()
            return HttpResponseRedirect('../saved/')
    else:
        initial = []
        section = None
        for a in activities:
            if a.section != section:
                section = a.section
            data = {}
            data['title'] = a.title
            data['digest'] = a.digest
            data['section'] = a.section.title
            try:
                act_s = ActivitySchedule.objects.get(schedule=schedule, digest=a.digest)
                start_date = act_s.start_date
                end_date = act_s.end_date
            except ActivitySchedule.DoesNotExist:
                start_date = None
                end_date = None
            data['start_date'] = start_date
            data['end_date'] = end_date
            initial.append(data)
        form = ScheduleForm(initial={'title': schedule.title,
                                     'default': schedule.default})
        formset = ActivityScheduleFormSet(initial=initial)

    return render(request, 'oppia/schedule-form.html', {'form': form, 'formset': formset, 'course': course, })


def schedule_saved(request, course_id, schedule_id=None):
    course = check_owner(request, course_id)
    return render_to_response('oppia/schedule-saved.html',
                              {'course': course},
                              context_instance=RequestContext(request))


def cohort(request, course_id):
    course = check_owner(request, course_id)
    cohorts = Cohort.objects.filter(course=course)
    return render_to_response('oppia/course/cohorts.html', {'course': course, 'cohorts': cohorts, },
                              context_instance=RequestContext(request))


def cohort_add(request, course_id):
    course = check_owner(request, course_id)
    if request.method == 'POST':
        form = CohortForm(request.POST)
        if form.is_valid():  # All validation rules pass
            cohort = Cohort()
            cohort.course = course
            cohort.start_date = form.cleaned_data.get("start_date")
            cohort.end_date = form.cleaned_data.get("end_date")
            cohort.description = form.cleaned_data.get("description").strip()
            cohort.save()

            students = form.cleaned_data.get("students").strip().split(",")
            if len(students) > 0:
                for s in students:
                    try:
                        student = User.objects.get(username=s.strip())
                        participant = Participant()
                        participant.cohort = cohort
                        participant.user = student
                        participant.role = Participant.STUDENT
                        participant.save()
                    except User.DoesNotExist:
                        pass
            teachers = form.cleaned_data.get("teachers").strip().split(",")
            if len(teachers) > 0:
                for t in teachers:
                    try:
                        teacher = User.objects.get(username=t.strip())
                        participant = Participant()
                        participant.cohort = cohort
                        participant.user = teacher
                        participant.role = Participant.TEACHER
                        participant.save()
                    except User.DoesNotExist:
                        pass
            return HttpResponseRedirect('../')  # Redirect after POST

    else:
        form = CohortForm()  # An unbound form

    return render(request, 'oppia/cohort-form.html', {'course': course, 'form': form, })


def cohort_edit(request, course_id, cohort_id):
    course = check_owner(request, course_id)
    cohort = Cohort.objects.get(pk=cohort_id)
    if request.method == 'POST':
        form = CohortForm(request.POST)
        if form.is_valid():
            cohort.description = form.cleaned_data.get("description").strip()
            cohort.start_date = form.cleaned_data.get("start_date")
            cohort.end_date = form.cleaned_data.get("end_date")
            cohort.save()

            Participant.objects.filter(cohort=cohort).delete()

            students = form.cleaned_data.get("students").split(",")
            if len(students) > 0:
                for s in students:
                    try:
                        participant = Participant()
                        participant.cohort = cohort
                        participant.user = User.objects.get(username=s.strip())
                        participant.role = Participant.STUDENT
                        participant.save()
                    except User.DoesNotExist:
                        pass
            teachers = form.cleaned_data.get("teachers").split(",")
            if len(teachers) > 0:
                for t in teachers:
                    try:
                        participant = Participant()
                        participant.cohort = cohort
                        participant.user = User.objects.get(username=t.strip())
                        participant.role = Participant.TEACHER
                        participant.save()
                    except User.DoesNotExist:
                        pass
            return HttpResponseRedirect('../../')

    else:
        participant_teachers = Participant.objects.filter(cohort=cohort, role=Participant.TEACHER)
        teacher_list = []
        for pt in participant_teachers:
            teacher_list.append(pt.user.username)
        teachers = ", ".join(teacher_list)

        participant_students = Participant.objects.filter(cohort=cohort, role=Participant.STUDENT)
        student_list = []
        for ps in participant_students:
            student_list.append(ps.user.username)
        students = ", ".join(student_list)
        form = CohortForm(initial={'description': cohort.description, 'teachers': teachers, 'students': students,
                                   'start_date': cohort.start_date, 'end_date': cohort.end_date})

    return render(request, 'oppia/cohort-form.html', {'course': course, 'form': form, })


def check_owner(request, id):
    try:
        # check only the owner can view 
        if request.user.is_staff:
            course = Course.objects.get(pk=id)
        else:
            course = Course.objects.get(pk=id, user=request.user)
    except Course.DoesNotExist:
        raise Http404
    return course


def check_can_view(request, id):
    try:
        # check only the owner can view 
        if request.user.is_staff:
            course = Course.objects.get(pk=id)
        else:
            course = Course.objects.get(pk=id, is_draft=False, is_archived=False)
    except Course.DoesNotExist:
        raise Http404
    return course


def get_nav(course, user):
    nav = []
    nav.append(
        {'url': reverse('oppia_recent_activity', args=(course.id,)), 'title': course.get_title(), 'class': 'bold'})
    if user.is_staff or user == course.user:
        nav.append({'url': reverse('oppia_recent_activity_detail', args=(course.id,)), 'title': _(u'Activity Detail')})
        if course.has_quizzes():
            nav.append({'url': reverse('oppia_course_quiz', args=(course.id,)), 'title': _(u'Course Quizzes')})
        if course.has_feedback():
            nav.append({'url': reverse('oppia_course_feedback', args=(course.id,)), 'title': _(u'Course Feedback')})
    return nav


def leaderboard_view(request):
    lb = Points.get_leaderboard(100)
    paginator = Paginator(lb, 25)  # Show 25 contacts per page

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        leaderboard = paginator.page(page)
    except (EmptyPage, InvalidPage):
        leaderboard = paginator.page(paginator.num_pages)

    return render_to_response('oppia/leaderboard.html', {'page': leaderboard}, context_instance=RequestContext(request))


def course_quiz(request, course_id):
    course = check_owner(request, course_id)
    digests = Activity.objects.filter(section__course=course, type='quiz').order_by('section__order').values(
        'digest').distinct()
    quizzes = []
    for d in digests:
        try:
            q = Quiz.objects.get(quizprops__name='digest', quizprops__value=d['digest'])
            quizzes.append(q)
        except Quiz.DoesNotExist:
            pass
    nav = get_nav(course, request.user)
    return render_to_response('oppia/course/quizzes.html', {'course': course, 'nav': nav, 'quizzes': quizzes},
                              context_instance=RequestContext(request))


def course_quiz_attempts(request, course_id, quiz_id):
    # get the quiz digests for this course
    course = check_owner(request, course_id)
    quiz = Quiz.objects.get(pk=quiz_id)
    attempts = QuizAttempt.objects.filter(quiz=quiz).order_by('-attempt_date')

    paginator = Paginator(attempts, 25)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        attempts = paginator.page(page)
        for a in attempts:
            a.responses = QuizAttemptResponse.objects.filter(quizattempt=a)
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)
    print  len(attempts)
    nav = get_nav(course, request.user)
    return render_to_response('oppia/course/quiz-attempts.html',
                              {'course': course, 'nav': nav, 'quiz': quiz, 'page': attempts},
                              context_instance=RequestContext(request))


def course_feedback(request, course_id):
    course = check_owner(request, course_id)
    digests = Activity.objects.filter(section__course=course, type='feedback').order_by('section__order').values(
        'digest').distinct()
    feedback = []
    for d in digests:
        try:
            q = Quiz.objects.get(quizprops__name='digest', quizprops__value=d['digest'])
            feedback.append(q)
        except Quiz.DoesNotExist:
            pass
    nav = get_nav(course, request.user)
    return render_to_response('oppia/course/feedback.html', {'course': course, 'nav': nav, 'feedback': feedback},
                              context_instance=RequestContext(request))


def course_feedback_responses(request, course_id, quiz_id):
    #get the quiz digests for this course
    course = check_owner(request, course_id)
    quiz = Quiz.objects.get(pk=quiz_id)
    attempts = QuizAttempt.objects.filter(quiz=quiz).order_by('-attempt_date')

    paginator = Paginator(attempts, 25)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        attempts = paginator.page(page)
        for a in attempts:
            a.responses = QuizAttemptResponse.objects.filter(quizattempt=a)
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)
    nav = get_nav(course, request.user)
    return render_to_response('oppia/course/feedback-responses.html',
                              {'course': course, 'nav': nav, 'quiz': quiz, 'page': attempts},
                              context_instance=RequestContext(request))


def clientfilter_view(request):
    methods_dict = {'Traditional Method': "पारंपरिक विधि", 'IUCD': "आई.यू .से .दी.", 'Condom': 'कंडोम',
                    'Injectable': "गर्भनिरोधक सूई", "OCP": "गर्भनिरोधक गोली", 'Female Sterilization': "महिला नसबंदी",
                    'NSV (Male Sterilization)': "एन. एस. वी. (पुरुष नसबंदी)", "ECP": 'आपातकालीन गोली',
                    'Post abortion': "गर्भपात उपरांत", 'Postpartum Family Planning': "प्रसव उपरांत"}

    lifestage_dict = {'adolescent': "بالغ", 'newlymarried': "نو وھاتا", 'pregnant': "حاملہ",
                      'onechild': "ایک بچہ", 'unwantedpregnancy': "انچاهاحمل",
                      'twoormorechildren': "دو یا دو سے زیادہ بچے"}

    methods_dict_urdu = {'Traditional Method': "روایتی طریقہ", 'IUCD': "آئ یو ڈی", 'Condom': 'کنڈوم',
                         'Injectable': "مانع حمل ٹیکہ", "OCP": "مانع حمل گولیاں", 'Female Sterilization': "نل بندی",
                         'NSV (Male Sterilization)': "نس بندی", "ECP": 'ہنگامی گولی مانع حمل',
                         'Post abortion': "اسقاط حمل کے بعد", 'Postpartum Family Planning': "ترسیل کے بعد"}

    lifestage_dict_urdu = {'adolescent': "किशोरावस्था ", 'newlymarried': "नव विहाहित", 'pregnant': "गर्भवती ",
                           'onechild': "एक बच्चे वाले दंपत्ति", 'unwantedpregnancy': "अनचाहा गर्भ",
                           'twoormorechildren': "दो या दो से अधिक वाले दंपत्ति"}

    if request.method == 'POST':
        form = ClientFilterForm(request.POST)
        if form.is_valid():
            clientsDict = {}
            user = form.cleaned_data['users']
            lifestage = form.cleaned_data['lifestage']
            parity = form.cleaned_data['parity']
            methods = form.cleaned_data['methods']
            is_deleted = form.cleaned_data['is_deleted']
            is_closed = form.cleaned_data['is_closed']
            clients = Client.objects.all()
            if user != 'none':
                clients = clients.filter(user__username=user).order_by('id')
            if lifestage != 'none':
                clients = clients.filter(Q(life_stage=lifestage) | Q(life_stage=lifestage_dict[lifestage]) |
                                         Q(life_stage=lifestage_dict_urdu[lifestage]))
            if parity != 'none':
                clients = clients.filter(parity=parity)
            if methods != 'none':
                clients = clients.filter(Q(using_method=methods) | Q(using_method=methods_dict[methods]) |
                                         Q(using_method=methods_dict_urdu[methods]))
            if is_closed or is_deleted:
                if not is_closed:
                    clients = clients.filter(Q(is_closed=False) | Q(is_deleted=True))
                if not is_deleted:
                    clients = clients.filter(Q(is_deleted=False) | Q(is_closed=True))
            else:
                clients = clients.filter(is_deleted=False)
                clients = clients.filter(is_closed=False)

            for client in clients:

                if client.adapted_method != "":
                    splits = client.adapted_method.split("_")
                    client.adapted_method = splits[0]
                    client.lastmodified_date = splits[1].split(" ")[0]
                clientsDict[client.id] = [client, []]
            clientTrackers = ClientTracker.objects.all().order_by('client__id')
            for tracker in clientTrackers:
                if clientsDict.has_key(tracker.client_id):
                    val = clientsDict[tracker.client_id][1]
                    val.append(tracker)
                else:
                    if len(clientsDict) == 1:
                        for key, value in clientsDict.items():
                            tracker.client_id = key
                            tracker.save()
                        val = clientsDict[tracker.client_id][1]
                        val.append(tracker)
            return render(request, 'oppia/clients-filter.html', {'form': form, 'clients': clientsDict, 'usr': user})
    else:
        form = ClientFilterForm()

    return render(request, 'oppia/clients-filter.html', {'form': form, })


def clientsession_view(request, client):
    if request.method == 'GET':
        clientObj = Client.objects.get(id=client)
        clientTrackers = ClientTracker.objects.filter(client__id=client).order_by('-start_time')
        session_dict = []
        for clint in clientTrackers:
            diff = relativedelta(clint.end_time, clint.start_time)
            diff = '%ihrs: %imin: %isec' % (diff.hours, diff.minutes, diff.seconds)
            session_dict.append([clint, diff])
    return render(request, 'oppia/client-session.html', {'sessions': session_dict, 'client': clientObj.name})


def leaderboards_view(request):
    activity = []
    if request.user.is_authenticated():
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
                count = Tracker.objects.filter(course__isnull=False, course__is_draft=False, user__is_staff=False,
                                               course__is_archived=False, tracker_date__day=day,
                                               tracker_date__month=month, tracker_date__year=year).count()
                activity.append([temp.strftime("%d %b %Y"), count])
        else:
            delta = relativedelta(months=+1)

            no_months = 0
            tmp_date = start_date
            while tmp_date <= end_date:
                print tmp_date
                tmp_date += delta
                no_months += 1

            for i in range(0, no_months, +1):
                temp = start_date + relativedelta(months=+i)
                month = temp.strftime("%m")
                year = temp.strftime("%Y")
                count = Tracker.objects.filter(course__isnull=False, course__is_draft=False, user__is_staff=False,
                                               course__is_archived=False, tracker_date__month=month,
                                               tracker_date__year=year).count()
                activity.append([temp.strftime("%b %Y"), count])
    else:
        form = None
    leaderboard = Points.get_leaderboard(10)
    clients = Client.objects.all().order_by('id')
    clientsDict = {}
    for client in clients:
        if client.adapted_method != "":
            splits = client.adapted_method.split("_")
            client.adapted_method = splits[0]
            client.lastmodified_date = splits[1].split(" ")[0]
        clientsDict[client.id] = [client, []]
    clientTrackers = ClientTracker.objects.all().order_by('client__id')
    for tracker in clientTrackers:
        val = clientsDict[tracker.client_id][1]
        val.append(tracker)

    users = User.objects.all()
    user_set = []
    for user in users:
        user_set.append((user.id, user.username))
    return render_to_response('oppia/leaderboard-separate.html',
                              {'form': form,
                               'clients': clientsDict,
                               'recent_activity': activity,
                               'interval': interval,
                               'leaderboard': leaderboard,
                               'user_set': user_set},
                              context_instance=RequestContext(request))


def clients_view(request):
    clients = Client.objects.all().order_by('id')
    clientsDict = {}
    for client in clients:
        if client.adapted_method != "":
            splits = client.adapted_method.split("_")
            client.adapted_method = splits[0]
            client.lastmodified_date = splits[1].split(" ")[0]
        clientsDict[client.id] = [client, []]
    clientTrackers = ClientTracker.objects.all().order_by('client__id')
    for tracker in clientTrackers:
        val = clientsDict[tracker.client_id][1]
        val.append(tracker)

    users = User.objects.all()
    user_set = []
    for user in users:
        user_set.append((user.id, user.username))
    return render_to_response('oppia/clients-list.html',
                              {'clients': clientsDict,
                               'user_set': user_set},
                              context_instance=RequestContext(request))


def recent_activity_view(request):
    activity = []
    if request.user.is_authenticated():
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
                count = Tracker.objects.filter(course__isnull=False, course__is_draft=False, user__is_staff=False,
                                               course__is_archived=False, tracker_date__day=day,
                                               tracker_date__month=month, tracker_date__year=year).count()
                activity.append([temp.strftime("%d %b %Y"), count])
        else:
            delta = relativedelta(months=+1)

            no_months = 0
            tmp_date = start_date
            while tmp_date <= end_date:
                print tmp_date
                tmp_date += delta
                no_months += 1

            for i in range(0, no_months, +1):
                temp = start_date + relativedelta(months=+i)
                month = temp.strftime("%m")
                year = temp.strftime("%Y")
                count = Tracker.objects.filter(course__isnull=False, course__is_draft=False, user__is_staff=False,
                                               course__is_archived=False, tracker_date__month=month,
                                               tracker_date__year=year).count()
                activity.append([temp.strftime("%b %Y"), count])
    else:
        form = None

    return render_to_response('oppia/recent-activity.html',
                              {'form': form,
                               'interval': interval,
                               'recent_activity': activity},
                              context_instance=RequestContext(request))


def clients_export(request):
    headers = (
        'UserId', 'Name', 'Mobile', 'Gender', 'Marital Status', 'Age', 'Parity', 'Life stage', 'Using Method',
        'Husband Name', 'Youngest Child Age', 'Created Date')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    clients = Client.objects.all()
    for c in clients:
        try:
            data.append((c.user_id, c.name, c.mobile_number, c.gender, c.marital_status, c.age, c.parity, c.life_stage,
                         c.using_method, c.husband_name, c.youngest_child_age,
                         c.created_date.strftime('%Y-%m-%d %H:%M:%S')))
        except ValueError:
            pass

    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=clients_export.xls"

    return response


def course_downloads_export(request):
    headers = (
        'UserId', 'Course', 'Download Date', 'Course Version', 'IP', 'Agent')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    downloads = CourseDownload.objects.all()
    for c in downloads:
        try:
            data.append((c.user_id, c.course_id, c.download_date.strftime('%Y-%m-%d %H:%M:%S'), c.course_version, c.ip,
                         c.agent))
        except ValueError:
            pass

    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=course_downloads_export.xls"

    return response


def course_activity_export(request):
    headers = (
        'UserId', 'Submitted Date', 'IP', 'Digest', 'Data', 'Course', 'Activity Title', 'Section Title', 'Type',
        'Completed', 'Time taken', 'Lang')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    activities = Tracker.objects.all()
    for a in activities:
        try:
            data.append((a.user_id, a.submitted_date.strftime('%Y-%m-%d %H:%M:%S'), a.ip, a.agent, a.data, a.course_id,
                         a.activity_title, a.section_title, a.type, a.completed, a.time_taken, a.lang))
        except ValueError:
            pass

    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=course_activity_export.xls"

    return response


def user_registrations_export(request):
    headers = ('User Name', 'First Name', 'Last Name', 'Email', 'Is Active', 'Date Joined')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    users = User.objects.all()
    for u in users:
        try:
            data.append((u.username, u.first_name, u.last_name, u.email, u.is_active,
                         u.date_joined.strftime('%Y-%m-%d %H:%M:%S')))
        except ValueError:
            pass

    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=user_registrations_export.xls"

    return response


def country_activity_export(request):
    headers = ('Country Name', 'Country Code', 'Region', 'Latitude', 'Longitude', 'Hits')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    usersViz = UserLocationVisualization.objects.all()
    for u in usersViz:
        try:
            data.append((u.country_name, u.country_code, u.region, u.lat, u.lng, u.hits))
        except ValueError:
            pass

    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=country_activity_export.xls"

    return response


def method_mixes_export(request):
    headers = (
        'UserId', 'Submitted Date', 'IP', 'Digest', 'Data', 'Course', 'Activity Title', 'Section Title', 'Type',
        'Completed', 'Time taken', 'Lang')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    activities = Tracker.objects.filter(course_id=13, type='page')
    for a in activities:
        try:
            data.append((a.user_id, a.submitted_date.strftime('%Y-%m-%d %H:%M:%S'), a.ip, a.agent, a.data, a.course_id,
                         a.activity_title, a.section_title, a.type, a.completed, a.time_taken, a.lang))
        except ValueError:
            pass

    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=method_mixes_export.xls"

    return response


def films_export(request):
    headers = (
        'UserId', 'Submitted Date', 'IP', 'Digest', 'Data', 'Course', 'Activity Title', 'Section Title', 'Type',
        'Completed', 'Time taken', 'Lang')
    data = []
    data = tablib.Dataset(*data, headers=headers)
    activities = Tracker.objects.filter(Q(course_id=13), Q(type='page'),
                                        Q(activity_title__icontains='Doctor Speaks') |
                                        Q(activity_title__icontains='Real') |
                                        Q(activity_title__icontains='Entertainment') |
                                        Q(activity_title__icontains='TV'))
    for a in activities:
        try:
            data.append((a.user_id, a.submitted_date.strftime('%Y-%m-%d %H:%M:%S'), a.ip, a.agent, a.data, a.course_id,
                         a.activity_title, a.section_title, a.type, a.completed, a.time_taken, a.lang))
        except ValueError:
            pass

    response = HttpResponse(data.xls, content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = "attachment; filename=films_export.xls"

    return response


def clientconversion_view(request):
    methods_dict = {'Traditional Method': "पारंपरिक विधि"}
    methods_dict_urdu = {'Traditional Method': "روایتی طریقہ"}
    if request.method == 'POST':
        form = ClientConversionFilterForm(request.POST)
        if form.is_valid():
            clientsDict = {}

            conversions = form.cleaned_data['conversions']
            clients = Client.objects.all()

            m2m = False
            if conversions != 'none':
                if conversions == 'none2method':
                    clients = clients.filter(Q(using_method='') | Q(using_method=None)).exclude(adapted_method='')
                elif conversions == 'traditional2method':
                    clients = clients.filter(Q(using_method='Traditional Method') |
                                             Q(using_method=methods_dict['Traditional Method']) |
                                             Q(using_method=methods_dict_urdu['Traditional Method'])). \
                        exclude(adapted_method='')
                else:
                    clients = clients.filter(~Q(using_method='')).exclude(adapted_method=''). \
                        exclude(using_method=methods_dict['Traditional Method']). \
                        exclude(using_method=methods_dict_urdu['Traditional Method'])
                    m2m = True

            for client in clients:
                if m2m:
                    if client.adapted_method != "":
                        splits = client.adapted_method.split("_")
                        client.adapted_method = splits[0]
                        client.lastmodified_date = splits[1].split(" ")[0]
                    if client.adapted_method != client.using_method and client.using_method != None:
                        if client.using_method != 'Traditional Method':
                            clientsDict[client.id] = [client, []]
                else:
                    if client.adapted_method != "":
                        splits = client.adapted_method.split("_")
                        client.adapted_method = splits[0]
                        client.lastmodified_date = splits[1].split(" ")[0]
                    clientsDict[client.id] = [client, []]
            clientTrackers = ClientTracker.objects.all().order_by('client__id')
            for tracker in clientTrackers:
                if clientsDict.has_key(tracker.client_id):
                    val = clientsDict[tracker.client_id][1]
                    val.append(tracker)
                else:
                    if len(clientsDict) == 1:
                        for key, value in clientsDict.items():
                            tracker.client_id = key
                            tracker.save()
                        val = clientsDict[tracker.client_id][1]
                        val.append(tracker)
            return render(request, 'oppia/clients-conversion.html', {'form': form, 'clients': clientsDict})
    else:
        form = ClientConversionFilterForm()

    return render(request, 'oppia/clients-conversion.html', {'form': form, })