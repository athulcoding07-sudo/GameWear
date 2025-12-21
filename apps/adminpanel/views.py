from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.
@staff_member_required
def admin_dashboard(request):   
    """
    -show the admin dashboard
    
    """
                                                              # admin_dashboard
    return render(request, "adminpanel/dashboard.html")