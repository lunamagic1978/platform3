# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import HttpResponseRedirect

# Create your views here.


@login_required
def index(request):
    return render(request, 'index.html', )


def login(request):
    return render(request, 'login.html', )


def login_action(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            response = HttpResponseRedirect('/index')
            request.session['user'] = username
            return response
        else:
            return render(request, 'login.html', {'error': 'username or password error'})


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/index/')
