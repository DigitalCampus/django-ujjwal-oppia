# # oppia/admin.py
# from django.contrib import admin
# from oppia.models import Course,Section,Activity,Tracker,Media,Cohort
# from oppia.models import Participant,Message,Schedule,ActivitySchedule,Tag,CourseTag
# from oppia.models import Badge,Award,Points,AwardCourse, UserProfile, Client
# from oppia.models import CourseCohort, CourseManager
# 
# class TrackerAdmin(admin.ModelAdmin):
#     list_display = ('user', 'submitted_date', 'tracker_date', 'time_taken', 'agent', 'course','completed')
#     
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('title', 'version', 'lastupdated_date', 'user', 'filename','is_draft','is_archived')
# 
# class ParticipantAdmin(admin.ModelAdmin):
#     list_display = ('cohort', 'user', 'role')
#    
# class ParticipantInline(admin.TabularInline):
#     model = Participant
#     
# class CohortAdmin(admin.ModelAdmin):
#     list_display = ('description', 'start_date', 'end_date','schedule')
#     inlines = [
#         ParticipantInline,
#     ]
#     
# class BadgeAdmin(admin.ModelAdmin):
#     list_display = ('description','points')
#  
# class PointsAdmin(admin.ModelAdmin):
#     list_display = ('user','type','course','points','date','description')
#     
# class ActivityAdmin(admin.ModelAdmin):
#     list_display = ('title','section','type','digest')
#      
# class ActivityScheduleAdmin(admin.ModelAdmin):
#     list_display = ('schedule','digest','start_date','end_date')
#  
# class AwardCourseAdmin(admin.ModelAdmin):
#     list_display = ('award','course','course_version')
#    
# class AwardAdmin(admin.ModelAdmin):
#     list_display = ('badge','user','description','award_date')
#   
# class CourseTagAdmin(admin.ModelAdmin):
#     list_display = ('course','tag')
#     
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'can_upload', 'job_title', 'organisation')
#  
# class MediaAdmin(admin.ModelAdmin):
#     list_display = ('course', 'digest','filename','download_url')   
#  
# class ScheduleAdmin(admin.ModelAdmin):
#     list_display = ('title','course','default','created_date','lastupdated_date','created_by')
# 
# class SectionAdmin(admin.ModelAdmin):
#     list_display = ('course','title','order')
#   
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('name','created_date','created_by','description','order_priority','highlight')
#     ordering = ['-order_priority','name'] 
#     
# class ClientAdmin(admin.ModelAdmin):
#     list_display = ('name', 'mobile_number', 'gender', 'marital_status', 'age', 'parity', 'life_stage', 'user')
#     
# class CourseCohortAdmin(admin.ModelAdmin):        
#     list_display = ('course','cohort')        
#        
# class CourseManagerAdmin(admin.ModelAdmin):        
#     list_display = ('user', 'course')
#     
# admin.site.register(Activity, ActivityAdmin)   
# admin.site.register(ActivitySchedule,ActivityScheduleAdmin)
# admin.site.register(Award, AwardAdmin)
# admin.site.register(Badge,BadgeAdmin)
# admin.site.register(AwardCourse,AwardCourseAdmin)
# admin.site.register(Cohort, CohortAdmin)                    
# admin.site.register(Course,CourseAdmin)
# admin.site.register(CourseTag,CourseTagAdmin)
# admin.site.register(Media, MediaAdmin)
# admin.site.register(Message)
# admin.site.register(Participant, ParticipantAdmin)
# admin.site.register(Points,PointsAdmin)
# admin.site.register(Schedule, ScheduleAdmin)
# admin.site.register(Section,SectionAdmin)
# admin.site.register(Tag,TagAdmin)
# admin.site.register(Tracker, TrackerAdmin)
# admin.site.register(UserProfile, UserProfileAdmin)
# admin.site.register(CourseCohort, CourseCohortAdmin)
# admin.site.register(CourseManager, CourseManagerAdmin)
# admin.site.register(Client, ClientAdmin)