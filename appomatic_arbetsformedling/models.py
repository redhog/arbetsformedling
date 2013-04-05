import django.db.models
import django.contrib.auth.models
import mptt.models

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile
from django.db import models
from django.conf import settings
import djangomail.models
import django.contrib.sites.models

class Skill(mptt.models.MPTTModel):
    name = django.db.models.CharField(max_length=50, unique=True)
    slug = django.db.models.SlugField(max_length=50, unique=True)
    parent = mptt.models.TreeForeignKey('self', null=True, blank=True, related_name='children')
    description = django.db.models.TextField(null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return django.core.urlresolvers.reverse("appomatic_arbetsformedling.views.skill", kwargs={'name': self.slug})


class Profile(UserenaBaseProfile):
    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='profile')
    skills = django.db.models.ManyToManyField(Skill, related_name="people", null=True, blank=True)

    send_project_email = django.db.models.BooleanField("Send emails about matching projects", blank=True)

    def matching_projects(self, limit = 10):
        projects = list(Project.objects.raw("""
          select
            *
          from
            appomatic_arbetsformedling_project p
          order by
            (select
               count(*)
             from
               appomatic_arbetsformedling_project_required_skills ps
               join appomatic_arbetsformedling_profile_skills us on
                 p.id = ps.project_id
                 and us.profile_id = %s
                 and us.skill_id = ps.skill_id) desc,
            created desc
          limit %s
        """, [self.id, limit]))

        skills = dict((skill.id, skill) for skill in self.skills.all())
        for project in projects:
            project.matching_skills = []
            for skill in project.required_skills.all():
                if skill.id in skills:
                    project.matching_skills.append(skill)
        return projects
    
    def get_absolute_url(self):
        return django.core.urlresolvers.reverse("userena.views.profile", kwargs={'username': self.user.username})


class Project(django.db.models.Model):
    """A project has a set of required skills and/or a set of roles. Skills not required in a role can be provided by any combination of people"""

    name = django.db.models.CharField(max_length=50, unique=True)
    slug = django.db.models.SlugField(max_length=50, unique=True)
    summary = django.db.models.TextField(null=True, blank=True)
    description = django.db.models.TextField(null=True, blank=True)
    #image = django.db.models.ImageField(upload_to=settings.MEDIA_ROOT, null=True, blank=True)
    link = django.db.models.CharField(max_length=1024, null=True, blank=True)

    owner = models.ForeignKey(Profile, related_name='own_projects')
    created = django.db.models.DateTimeField(auto_now_add = True)

    required_skills = django.db.models.ManyToManyField(Skill, related_name="projects", null=True, blank=True)
    

    signups = django.db.models.ManyToManyField(Profile, related_name="projects", null=True, blank=True)

    def __unicode__(self):
        return self.name

    def matching_people(self, limit=10):
        q = [self.id]
        sql = """
          select
            *
          from
            (select
               *,
               (select
                  count(*)
                from
                  appomatic_arbetsformedling_project_required_skills ps
                  join appomatic_arbetsformedling_profile_skills us on
                    p.id = us.profile_id
                    and ps.project_id = %s
                    and us.skill_id = ps.skill_id) as matching_nr
             from
               appomatic_arbetsformedling_profile p
            ) as a
          where
            matching_nr > 0
        """
        if limit:
            q.append(limit)
            sql += " limit %s"
        profiles = list(Profile.objects.raw(sql, q))
        
        required_skills = dict((skill.id, skill) for skill in self.required_skills.all())
        for profile in profiles:
            profile.matching_skills = []
            for skill in profile.skills.all():
                if skill.id in required_skills:
                    profile.matching_skills.append(skill)
        return profiles

    def get_absolute_url(self):
        return django.core.urlresolvers.reverse("appomatic_arbetsformedling.views.project", kwargs={'name': self.slug})


@django.dispatch.receiver(django.db.models.signals.m2m_changed, sender=Project.required_skills.through)
def handler(sender, instance, **kwargs):
    djangomail.models.MailTask.objects.get(name="new_project").send(
        [profile.user
         for profile in instance.matching_people(None)
         if profile.send_project_email], 
        project=instance,
        SITE_URL="http://" + django.contrib.sites.models.Site.objects.get_current().domain)
