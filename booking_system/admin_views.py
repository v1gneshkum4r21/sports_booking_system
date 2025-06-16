from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

@staff_member_required
def qr_code_scanner(request):
    return render(request, 'admin/qr_code_scanner.html') 