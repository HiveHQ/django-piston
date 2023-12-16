from blogserver.blog.models import Blogpost
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext


def posts(request):
    posts = Blogpost.objects.all()

    return render(
        request,
        "posts.html",
        {"posts": posts},
    )


def test_js(request):
    return render(
        request,
        "test_js.html",
        {},
    )
