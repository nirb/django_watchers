import time
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from core.defs import *
from core.docs_analyzer import InvestmentsAnalayzer
from django.core.cache import cache

from utils.cache import is_analyze_ready, on_analyze_done
from utils.parallel import run_in_thread


class FileUploadForm(forms.Form):
    file = forms.FileField(label="")


@login_required
def ai_view(request):
    context = {"form": None, "file_name": None,
               "task_completed": TASK_COMPLETED}
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            context["file_name"] = uploaded_file.name
            context["task_id"] = f"ai_task:{int(time.time())}"
            with uploaded_file.open('rb') as file:
                cache.set(ANALYZE_RESULT_KEY, "")
                ia = InvestmentsAnalayzer(file)
                run_in_thread(ia.analyze,
                              context["task_id"], on_analyze_done)
                # let the thread start using the file
                # without the delay, the file will be closed
                time.sleep(.5)
    else:
        form = FileUploadForm()
        context["form"] = form

    print("ai_view", cache.get(ANALYZE_RESULT_KEY))
    if is_analyze_ready():
        return redirect('/create_event/')

    return render(request, "ai.html", context)
