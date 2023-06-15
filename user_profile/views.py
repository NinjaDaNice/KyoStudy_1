from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from main import forms
from main.forms import MyForm
from main.models import UsersInfo, Subjects, SubjectLists, Topics, Topic_theory, Topic_task, UserTask, UserTheory, \
    UserTopic, Theory_question, Task_question, Leveltest_question, UserLeveltests


# Create your views here.

def profile_page(request, username):
    user = User.objects.get(username=username)
    fname = user.first_name
    email = user.email
    UserObject = User.objects.get(email=email)
    user_id = UserObject.id
    request.session['fname'] = fname
    request.session['email'] = email
    request.session['user_id'] = user_id
    userinfo = UsersInfo.objects.get(id=user_id)
    phone_number = userinfo.phone_number
    avatar = userinfo.avatar_img
    if userinfo.subjects_list_id is not None:
        subjects_list_id = userinfo.subjects_list_id.subjects_list_id
        user_subjects = SubjectLists.objects.get(subjects_list_id=subjects_list_id)
        subjects_list = Subjects.objects.filter(subject_id__in=user_subjects.subjects)
    else:
        if user.is_staff:
            subjects_list = Subjects.objects.filter(teacher=user)
        else:
            subjects_list = []
    request.session['phone'] = phone_number
    request.session['avatar'] = avatar

    # request.session['subjects'] = subjects_list
    return render(request, 'user_profile/profile.html', {'userinfo': userinfo,
                                                         'email': email,
                                                         'fname': fname,
                                                         'user_id': user_id,
                                                         'phone': phone_number,
                                                         'avatar': avatar,
                                                         'subjects': subjects_list
                                                         })


def subject_page(request, subject_id, username):
    subject_instance = Subjects.objects.get(subject_id=subject_id)

    topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)
    user = User.objects.get(username=username)
    subject = Subjects.objects.get(subject_id=subject_id)

    # Get all topics related to the subject
    topics = Topics.objects.filter(topic_id__in=subject.topics)

    all_topics_tasks = Topic_task.objects.filter(task_topic__in=topics)
    all_topics_theory = Topic_theory.objects.filter(theory_topic__in=topics)

    total_topics = topics.count()
    completed_topics = 0
    user_topics = UserTopic.objects.filter(user=user)
    # Iterate over each topic and check if the user has completed it
    for topic in topics:
        total_tasks = Topic_task.objects.filter(task_topic=topic).count()
        total_theory = Topic_theory.objects.filter(theory_topic=topic).count()
        user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic, completed=True).count()
        user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic,
                                                            completed=True).count()

        if user_tasks_completed + user_theories_completed == total_tasks + total_theory:
            completed_topics += 1

    if total_topics > 0:
        completion_percentage = (completed_topics / total_topics) * 100
    else:
        completion_percentage = 0

    return render(request, 'user_profile/subject.html', {
        'subject_instance': subject_instance,
        'topics_list': topic_list,
        'completion_percentage': completion_percentage,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'all_topics_tasks': all_topics_tasks,
        'all_topics_theory': all_topics_theory,
        'user_topics': user_topics,
    })


def topic_page(request, topic_id, subject_id, username):
    user = User.objects.get(username=username)

    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topic_instance = Topics.objects.get(topic_id=topic_id)
    theory_list = Topic_theory.objects.filter(theory_topic=topic_instance)
    task_list = Topic_task.objects.filter(task_topic=topic_instance)
    total_activities = theory_list.count() + task_list.count()

    user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic_instance, completed=True).count()
    user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic_instance,
                                                        completed=True).count()

    try:
        tasks_progress_percentage = (user_tasks_completed / task_list.count()) * 100
    except:
        tasks_progress_percentage = 0

    try:
        theory_progress_percentage = (user_theories_completed / theory_list.count()) * 100
    except:
        theory_progress_percentage = 0

    tasks_progress_percentage = round(tasks_progress_percentage, 1)
    theory_progress_percentage = round(theory_progress_percentage, 1)

    user_tasks = UserTask.objects.filter(user=user, task__task_topic=topic_instance)
    user_theories = UserTheory.objects.filter(user=user, theory__theory_topic=topic_instance)

    return render(request, 'user_profile/topic.html', {
        'subject_instance': subject_instance,
        'topic_instance': topic_instance,
        'topic_theorys': theory_list,
        'topic_tasks': task_list,
        'total_activities': total_activities,
        'completed_activities': user_tasks_completed + user_theories_completed,
        'user_tasks': user_tasks,
        'user_theories': user_theories,
        'tasks_progress_percentage': tasks_progress_percentage,
        'theory_progress_percentage': theory_progress_percentage,
    })


def task_page(request, topic_id, subject_id, topic_task_id, username):
    user = User.objects.get(username=username)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topic_instance = Topics.objects.get(topic_id=topic_id)
    topic_task_instance = Topic_task.objects.get(topic_task_id=topic_task_id)
    if not user.is_staff:
        usertask = UserTask.objects.get(user_id=user.id, task_id=topic_task_instance.topic_task_id)

    if not user.is_staff:
        userleveltest = UserLeveltests.objects.get(User=user)
    try:
        if usertask.submitted == True and userleveltest.is_completed == False:

            submitted_task = Task_question.objects.get(user_submitted=user.id,
                                                       question_task=topic_task_instance.topic_task_id,
                                                       question_topic=topic_instance.topic_id)
        else:
            submitted_task = 0
    except:
        submitted_task = 0
    if not user.is_staff:
        check_task_is_submitted = UserTask.objects.get(user=user, task=topic_task_instance)
    else:
        check_task_is_submitted = False

    return render(request, 'user_profile/task.html', {
        'subject_instance': subject_instance,
        'topic_instance': topic_instance,
        'topic_task_instance': topic_task_instance,
        'check_task_is_submitted': check_task_is_submitted,
        'submitted_task': submitted_task,
    })


def theory_page(request, username, topic_id, subject_id, topic_theory_id):
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topic_instance = Topics.objects.get(topic_id=topic_id)
    topic_theory_instance = Topic_theory.objects.get(topic_theory_id=topic_theory_id)
    user = User.objects.get(username=username)
    topic_theory_questions = Theory_question.objects.filter(question_theory=topic_theory_instance,
                                                            question_topic=topic_instance)

    if not user.is_staff:
        is_completed = UserTheory.objects.get(user=user, theory_id=topic_theory_id).completed
    else:
        is_completed = False

    return render(request, 'user_profile/topic-theory.html', {
        'subject_instance': subject_instance,
        'topic_instance': topic_instance,
        'topic_theory_instance': topic_theory_instance,
        'topic_theory_questions': topic_theory_questions,
        'is_completed': is_completed,
    })


def edit_profile_page(request, username):
    user = User.objects.get(username=username)
    usersinfo = UsersInfo.objects.get(id=user)
    subjects_lists = SubjectLists.objects.all()

    img_link = usersinfo.avatar_img
    return render(request, 'user_profile/edit_profile.html', {
        'subjects_lists': subjects_lists,
        'avatar_link': img_link,
        'username': username,
    })


def edit_profile_action(request, username):
    if request.method == 'POST':
        # Retrieve the user's profile
        profile = User.objects.get(username=username)
        usersinfo = UsersInfo.objects.get(id=profile)
        # Update the profile fields with the submitted data
        usersinfo.phone_number = request.POST.get('phone_number')
        usersinfo.birth_date = request.POST.get('birth_date')
        usersinfo.avatar_img = request.POST.get('avatar_img')
        subjects = request.POST.get('subjects_list_id')

        subject_list_id = SubjectLists.objects.get(subjects_list_id=subjects)
        usersinfo.subjects_list_id = subject_list_id
        usersinfo.grade = request.POST.get('grade')

        # Save the updated profile
        usersinfo.save()

        # Display a success message
        messages.success(request, 'Profile updated successfully.')

        user = User.objects.get(username=username)
        fname = user.first_name
        email = user.email
        UserObject = User.objects.get(email=email)
        user_id = UserObject.id
        request.session['fname'] = fname
        request.session['email'] = email
        request.session['user_id'] = user_id
        userinfo = UsersInfo.objects.get(id=user_id)
        phone_number = userinfo.phone_number
        avatar = userinfo.avatar_img
        if userinfo.subjects_list_id is not None:
            subjects_list_id = userinfo.subjects_list_id.subjects_list_id
            user_subjects = SubjectLists.objects.get(subjects_list_id=subjects_list_id)
            subjects_list = Subjects.objects.filter(subject_id__in=user_subjects.subjects)
        else:
            subjects_list = []
        request.session['phone'] = phone_number
        request.session['avatar'] = avatar

        return render(request, 'user_profile/edit_profile.html', {
            'subjects_lists': subjects_list,
            'avatar_link': avatar,
            'username': username,
        })


def submitting(request, username, subject_id, topic_id, topic_task_id):
    user = User.objects.get(username=username)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topic_instance = Topics.objects.get(topic_id=topic_id)
    topic_task_instance = Topic_task.objects.get(topic_task_id=topic_task_id)

    if request.method == 'POST':
        print(request.POST.get('question_field1_hidden'))
        Task_question.objects.create(
            question_field1=request.POST.get('question_field1_hidden'),
            question_field2=request.POST.get('question_field2_hidden'),
            question_field3=request.POST.get('question_field3_hidden'),
            question_field4=request.POST.get('question_field4_hidden'),
            question_field5=request.POST.get('question_field5_hidden'),
            question_field6=request.POST.get('question_field6_hidden'),
            question_field7=request.POST.get('question_field7_hidden'),
            question_field8=request.POST.get('question_field8_hidden'),
            question_field9=request.POST.get('question_field9_hidden'),
            question_field10=request.POST.get('question_field10_hidden'),
            question_answer=request.POST.get('question_answer_hidden'),
            question_topic=topic_instance,
            question_task=topic_task_instance,
            user_submitted=user,
            question_text=topic_task_instance.task_body,
            checked=False
        )

        theory_list = Topic_theory.objects.filter(theory_topic=topic_instance)
        task_list = Topic_task.objects.filter(task_topic=topic_instance)
        total_activities = theory_list.count() + task_list.count()

        user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic_instance,
                                                       completed=True).count()
        user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic_instance,
                                                            completed=True).count()
        try:
            tasks_progress_percentage = (user_tasks_completed / task_list.count()) * 100
        except:
            tasks_progress_percentage = 0

        try:
            theory_progress_percentage = (user_theories_completed / theory_list.count()) * 100
        except:
            theory_progress_percentage = 0

        tasks_progress_percentage = round(tasks_progress_percentage, 1)
        theory_progress_percentage = round(theory_progress_percentage, 1)

        user_tasks = UserTask.objects.filter(user=user, task__task_topic=topic_instance)
        user_theories = UserTheory.objects.filter(user=user, theory__theory_topic=topic_instance)

        return render(request, 'user_profile/topic.html', {'subject_instance': subject_instance,
                                                           'topic_instance': topic_instance,
                                                           'topic_theorys': theory_list,
                                                           'topic_tasks': task_list,
                                                           'total_activities': total_activities,
                                                           'completed_activities': user_tasks_completed + user_theories_completed,
                                                           'user_tasks': user_tasks,
                                                           'user_theories': user_theories,
                                                           'tasks_progress_percentage': tasks_progress_percentage,
                                                           'theory_progress_percentage': theory_progress_percentage, })
    return redirect('home')


def check_answers(request, topic_theory_id, topic_id, subject_id, username):
    user = User.objects.get(username=username)
    subject_instance = Subjects.objects.get(subject_id=subject_id)

    topic_instance = Topics.objects.get(topic_id=topic_id)
    topic_theory_instance = Topic_theory.objects.get(topic_theory_id=topic_theory_id)
    questions = Theory_question.objects.filter(question_topic=topic_instance, question_theory=topic_theory_instance)
    if request.method == 'POST':
        # Get the submitted form data
        submitted_answers = {}
        for key in request.POST:
            if key.startswith('answer_'):
                question_id = key.split('_')[1]
                answer = request.POST[key]
                submitted_answers[question_id] = answer
        # Get the correct answers from the database
        correct_answers = {}
        for question in questions:
            correct_answers[str(question.id)] = question.question_answer  ##12 04

        # Compare the submitted answers with the correct answers
        total_questions = len(correct_answers)
        correct_count = 0
        for question_id, submitted_answer in submitted_answers.items():
            if submitted_answer == correct_answers[question_id]:
                correct_count += 1

        # Calculate the percentage of correct answers

        questions_count = Theory_question.objects.filter(question_topic_id=topic_id,
                                                         question_theory_id=topic_theory_id).count()

        if (questions_count > 0):
            percentage_correct = (correct_count / total_questions) * 100
        else:
            percentage_correct = 100

        if not user.is_staff:
            user_theory_instance = UserTheory.objects.get(user=user, theory_id=topic_theory_id)
            user_theory_instance.completed = True
            user_theory_instance.grade = int(percentage_correct)
            user_theory_instance.save()

        theory_list = Topic_theory.objects.filter(theory_topic=topic_instance)
        task_list = Topic_task.objects.filter(task_topic=topic_instance)
        total_activities = theory_list.count() + task_list.count()

        user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic_instance,
                                                       completed=True).count()
        user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic_instance,
                                                            completed=True).count()

        try:
            tasks_progress_percentage = (user_tasks_completed / task_list.count()) * 100
        except:
            tasks_progress_percentage = 0

        try:
            theory_progress_percentage = (user_theories_completed / theory_list.count()) * 100
        except:
            theory_progress_percentage = 0

        tasks_progress_percentage = round(tasks_progress_percentage, 1)
        theory_progress_percentage = round(theory_progress_percentage, 1)

        user_tasks = UserTask.objects.filter(user=user, task__task_topic=topic_instance)
        user_theories = UserTheory.objects.filter(user=user, theory__theory_topic=topic_instance)

        # Pass the percentage to the result template
        return render(request, 'user_profile/topic.html', {'subject_instance': subject_instance,
                                                           'topic_instance': topic_instance,
                                                           'topic_theorys': theory_list,
                                                           'topic_tasks': task_list,
                                                           'total_activities': total_activities,
                                                           'completed_activities': user_tasks_completed + user_theories_completed,
                                                           'user_tasks': user_tasks,
                                                           'user_theories': user_theories,
                                                           'tasks_progress_percentage': tasks_progress_percentage,
                                                           'theory_progress_percentage': theory_progress_percentage, })

    return redirect('home')


def create_topic(request, subject_id, username):
    user = User.objects.get(username=username)
    subject = Subjects.objects.get(subject_id=subject_id)
    # Get all topics related to the subject

    if request.method == 'POST':
        new_topic = Topics(
            topic_name=request.POST.get('topic_name')
        )
        new_topic.save()
        subject.topics.append(new_topic.topic_id)
        subject.save()
    messages.success(request, 'Topic created successfully.')
    subject = Subjects.objects.get(subject_id=subject_id)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topics = Topics.objects.filter(topic_id__in=subject.topics)
    topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)
    all_topics_tasks = Topic_task.objects.filter(task_topic__in=topics)
    all_topics_theory = Topic_theory.objects.filter(theory_topic__in=topics)

    total_topics = topics.count()
    completed_topics = 0
    user_topics = UserTopic.objects.filter(user=user)
    # Iterate over each topic and check if the user has completed it
    for topic in topics:
        total_tasks = Topic_task.objects.filter(task_topic=topic).count()
        total_theory = Topic_theory.objects.filter(theory_topic=topic).count()
        user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic, completed=True).count()
        user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic,
                                                            completed=True).count()

        if user_tasks_completed + user_theories_completed == total_tasks + total_theory:
            completed_topics += 1

    if total_topics > 0:
        completion_percentage = (completed_topics / total_topics) * 100
    else:
        completion_percentage = 0

    return render(request, 'user_profile/subject.html', {
        'subject_instance': subject_instance,
        'topics_list': topic_list,
        'completion_percentage': completion_percentage,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'all_topics_tasks': all_topics_tasks,
        'all_topics_theory': all_topics_theory,
        'user_topics': user_topics,
    })


def get_theories(request):
    topic_id = request.GET.get('topic_id')
    theories = Topic_theory.objects.filter(theory_topic_id=topic_id)
    theory_list = [{'theory_name': theory.theory_name} for theory in theories]
    return JsonResponse(theory_list, safe=False)


def create_theory(request, subject_id, username):
    user = User.objects.get(username=username)
    subject = Subjects.objects.get(subject_id=subject_id)
    topic_instance = Topics.objects.get(topic_id=request.POST.get('theory_topic_id'))
    # Get all topics related to the subject

    if request.method == 'POST':
        new_theory = Topic_theory(
            theory_name=request.POST.get('theory_name'),
            theory_topic=topic_instance,
            theory_body=request.POST.get('theory_body'),
            theory_video=request.POST.get('theory_video'),

        )
        new_theory.save()

    messages.success(request, 'Theory created successfully.')
    subject = Subjects.objects.get(subject_id=subject_id)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topics = Topics.objects.filter(topic_id__in=subject.topics)
    topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)
    all_topics_tasks = Topic_task.objects.filter(task_topic__in=topics)
    all_topics_theory = Topic_theory.objects.filter(theory_topic__in=topics)

    total_topics = topics.count()
    completed_topics = 0
    user_topics = UserTopic.objects.filter(user=user)
    # Iterate over each topic and check if the user has completed it
    for topic in topics:
        total_tasks = Topic_task.objects.filter(task_topic=topic).count()
        total_theory = Topic_theory.objects.filter(theory_topic=topic).count()
        user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic, completed=True).count()
        user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic,
                                                            completed=True).count()

        if user_tasks_completed + user_theories_completed == total_tasks + total_theory:
            completed_topics += 1

    if total_topics > 0:
        completion_percentage = (completed_topics / total_topics) * 100
    else:
        completion_percentage = 0

    return render(request, 'user_profile/subject.html', {
        'subject_instance': subject_instance,
        'topics_list': topic_list,
        'completion_percentage': completion_percentage,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'all_topics_tasks': all_topics_tasks,
        'all_topics_theory': all_topics_theory,
        'user_topics': user_topics,
    })


def create_task(request, subject_id, username):
    user = User.objects.get(username=username)
    subject = Subjects.objects.get(subject_id=subject_id)
    topic_instance = Topics.objects.get(topic_id=request.POST.get('task_topic_id'))
    # Get all topics related to the subject

    if request.method == 'POST':
        new_task = Topic_task(
            task_name=request.POST.get('task_name'),
            task_topic=topic_instance,
            task_body=request.POST.get('task_body'),

        )
        new_task.save()

    messages.success(request, 'Task created successfully.')
    subject = Subjects.objects.get(subject_id=subject_id)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topics = Topics.objects.filter(topic_id__in=subject.topics)
    topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)
    all_topics_tasks = Topic_task.objects.filter(task_topic__in=topics)
    all_topics_theory = Topic_theory.objects.filter(theory_topic__in=topics)

    total_topics = topics.count()
    completed_topics = 0
    user_topics = UserTopic.objects.filter(user=user)
    # Iterate over each topic and check if the user has completed it
    for topic in topics:
        total_tasks = Topic_task.objects.filter(task_topic=topic).count()
        total_theory = Topic_theory.objects.filter(theory_topic=topic).count()
        user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic, completed=True).count()
        user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic,
                                                            completed=True).count()

        if user_tasks_completed + user_theories_completed == total_tasks + total_theory:
            completed_topics += 1

    if total_topics > 0:
        completion_percentage = (completed_topics / total_topics) * 100
    else:
        completion_percentage = 0

    return render(request, 'user_profile/subject.html', {
        'subject_instance': subject_instance,
        'topics_list': topic_list,
        'completion_percentage': completion_percentage,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'all_topics_tasks': all_topics_tasks,
        'all_topics_theory': all_topics_theory,
        'user_topics': user_topics,
    })


def create_leveltest_question(request, subject_id, username):
    user = User.objects.get(username=username)
    subject = Subjects.objects.get(subject_id=subject_id)

    topic_instance = Topics.objects.get(topic_id=request.POST.get('leveltest_topic'))

    # Get all topics related to the subject

    if request.method == 'POST':
        new_leveltest_question = Leveltest_question(
            leveltest_topic=topic_instance,
            leveltest_text=request.POST.get('leveltest_text'),
            leveltest_var1=request.POST.get('leveltest_var1'),
            leveltest_var2=request.POST.get('leveltest_var2'),
            leveltest_var3=request.POST.get('leveltest_var3'),
            leveltest_var4=request.POST.get('leveltest_var4'),
            leveltest_answer=request.POST.get('leveltest_answer')
        )
        new_leveltest_question.save()

    messages.success(request, 'Leveltest question created successfully.')
    subject = Subjects.objects.get(subject_id=subject_id)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topics = Topics.objects.filter(topic_id__in=subject.topics)
    topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)
    all_topics_tasks = Topic_task.objects.filter(task_topic__in=topics)
    all_topics_theory = Topic_theory.objects.filter(theory_topic__in=topics)

    total_topics = topics.count()
    completed_topics = 0
    user_topics = UserTopic.objects.filter(user=user)
    # Iterate over each topic and check if the user has completed it
    for topic in topics:
        total_tasks = Topic_task.objects.filter(task_topic=topic).count()
        total_theory = Topic_theory.objects.filter(theory_topic=topic).count()
        user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic, completed=True).count()
        user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic,
                                                            completed=True).count()

        if user_tasks_completed + user_theories_completed == total_tasks + total_theory:
            completed_topics += 1

    if total_topics > 0:
        completion_percentage = (completed_topics / total_topics) * 100
    else:
        completion_percentage = 0

    return render(request, 'user_profile/subject.html', {
        'subject_instance': subject_instance,
        'topics_list': topic_list,
        'completion_percentage': completion_percentage,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'all_topics_tasks': all_topics_tasks,
        'all_topics_theory': all_topics_theory,
        'user_topics': user_topics,
    })


def check_leveltest_answers(request, subject_id, username):
    user = User.objects.get(username=username)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)

    questions = Leveltest_question.objects.filter(leveltest_topic__in=topic_list)
    topic_counts = dict()
    topic_correct_counts = dict()

    if request.method == 'POST':
        # Get the submitted form data
        submitted_answers = {}

        for key in request.POST:
            if key.startswith('answer_'):
                question_id = key.split('_')[1]
                answer = request.POST[key]
                question = Leveltest_question.objects.get(id=question_id)
                submitted_answers[question_id] = {
                    'answer': answer,
                    'topic': question.leveltest_topic.topic_name
                }

                topic_counts.setdefault(question.leveltest_topic.topic_name, 0)
                topic_counts[question.leveltest_topic.topic_name] += 1

                if answer == question.leveltest_answer:
                    topic_correct_counts.setdefault(question.leveltest_topic.topic_name, 0)
                    topic_correct_counts[question.leveltest_topic.topic_name] += 1

        # Calculate the percentage of correct answers per topic
        topic_percentages = {}

        for topic in topic_list:
            count = topic_counts.get(topic.topic_name, 0)
            correct_count = topic_correct_counts.get(topic.topic_name, 0)

            if count > 0:
                percentage = (correct_count / count) * 100
            else:
                percentage = 0

            topic_percentages[topic.topic_name] = percentage

            if percentage > 90:

                usertopic = UserTopic.objects.get(user=user, topic=topic)

                usertopic.topic_progress = percentage
                usertopic.theory_completed = topic.topic_theory_count
                usertopic.task_completed = topic.topic_task_count

                task_list = Topic_task.objects.filter(task_topic=topic)
                theory_list = Topic_theory.objects.filter(theory_topic=topic)

                usertasks = UserTask.objects.filter(user=user, task__in=task_list)
                usertheorys = UserTheory.objects.filter(user=user, theory__in=theory_list)

                for task in usertasks:
                    task.submitted = True
                    task.completed = True
                    task.grade = 100
                    task.save()

                for theory in usertheorys:
                    theory.completed = True
                    theory.grade = 100
                    theory.save()

                usertopic.save()

            messages.success(request, f"Topic: {topic.topic_name}, Correct Percentage: {percentage}%")

        # Rest of your code...
        new_leveltest_result = UserLeveltests.objects.create(
            User=user,
            is_completed=True
        )

        subject = Subjects.objects.get(subject_id=subject_id)
        subject_instance = Subjects.objects.get(subject_id=subject_id)
        topics = Topics.objects.filter(topic_id__in=subject.topics)
        topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)
        all_topics_tasks = Topic_task.objects.filter(task_topic__in=topics)
        all_topics_theory = Topic_theory.objects.filter(theory_topic__in=topics)

        total_topics = topics.count()
        completed_topics = 0
        user_topics = UserTopic.objects.filter(user=user)
        # Iterate over each topic and check if the user has completed it
        for topic in topics:
            total_tasks = Topic_task.objects.filter(task_topic=topic).count()
            total_theory = Topic_theory.objects.filter(theory_topic=topic).count()
            user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic, completed=True).count()
            user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic,
                                                                completed=True).count()

            if user_tasks_completed + user_theories_completed == total_tasks + total_theory:
                completed_topics += 1

        if total_topics > 0:
            completion_percentage = (completed_topics / total_topics) * 100
        else:
            completion_percentage = 0

        return render(request, 'user_profile/subject.html', {
            'subject_instance': subject_instance,
            'topics_list': topic_list,
            'completion_percentage': completion_percentage,
            'total_topics': total_topics,
            'completed_topics': completed_topics,
            'all_topics_tasks': all_topics_tasks,
            'all_topics_theory': all_topics_theory,
            'user_topics': user_topics,
            'topic_percentages': topic_percentages,  # Add the topic percentages to the rendered context
        })

    return redirect


def leveltest_page(request, subject_id, username):
    user = User.objects.get(username=username)
    subject = Subjects.objects.get(subject_id=subject_id)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)
    leveltest_questions = Leveltest_question.objects.filter(leveltest_topic__in=topic_list)

    return render(request, 'user_profile/leveltest.html', {
        'subject_instance': subject_instance,
        'topics_list': topic_list,
        'leveltest_questions': leveltest_questions,
    })


def create_theory_question(request, subject_id, username):
    user = User.objects.get(username=username)
    subject = Subjects.objects.get(subject_id=subject_id)

    topic_instance = Topics.objects.get(topic_id=request.POST.get('question_topic'))
    topic_theory_id = Topic_theory.objects.get(theory_topic=topic_instance,
                                               theory_name=request.POST.get('question_theory')).topic_theory_id

    topic_theory_instance = Topic_theory.objects.get(topic_theory_id=topic_theory_id)

    # Get all topics related to the subject

    if request.method == 'POST':
        new_theory_question = Theory_question(
            question_topic=topic_instance,
            question_theory=topic_theory_instance,
            question_text=request.POST.get('question_text'),
            question_var1=request.POST.get('question_var1'),
            question_var2=request.POST.get('question_var2'),
            question_var3=request.POST.get('question_var3'),
            question_var4=request.POST.get('question_var4'),
            question_answer=request.POST.get('question_answer')
        )
        new_theory_question.save()

    messages.success(request, 'Theory question created successfully.')
    subject = Subjects.objects.get(subject_id=subject_id)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    topics = Topics.objects.filter(topic_id__in=subject.topics)
    topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)
    all_topics_tasks = Topic_task.objects.filter(task_topic__in=topics)
    all_topics_theory = Topic_theory.objects.filter(theory_topic__in=topics)

    total_topics = topics.count()
    completed_topics = 0
    user_topics = UserTopic.objects.filter(user=user)
    # Iterate over each topic and check if the user has completed it
    for topic in topics:
        total_tasks = Topic_task.objects.filter(task_topic=topic).count()
        total_theory = Topic_theory.objects.filter(theory_topic=topic).count()
        user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic, completed=True).count()
        user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic,
                                                            completed=True).count()

        if user_tasks_completed + user_theories_completed == total_tasks + total_theory:
            completed_topics += 1

    if total_topics > 0:
        completion_percentage = (completed_topics / total_topics) * 100
    else:
        completion_percentage = 0

    return render(request, 'user_profile/subject.html', {
        'subject_instance': subject_instance,
        'topics_list': topic_list,
        'completion_percentage': completion_percentage,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'all_topics_tasks': all_topics_tasks,
        'all_topics_theory': all_topics_theory,
        'user_topics': user_topics,
    })


def submitted_tasks_page(request, subject_id, username):
    subject_instance = Subjects.objects.get(subject_id=subject_id)

    topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)
    user = User.objects.get(username=username)
    subject = Subjects.objects.get(subject_id=subject_id)

    # Get all topics related to the subject
    topics = Topics.objects.filter(topic_id__in=subject.topics)

    all_topics_tasks = Topic_task.objects.filter(task_topic__in=topics)
    all_topics_theory = Topic_theory.objects.filter(theory_topic__in=topics)

    all_submitted_tasks = Task_question.objects.filter(question_topic_id__in=topics)
    all_user_infos = UsersInfo.objects.all()
    total_topics = topics.count()
    completed_topics = 0
    user_topics = UserTopic.objects.filter(user=user)
    # Iterate over each topic and check if the user has completed it
    for topic in topics:
        total_tasks = Topic_task.objects.filter(task_topic=topic).count()
        total_theory = Topic_theory.objects.filter(theory_topic=topic).count()
        user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic, completed=True).count()
        user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic,
                                                            completed=True).count()

        if user_tasks_completed + user_theories_completed == total_tasks + total_theory:
            completed_topics += 1

    if total_topics > 0:
        completion_percentage = (completed_topics / total_topics) * 100
    else:
        completion_percentage = 0

    return render(request, 'user_profile/submitted_tasks.html', {
        'subject_instance': subject_instance,
        'topics_list': topic_list,
        'completion_percentage': completion_percentage,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'all_submitted_tasks': all_submitted_tasks,
        'all_topics_tasks': all_topics_tasks,
        'all_topics_theory': all_topics_theory,
        'user_topics': user_topics,
        'all_user_infos': all_user_infos,
    })


def submitted_task(request, subject_id, username, submitted_user, submitted_topic, submitted_task):
    user = User.objects.get(username=username)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    submitted_task = Task_question.objects.get(user_submitted=submitted_user, question_task=submitted_task,
                                               question_topic=submitted_topic)
    print(submitted_task)

    return render(request, 'user_profile/submitted_task_instance.html', {
        'subject_instance': subject_instance,
        'submitted_task_instance': submitted_task,
    })


def submitted_grade(request, subject_id, username, submitted_user, submitted_topic, submitted_task):
    user = User.objects.get(username=username)
    subject_instance = Subjects.objects.get(subject_id=subject_id)
    submitted_task = Task_question.objects.get(user_submitted=submitted_user, question_task=submitted_task,
                                               question_topic=submitted_topic)

    usertask = UserTask.objects.get(user_id=submitted_user, task_id=submitted_task.question_task, submitted=True)

    if request.method == 'POST':
        usertask.grade = request.POST.get('grade')
        usertask.completed = True
        usertask.save()
        submitted_task.checked = True
        submitted_task.save()

    topic_list = Topics.objects.filter(topic_id__in=subject_instance.topics)
    subject = Subjects.objects.get(subject_id=subject_id)

    # Get all topics related to the subject
    topics = Topics.objects.filter(topic_id__in=subject.topics)

    all_topics_tasks = Topic_task.objects.filter(task_topic__in=topics)
    all_topics_theory = Topic_theory.objects.filter(theory_topic__in=topics)

    all_submitted_tasks = Task_question.objects.filter(question_topic_id__in=topics)
    all_user_infos = UsersInfo.objects.all()
    total_topics = topics.count()
    completed_topics = 0
    user_topics = UserTopic.objects.filter(user=user)
    # Iterate over each topic and check if the user has completed it
    for topic in topics:
        total_tasks = Topic_task.objects.filter(task_topic=topic).count()
        total_theory = Topic_theory.objects.filter(theory_topic=topic).count()
        user_tasks_completed = UserTask.objects.filter(user=user, task__task_topic=topic, completed=True).count()
        user_theories_completed = UserTheory.objects.filter(user=user, theory__theory_topic=topic,
                                                            completed=True).count()

        if user_tasks_completed + user_theories_completed == total_tasks + total_theory:
            completed_topics += 1

    if total_topics > 0:
        completion_percentage = (completed_topics / total_topics) * 100
    else:
        completion_percentage = 0

    return render(request, 'user_profile/submitted_tasks.html', {
        'subject_instance': subject_instance,
        'topics_list': topic_list,
        'completion_percentage': completion_percentage,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'all_submitted_tasks': all_submitted_tasks,
        'all_topics_tasks': all_topics_tasks,
        'all_topics_theory': all_topics_theory,
        'user_topics': user_topics,
        'all_user_infos': all_user_infos,
    })
