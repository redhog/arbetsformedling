# -*- coding: utf-8 -*-
import appomatic_arbetsformedling.models
import django.forms
import django.shortcuts
import django.http
import django.template.defaultfilters
import autocomplete_light
from django.utils.translation import ugettext_lazy as _
import django.contrib.auth.decorators
import djangomail.models

class ProjectForm(django.forms.ModelForm):
    class Meta:
        model = appomatic_arbetsformedling.models.Project
        exclude = ('owner', 'slug', 'signups')
        widgets = autocomplete_light.get_widgets_dict(appomatic_arbetsformedling.models.Project)


class SkillForm(django.forms.ModelForm):
    class Meta:
        model = appomatic_arbetsformedling.models.Skill
        exclude = ('slug',)

def skills(request):
    skills = appomatic_arbetsformedling.models.Skill.objects.all()

    return django.shortcuts.render(request, 'appomatic_arbetsformedling/skills.html', {
        'skills': skills,
    })

@django.contrib.auth.decorators.login_required
def skill_create(request):
    if request.method == 'POST':
        form = SkillForm(request.POST, request.FILES)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.slug = django.template.defaultfilters.slugify(skill.name)
            skill.save()
            form.save_m2m()
            if "_popup" in request.GET:
                return django.http.HttpResponse("""
                    <script type="text/javascript">
                        opener.dismissAddAnotherPopup(
                            window,
                            "%(id)s",
                            "%(name)s"
                        );
                    </script>
                    """ % {"name": skill.name, "id": skill.id})
            else:
                return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse('appomatic_arbetsformedling.views.skill', kwargs={"name": skill.slug}))
    else:
        form = SkillForm()

    return django.shortcuts.render(request, 'appomatic_arbetsformedling/skill_edit.html', {
        'form': form,
        'is_new': True
    })

def skill(request, name):
    skill = appomatic_arbetsformedling.models.Skill.objects.get(slug=name)

    return django.shortcuts.render(request, 'appomatic_arbetsformedling/skill.html', {
        'skill': skill,
    })

def projects(request):
    if request.user.is_authenticated():
        projects = request.user.profile.matching_projects()
    else:
        projects = appomatic_arbetsformedling.models.Project.objects.all().order_by('created')[:10]

    return django.shortcuts.render(request, 'appomatic_arbetsformedling/projects.html', {
            'projects': projects,
            })


@django.contrib.auth.decorators.login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.slug = django.template.defaultfilters.slugify(project.name)
            project.owner = request.user.profile
            project.save()
            form.save_m2m()
            return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse('appomatic_arbetsformedling.views.project', kwargs={"name": project.slug}))
    else:
        form = ProjectForm()

    return django.shortcuts.render(request, 'appomatic_arbetsformedling/project_edit.html', {
        'form': form,
        'is_new': True
    })

def project(request, name):
    project = appomatic_arbetsformedling.models.Project.objects.get(slug=name)

    return django.shortcuts.render(request, 'appomatic_arbetsformedling/project.html', {
        'project': project,
    })

@django.contrib.auth.decorators.login_required
def project_edit(request, name):
    project = appomatic_arbetsformedling.models.Project.objects.get(slug=name)
    assert project.owner.id == request.user.profile.id
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            form.save_m2m()
            return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse('appomatic_arbetsformedling.views.project', kwargs={"name": project.slug}))
    else:
        form = ProjectForm(instance=project)

    return django.shortcuts.render(request, 'appomatic_arbetsformedling/project_edit.html', {
        'form': form,
    })

@django.contrib.auth.decorators.login_required
def project_signup(request, name):
    project = appomatic_arbetsformedling.models.Project.objects.get(slug=name)
    project.signups.add(request.user.profile)

    djangomail.models.MailTask.objects.get(name="signup").send(
        [project.owner.user], 
        project=project,
        signer=request.user.profile,
        SITE_URL=django.contrib.sites.models.Site.objects.get_current().domain)

    return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse('appomatic_arbetsformedling.views.project', kwargs={"name": project.slug}))

@django.contrib.auth.decorators.login_required
def project_signdown(request, name):
    project = appomatic_arbetsformedling.models.Project.objects.get(slug=name)
    project.signups.remove(request.user.profile)

    djangomail.models.MailTask.objects.get(name="signdown").send(
        [project.owner.user], 
        project=project,
        signer=request.user.profile,
        SITE_URL=django.contrib.sites.models.Site.objects.get_current().domain)

    return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse('appomatic_arbetsformedling.views.project', kwargs={"name": project.slug}))
