# oppia/viz/urls.py
from django.conf import settings
from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
        url(r'^summary/$', 'oppia.viz.views.summary_view', name="oppia_viz_summary"),
        url(r'^user-registrations/$', 'oppia.viz.views.user_registrations_view', name="oppia_viz_user_registrations"),
        url(r'^activity-by-country/$', 'oppia.viz.views.activity_by_country_view',
            name="oppia_viz_activity_by_country"),
        url(r'^course-activity/$', 'oppia.viz.views.course_activity_view', name="oppia_viz_course_activity"),
        url(r'^course-downloads/$', 'oppia.viz.views.course_downloads_view', name="oppia_viz_course_downloads"),
        url(r'^method-mixes/$', 'oppia.viz.views.method_mixes_view', name="oppia_viz_method_mixes"),
        url(r'^unique-repeat-clients/$', 'oppia.viz.views.clients_view', name="oppia_viz_clients"),
        url(r'^films-for-method/$', 'oppia.viz.views.films_for_method_view', name="oppia_viz_films_for_methods"),
        url(r'^map/$', 'oppia.viz.views.map_view', name="oppia_viz_map"),
        )