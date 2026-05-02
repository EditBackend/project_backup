import os
import subprocess
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def github_webhook(request):
    if request.method == "POST":
        # Loyiha papkasiga o'tish (username va loyiha nomini o'zingiznikiga o'zgartiring)
        repo_dir = '/home/SmartTalim/Smart-Talim-BackEnd/'
        # https: // www.pythonanywhere.com / user / Hacker99000 /
        # GitHub'dan yangi kodni tortish (pull)
        subprocess.run(['git', 'pull', 'origin', 'main'], cwd=repo_dir)

        # PythonAnywhere serverini avtomatik qayta ishga tushirish (reload)
        wsgi_file = '/var/www/SmartTalim_pythonanywhere_com_wsgi.py'
        subprocess.run(['touch', wsgi_file])

        return HttpResponse("Server muvaffaqiyatli yangilandi!", status=200)

    return HttpResponse("Faqat POST so'rovlar qabul qilinadi", status=405)