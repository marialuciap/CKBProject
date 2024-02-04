"""
URL configuration for CKBProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from CKBApp.views import create_tournament_view, manage_payload,home_view ,evaluate_battle_view ,joinTeam, invite_friends_view, close_tournament_view, tournament_ranking_view, tournament_details_view, login_view, loginEducator_view, home_student_view, home_educator_view, registration_view, check_email_exists, logoutEducator_view, battle_details_view, ongoing_tournament_details_view, enrolled_tournament_view, logout_view, join_battle_view, check_enrollment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login-page'),
    path('loginEducator/', loginEducator_view, name='loginEducator-page'),
    path('registration/', registration_view, name='registration-page'),
    path('home/student/', home_student_view, name='home-student'),
    path('home/educator/', home_educator_view, name='home-educator'),
    path('check-email-exists/', check_email_exists, name='check-email-exists'),
    path('createTournament/', create_tournament_view, name='create-tournament'),
    path('tournament-details/<int:tournament_id>/', tournament_details_view, name='tournament-details'),
    path('logout/', logoutEducator_view, name='logout'),
    path('logout/student/', logout_view, name='logoutStudent-page'),
    path('battle-details/<int:battle_id>/', battle_details_view, name='battle-details'),
    path('rankingTournament/<int:tournament_id>/', tournament_ranking_view , name='ranking-tournament'),
    path('close-tournament/<int:tournament_id>/', close_tournament_view, name='close-tournament'),
    path('ongoing-tournament-details/<int:tournament_id>/', ongoing_tournament_details_view, name='ongoing-tournament-details'),
    path('enrolledTo/<int:tournament_id>/', enrolled_tournament_view, name='enrolled_tournament'),
    path('join-battle/<int:battle_id>/', join_battle_view, name='join-battle'),
    path('check-enrollment/<int:battle_id>/', check_enrollment, name='check-enrollment'),
    path('invite-friends/<int:battle_id>/', invite_friends_view, name='inviteFriends-page'),
    path('joinTeam/<int:team_id>/<int:battle_id>/<int:invite_id>/', joinTeam, name='joinTeam'),
    path('evaluate-battle/<int:battle_id>/', evaluate_battle_view, name='evaluate-battle'),
    path('goHome/', home_view, name='go-home'),
    path('managePayload/', manage_payload, name='manage-payload'),
]
 