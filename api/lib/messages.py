# -*- coding: utf-8 -*-
from django.contrib import messages

def flash(request, title, text, level='info'):
    """
    利用django的message系统发送一个信息。
    """
    level_map = {
        'info': messages.INFO,
        'debug': messages.DEBUG,
        'success': messages.SUCCESS,
        'warning': messages.WARNING,
        'error': messages.ERROR
    }

    level = level_map[level]
    messages.add_message(request, level, text, extra_tags=title)