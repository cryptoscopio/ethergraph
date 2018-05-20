from django.contrib import admin
from django.urls import path, re_path

from etherscanner.views import CSVAddressView

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('address/(?P<address>0x[0-9a-zA-z]{40})/csv/$', CSVAddressView.as_view()),
]
