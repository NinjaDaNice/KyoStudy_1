from django.contrib import admin

from main.models import UsersInfo, Subjects, SubjectLists, Topics, Topic_theory, Topic_task, UserTask, UserTheory, \
    Theory_question, UserTopic, Task_question, Leveltest_question, UserLeveltests

# Register your models here.

admin.site.register(UsersInfo)
admin.site.register(Subjects)
admin.site.register(SubjectLists)
admin.site.register(Topics)
admin.site.register(Topic_theory)
admin.site.register(Topic_task)
admin.site.register(UserTask)
admin.site.register(UserTheory)
admin.site.register(UserTopic)
admin.site.register(Theory_question)
admin.site.register(Task_question)
admin.site.register(Leveltest_question)
admin.site.register(UserLeveltests)

