from logging import PlaceHolder
from msilib.schema import ListView
from operator import truediv
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown
from django.shortcuts import redirect, render
from django import forms
from . import util

import time                             # for random seed
import random

t = time.localtime(time.time())         # get current local time
ss = int(t.tm_sec % 10) * 10
random.seed(ss)                          # seeding current system time

class TitleForm(forms.Form):
    Title = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Entry Title (no special character)', 'style': 'width: 300px;', 'class': 'form-control'}))
class ContentForm(forms.Form):
    Content = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Entry Contents using Markdown syntax', 
        'style': 'width: 80%; height: 80vh',  'class': 'form-control'}))
class EditForm(forms.Form):
    #overwrite __init__
    def __init__(self, title):
        #call standard __init__
        super().__init__()
        #extend __init__    
        self.fields["edit"] = forms.CharField(label = "Show me what you got !", 
            widget=forms.Textarea(attrs={ 'style': 'width: 80%; height: 80vh; color:black;',  
            'class': 'form-control'}), 
            initial=util.get_entry(title))
    #edit = forms.CharField()

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entries(request, title):
    if util.get_entry(title):
        return render(request, "encyclopedia/entries.html", {
            "content": markdown.markdown(util.get_entry(title)),
            "title": title
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "content": "The requested entry doest not exist!",
            "title": title
        })
    
def newpage(request):
    
    if request.method == "POST":                    # Check if method is POST
        
        title = TitleForm(request.POST)             # Take in the data the user submitted and save it as form
        content = ContentForm(request.POST)        

        if title.is_valid() and content.is_valid():     # Check if form data is valid (server-side)
            tt = title.cleaned_data["Title"]            # Isolate the task from the 'cleaned' version of form data
            cc = content.cleaned_data["Content"]    

            # Check if entry matches existed entry
            entries = util.list_entries()
            for entry in entries:
                if tt == entry:
                    # some error message
                    return render(request, "encyclopedia/newpage.html", {
                        "title": TitleForm(),
                        "content": ContentForm()
                    })
            util.save_entry(tt, cc)

            # redirect to new entry's page
            return HttpResponseRedirect(reverse("encyclopedia:entries", kwargs={'title':tt}))

        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/newpage.html", {
                # some error message
                "title": TitleForm(),
                "content": ContentForm()
            })

    else:
        return render(request, "encyclopedia/newpage.html", {
            "title": TitleForm(),
            "content": ContentForm()
        })

def rand(request):
    lists = util.list_entries()     
    n = len(lists) - 1
    rand_num = random.randint(0, n)
    list = lists[rand_num]
    # Redirect user a random entry
    return HttpResponseRedirect(reverse("encyclopedia:entries", kwargs={'title':list})) 

def edit(request, title):
    if request.method == "POST":
        #return HttpResponseRedirect(reverse("encyclopedia:entries", kwargs={'title':title}))
    
        util.save_entry(title, bytes(request.POST['edit'], 'utf8'))
        # redirect to edited entry's page
        return HttpResponseRedirect(reverse("encyclopedia:entries", kwargs={'title':title}))

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": EditForm(title = title)
    })

def search(request):
    query = request.GET['q']

    entries = util.list_entries()
    substring_list = []
    for entry in entries:
        # If the query matches the name of an encyclopedia entry,
        if entry.lower() == query.lower():
            return HttpResponseRedirect(reverse("encyclopedia:entries", kwargs={'title': entry}))  

        elif query.lower() in entry.lower():
            substring_list.append(entry)
    # If the query does not match the name of an encyclopedia entry, query as a substring
    return render(request, "encyclopedia/search.html", {
        "title": query,
        "queries": substring_list
    })