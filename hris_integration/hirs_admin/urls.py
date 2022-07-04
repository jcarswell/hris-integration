# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.Index.as_view(),
         name='index'),
    path('actions/',
         views.JobActions.as_view(),
         name='actions'),
    path('actions/<str:job>',
          views.JobActions.as_view(),
         name='actions_go'),
]