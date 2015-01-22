#encoding: utf-8
from datetime import datetime, date, timedelta
import time
from jinja2 import Markup
from django import template
from django_jinja import library
from django.utils.translation import get_language, ugettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings as django_settings

from base_template import settings



register = template.Library()


@library.global_function
@register.simple_tag
def locale_switcher(request, template='base_template/common/locale_switcher.jinja'):
    locales = [lang_code for lang_code, name in django_settings.LANGUAGES]
    path = request.path
    if path[1:3] in locales:
        path = request.path[3:]
    GET = request.GET
    if hasattr(request, 'GET_backuped'):
        GET = request.GET_backuped
    if GET:
        path = u'{0}?{1}'.format(path, GET.urlencode())

    return Markup(render_to_string(template, {'path': path, 'settings': django_settings, 'current_language': get_language()}))

@library.global_function
@register.simple_tag
def get_host():
    return django_settings.HOST


@library.global_function
@register.simple_tag
def locale():
    _language = get_language()
    if _language == django_settings.LANGUAGE_CODE:
        return ''
    return '/%s' % _language


@register.simple_tag
@library.global_function
def language():
    return get_language()


def do_media(domain, path):
    return '{0}{1}?{2}'.format(domain, path, settings.MEDIA_VERSION)


@library.global_function
@register.simple_tag
def image(path):
    return do_media(settings.BASE_MEDIA_URL, path)


@library.global_function
@register.simple_tag
def static_image(path):
    return do_media(settings.STATIC_URL_IMG, path)

@library.global_function
@register.simple_tag
def stylesheet(path):
    return do_media(settings.STATIC_URL_CSS, path)


@library.global_function
@register.simple_tag
def javascript(path):
    return do_media(settings.STATIC_URL_JS, path)


@library.global_function
@register.simple_tag
def plugin(path):
    return do_media(settings.BASE_STATIC_URL, path)

@library.global_function
@register.simple_tag
def now(_format):
    return datetime.now().strftime(_format)

def human_time(d):
    mon = [_(u'января'), _(u'февраля'), _(u'марта'), _(u'апреля'), _(u'мая'), _(u'июня'),
           _(u'июля'), _(u'августа'), _(u'сентября'), _(u'октября'), _(u'ноября'), _(u'декабря'),]
    n = datetime.now()         # Текущее время
    deltas = time.mktime(n.timetuple()) - time.mktime(d.timetuple())   # Дельта в секундах
    delta = deltas / 60                 # Дельта в минутах
    if deltas < 1:
        deltas = 1
    if deltas < 60:                     # Секунды
        return _(u"%d сек. назад") % deltas
    elif delta < 60:                    # Минуты
        return _(u"%d мин. назад") % delta
    elif delta < (n.hour * 60 + n.minute):
        shour = round(delta/60)
        if shour in (1,21):
            shours = _(u"час")
        elif shour in (2,3,4,22,23,24):
            shours = _(u"часа")
        else:
            shours = _(u"часов")
        return _(u"%(hour)d %(hours)s назад") % {'hour': shour, 'hours': shours}
    elif delta < (n.hour * 60 + n.minute + 60 * 24):
        return _(u"вчера, %(hour)02d:%(minute)02d") % {'hour': d.hour, 'minute': d.minute}
    elif d.year == n.year:
        return _(u"%(day)d %(month)s") % {'day': d.day, 'month': mon[d.month - 1]}
    else:
        return _(u"%(day)d %(month)s %(year)d") % {'day':d.day, 'month': mon[d.month - 1],'year': d.year}

@register.filter
@library.filter
def human_time_from_string(time_string, _format='%Y-%m-%d %H:%M:%S'):
    try:
        obj = datetime.strptime(time_string, _format)
        return human_time(obj)
    except Exception, e:
        return str(time_string)