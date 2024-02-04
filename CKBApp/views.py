
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import datetime
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from CKBApp.create_repositories import create_github_repository
#from create_repositories import create_github_repositories
from .forms import InvitationForm, LoginForm, PermissionForm, RegistrationForm, TeamRegistrationForm, TournamentCreationForm
from .models import Battle, Invite, Student, Educator, StudentBattleRanking, Team, TeamBattleRanking, Tournament, TournamentRanking, User
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404

def home_student_view(request):
    #create_github_repositories()
    # Get the user ID from the session
    user_id = request.session.get('user_id')
    # Retrieve the student associated with the user ID
    student = Student.objects.get(user_id=user_id)
    student_name = student.user.name
    current_date = timezone.now().date()
    user_tournaments_ongoing = student.tournaments.filter(submission_deadline__gte=current_date)
    user_tournaments_expired = student.tournaments.filter(submission_deadline__lt=current_date)
    all_tournaments_expired = Tournament.objects.filter(submission_deadline__lt=current_date)
    user = User.objects.get(id=user_id)

    invites = Invite.objects.filter(user_invited=user)

    # Filter out tournaments where the submission deadline has passed
    available_tournaments = Tournament.objects.filter(submission_deadline__gte=current_date).exclude(pk__in=student.tournaments.all())
    
    return render(request, 'CKBApp/HomePageStudent.html', {'student_name': student_name, 'all_tournaments_expired': all_tournaments_expired ,'user_tournaments_ongoing': user_tournaments_ongoing, 'user_tournaments_expired': user_tournaments_expired, 'available_tournaments': available_tournaments, 'invites': invites})


def invite_friends_view(request, battle_id):
    battle = Battle.objects.get(id=battle_id)
    user_id = request.session.get('user_id')
    student = Student.objects.get(user_id=user_id)
    user = User.objects.get(id=user_id)
    invitation_form = InvitationForm()
    team = Team.objects.get(battle=battle, creator=user)

    if request.method == 'POST':
        invitation_form = InvitationForm(request.POST)
        if invitation_form.is_valid():
            mate_email = invitation_form.cleaned_data['mate_email']
            try:
                invited_user = User.objects.get(email=mate_email)
            except User.DoesNotExist:
                messages.error(request, "User with the given name does not exist.")
                return render(request, 'CKBApp/InviteFriends.html')
            if Invite.objects.filter(team=team, user_invited=invited_user).exists():
                # Display an error message if an invitation already exists
                messages.error(request, 'This student has already been invited to join the team.')
            else:
                # Get the user ID from the session
                user_id = request.session.get('user_id')
                creator_user= User.objects.get(id=user_id)

                student = Student.objects.get(user_id=user_id)

                # Create a new Team instance
                invite = Invite (
                    user_invited = invited_user,
                    user_who_invite = creator_user,
                    team = team,
                    accepted = False
                )
                invite.save()
                invitation_form = InvitationForm()     
        else:
           invitation_form = InvitationForm()     
    
    context = {
        'battle_name' : battle.name,
        'team_name': team.name,
        'battle_max_team_stud' : battle.max_team_students,
        'battle_min_team_stud' : battle.min_team_students,
        'invitation_form': invitation_form,   
    }
    return render(request, 'CKBApp/InviteFriends.html', context)

     
def enrolled_tournament_view(request, tournament_id):
    # Get the user ID from the session
    user_id = request.session.get('user_id')
    # Retrieve the student associated with the user ID
    student = Student.objects.get(user_id=user_id)
    user = User.objects.get(id=user_id)
    student_name = student.user.name
    student_id = student.id
    if request.method == 'POST':
        # Get the tournament to enroll in
        tournament = Tournament.objects.get(pk=tournament_id)
        current_date = timezone.now().date()
        if current_date <= tournament.submission_deadline:
            existing_ranking = TournamentRanking.objects.filter(student=student, tournament=tournament).exists()
            if not existing_ranking:
                student.tournaments.add(tournament)
                tournament_ranking = TournamentRanking (
                    student = student,
                    tournament = tournament
                )
                tournament_ranking.save()
    tournament = Tournament.objects.get(pk=tournament_id)
    battles = Battle.objects.filter(tournament=tournament)
    enrolled_battles = battles.filter(team__students=student)
    battle_team_created = enrolled_battles.filter(team__creator=user)
    today = datetime.now().date()

    tournament_name = tournament.name
    
    context = {
            'tournament': tournament,
            'tournament_name': tournament_name,
            'battles': battles,
            'student_name': student_name,
            'student' : student,
            'enrolled_battles': enrolled_battles,
            'battle_team_created': battle_team_created,
            'today': today
    }
    return render(request, 'CKBApp/EnrolledTournamentDetails.html', context)


def tournament_ranking_view(request, tournament_id):
   # Retrieve the tournament details using the tournament_id
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    tournament_rankings = TournamentRanking.objects.filter(tournament=tournament).order_by('-score')
    context = {
        'tournament': tournament,
        'tournament_rankings': tournament_rankings
    }
    return render(request, 'CKBApp/Ranking.html', context)

def home_educator_view(request):
    # Get the user ID from the session
    user_id = request.session.get('user_id')
    # Retrieve the educator associated with the user ID
    educator = Educator.objects.get(user_id=user_id)
    educator_name = educator.user.name
    user_tournaments = educator.tournaments.all()
    other_tournaments = Tournament.objects.exclude(pk__in=[tournament.pk for tournament in user_tournaments])
    return render(request, 'CKBApp/HomePageEducator.html', {'user_tournaments': user_tournaments, 'other_tournaments': other_tournaments,'educator_name': educator_name})

def ongoing_tournament_details_view(request, tournament_id):
    try:
        tournament = Tournament.objects.get(pk=tournament_id)
        battles = Battle.objects.filter(tournament=tournament)
        context = {
            'tournament': tournament,
            'battles': battles,
        }
        return render(request, 'CKBApp/OngoingTournamentStatus.html', context)
    except Tournament.DoesNotExist:
        # Handle case where tournament does not exist
        return render(request, 'CKBApp/tournament_not_found.html')

def tournament_details_view(request, tournament_id):
    # Get the user ID from the session
    user_id = request.session.get('user_id')
    # Retrieve the educator associated with the user ID
    educator = Educator.objects.get(user_id=user_id)
    educator_name = educator.user.name
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    permission_form = PermissionForm(prefix='permission_form')

    if request.method == 'POST':
        if 'create_battle_form' in request.POST:
            name = request.POST.get('name')
            registration_deadline = request.POST.get('registration_deadline')
            submission_deadline = request.POST.get('submission_deadline')
            max_team_students = request.POST.get('maximum_number_of_students')
            min_team_students = request.POST.get('minimum_number_of_students')
            registration_deadline = datetime.strptime(registration_deadline, '%Y-%m-%d').date()
            submission_deadline = datetime.strptime(submission_deadline, '%Y-%m-%d').date()
            github_username = request.POST.get('github_username')
            
            code_kata = request.FILES.get('code_kata')

            # Create a new Battle instance
            battle = Battle(
                        name=name,
                        tournament=tournament,
                        registration_deadline = registration_deadline,
                        submission_deadline = submission_deadline,
                        max_team_students = int(max_team_students),
                        min_team_students = int(min_team_students),
                        code_kata= code_kata
                    )
            current_date = timezone.now().date()
            if current_date <= battle.registration_deadline and current_date <= battle.submission_deadline and battle.registration_deadline <= battle.submission_deadline:
                if battle.registration_deadline >= tournament.submission_deadline and battle.submission_deadline >= tournament.submission_deadline:
                    existing_battle = Battle.objects.filter(name=battle.name, tournament=tournament).exists()
                    if not existing_battle:
                        battle.save()     
     
        elif 'permission_form' in request.POST:  # Check if the permission form is submitted
                permission_form = PermissionForm(request.POST, prefix='permission_form')  # Add prefix to distinguish form fields
                if permission_form.is_valid():
                    educator_granted = permission_form.cleaned_data['educator_granted']
                    # Check if an educator with the specified name exists
                    try:
                        educator_granted = Educator.objects.get(user__name=educator_granted)
                        # Add the tournament to the list of tournaments associated with the educator
                        tournament = get_object_or_404(Tournament, pk=tournament_id)
                        educator_granted.tournaments.add(tournament)
                        messages.success(request, f'Tournament added to {educator_granted}')
                    except Educator.DoesNotExist:
                        messages.error(request, f'Educator with the name "{educator_granted}" does not exist.')
                    permission_form = PermissionForm(prefix='permission_form')
    else:
        permission_form = PermissionForm(prefix='permission_form')         
    try:
        tournament = Tournament.objects.get(pk=tournament_id)
        battles = Battle.objects.filter(tournament=tournament)
        today = datetime.now().date()
        context = {
            'tournament': tournament,
            'educator_name': educator_name,  
            'battles': battles,
            'permission_form': permission_form,
            'today': today
        }
        return render(request, 'CKBApp/TournamentDetails.html', {**context})
    except Tournament.DoesNotExist:
        # Handle case where tournament does not exist
        return render(request, 'CKBApp/tournament_not_found.html')

def battle_details_view(request, battle_id):
   # Retrieve the battle details using the battle_id
    battle = get_object_or_404(Battle, pk=battle_id)
    team_battle_rankings = TeamBattleRanking.objects.filter(battle=battle).order_by('-score')
    student_battle_rankings = StudentBattleRanking.objects.filter(battle=battle).order_by('-score')
    enrolled_teams = Team.objects.filter(battle=battle_id)
    current_date = datetime.now().date()
    tournament = Tournament.objects.get(battle=battle)
     
    # Create a dictionary to store the mapping between students and their teams
    enrolled_students = {}

    # Iterate over each enrolled team
    for team in enrolled_teams:
        # Retrieve all the students associated with the current team
        students_in_team = Student.objects.filter(teams=team)
        # Store the students and their team in the dictionary
        for student in students_in_team:
            student_battle_ranking = student_battle_rankings.filter(student=student).first()
            enrolled_students[student_battle_ranking] = team

    github_repo_url = None
    if not battle.repository_created:
        if current_date > battle.registration_deadline:
            # Assuming code_kata_file is the FileField containing the code kata file
            code_kata_file = battle.code_kata        
            github_repo_url = create_github_repository(tournament.name, battle.name, code_kata_file)
            battle.url_repository = github_repo_url
            battle.repository_created = True
            battle.save()


    context = {
        'battle': battle,
        'enrolled_teams': enrolled_teams,
        'enrolled_students': enrolled_students,
        'team_battle_rankings': team_battle_rankings,
        'student_battle_rankings': student_battle_rankings,
        'github_repo_url': github_repo_url
    }
    return render(request, 'CKBApp/ViewBattleDetails.html', context)


def close_tournament_view(request, tournament_id):
    if request.method == 'POST':
        # Retrieve the tournament object
        tournament = get_object_or_404(Tournament, pk=tournament_id)
        # Delete the tournament from the database
        tournament.delete()
        # Redirect to a success page or home page
        return redirect('home-educator')  # Change 'home-educator' to the name of your educator's home page URL pattern
    else:
        # Handle invalid request method (GET)
        return redirect('home-educator')  # Redirect to the home page or an appropriate page

def registration_view(request): 
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            if User.objects.filter(email=email).exists():
                # Display an error message in the form
                messages.error(request, 'User with this email already exists.')

            else:
                # Create a new User instance
                password = form.cleaned_data['password']
                hashed_password = make_password(password)
                user = User(
                    email=email,
                    name=form.cleaned_data['name'],
                    surname=form.cleaned_data['surname'],
                    password=hashed_password,
                    user_type=form.cleaned_data['user_type'],
                    github_username = form.cleaned_data['github_username']
                )
                user.save()

                if user.user_type == 'student':
                    Student.objects.create(user=user)
                elif user.user_type == 'educator':
                    Educator.objects.create(user=user)

                
                if user is not None:
                    request.session['user_id'] = user.id
                    # Redirect to the appropriate home page
                    if user.user_type == 'student':
                        return redirect('home-student')
                    elif user.user_type == 'educator':
                        return redirect('home-educator')
                else:
                    # Handle authentication failure
                    messages.error(request, 'Failed to log in after registration.')

    
    else:
        form = RegistrationForm()

    return render(request, 'CKBApp/Registration.html', {'form': form})

    


def check_email_exists(request):
    email = request.GET.get('email', None)
    data = {'exists': User.objects.filter(email=email).exists()}
    return JsonResponse(data)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Retrieve the user based on the provided email
            user = User.objects.filter(email=email, user_type='student').first()
            
            if user is not None:
                
                # Check if the entered password matches the hashed password in the database
                if check_password(password, user.password):
                    # Password matches, perform login
                    request.session['user_id'] = user.id
                    # Redirect to a success page or homepage
                    return redirect ('home-student')
                else:
                    # Handle incorrect password
                    messages.error(request, 'Invalid password')
            else:
                # Handle user not found
                messages.error(request, 'User not found')
        else:
            # Handle invalid form submission
            messages.error(request, 'Invalid form submission')
    else:
        form = LoginForm()

    return render(request, 'CKBApp/login.html', {'form': form})


def loginEducator_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Retrieve the user based on the provided email
            user = User.objects.filter(email=email, user_type='educator').first()
            
            if user is not None:
                
                # Check if the entered password matches the hashed password in the database
                if check_password(password, user.password):
                    # Password matches, perform login
                    request.session['user_id'] = user.id
                    # Redirect to a success page or homepage
                    return redirect('home-educator')
                else:
                    # Handle incorrect password
                    messages.error(request, 'Invalid password')
            else:
                # Handle user not found
                messages.error(request, 'User not found')
        else:
            # Handle invalid form submission
            messages.error(request, 'Invalid form submission')
    else:
        form = LoginForm()

    return render(request, 'CKBApp/loginEducator.html', {'form': form})

def create_tournament_view(request):
    if request.method == 'POST':
        form = TournamentCreationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Tournament.objects.filter(name=name).exists():
                # Display an error message in the form
                messages.error(request, 'Tournament with this name already exists.')
            else:
               # Get the user ID from the session
                user_id = request.session.get('user_id')
                # Retrieve the educator associated with the user ID
                educator = Educator.objects.get(user_id=user_id)

                # Create a new Tournament instance
                tournament = Tournament(
                    name=name,
                    description=form.cleaned_data['description'],
                    submission_deadline=form.cleaned_data['submission_deadline'],
                    ending_date=form.cleaned_data['ending_date']   
                )
                tournament.save()
                educator.tournaments.add(tournament)
                form = TournamentCreationForm()
            
    else:
        form = TournamentCreationForm()

    return render(request, 'CKBApp/TournamentCreation.html', {'form': form})


def logoutEducator_view(request):
    logout(request)
    # Redirect to a logout success page or homepage
    return redirect('loginEducator-page')

def logout_view(request):
    logout(request)
    # Redirect to a logout success page or homepage
    return redirect('login-page')

def home_view(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    if user.user_type == 'student':
        return redirect('home-student')
    elif user.user_type == 'educator':
        return redirect('home-educator')


def join_battle_view(request, battle_id):
    battle = Battle.objects.get(id=battle_id)

    team_registration_form = TeamRegistrationForm()

    if request.method == 'POST':
        team_registration_form = TeamRegistrationForm(request.POST)
        if team_registration_form.is_valid():
            team_name = team_registration_form.cleaned_data['team_name']
            if Team.objects.filter(name=team_name,battle=battle).exists():
                # Display an error message in the form
                messages.error(request, 'Team with this name already exists in this battle.')
            else:
                # Get the user ID from the session
                user_id = request.session.get('user_id')
                creator_user= User.objects.get(id=user_id)
                # Retrieve the student associated with the user ID
                student = Student.objects.get(user_id=user_id)

                # Create a new Team instance
                team = Team(
                    name=team_name,
                    num_members=1,
                    battle=battle,
                    creator= creator_user,
                )
                team.save()
                student.teams.add(team)
                team_battle_ranking = TeamBattleRanking(
                    team=team,
                    battle=battle
                )
                team_battle_ranking.save()
                student_battle_ranking = StudentBattleRanking(
                    student=student,
                    battle=battle
                )
                student_battle_ranking.save()
                team_registration_form = TeamRegistrationForm()       
        else:
            team_registration_form = TeamRegistrationForm()

    context = {
        'battle_name' : battle.name,
        'battle_max_team_stud' : battle.max_team_students,
        'battle_min_team_stud' : battle.min_team_students,
        'team_registration_form': team_registration_form,   
    }

    
    return render(request, 'CKBApp/JoinBattlePage.html', context)


def check_enrollment(request, battle_id):
    
    try:
        # Retrieve the battle and student objects
        battle = Battle.objects.get(id=battle_id)
        # Get the user ID from the session
        user_id = request.session.get('user_id')
        # Retrieve the student associated with the user ID
        student = Student.objects.get(user_id=user_id)

        is_part_of_team = student.teams.filter(battle=battle).exists()

        # Return the enrollment status as JSON response
        return JsonResponse({'is_part_of_team': is_part_of_team})

    except (Battle.DoesNotExist, Student.DoesNotExist):
        # Return error response if battle or student not found
        return JsonResponse({'error': 'Battle or student not found'}, status=404)
    


def joinTeam(request, team_id, battle_id, invite_id):
    team = Team.objects.get(id=team_id)
    battle = Battle.objects.get(id=battle_id)
    tournament = Tournament.objects.get(id=battle.tournament.id)
    invite = Invite.objects.get(id=invite_id)
    joined = False
    
    current_date = timezone.now().date()
    if current_date <= battle.registration_deadline:
        if not invite.accepted:
            if team.num_members < battle.max_team_students:
                # Get the user ID from the session
                user_id = request.session.get('user_id')
                # Retrieve the student associated with the user ID
                student = Student.objects.get(user_id=user_id)

                # Check if the student is already a member of the team
                if student.teams.filter(id=team_id).exists():
                    # Student is already a member of the team, return without joining again
                    invite.delete()
                    return JsonResponse({'joined': joined})
                
                # Check if the student has already enrolled in the battle with another team
                if student.teams.filter(battle=battle).exists():
                    # Student has already enrolled in the battle with another team, return without joining
                    invite.delete()
                    return JsonResponse({'joined': joined})
                

                team.num_members = team.num_members + 1
                team.save()
                student.teams.add(team)
                joined = True
                invite.accepted = True
                invite.save()
                invite.delete()
                student_battle_ranking = StudentBattleRanking(
                    student=student,
                    battle=battle
                )
                student_battle_ranking.save()
                current_date = timezone.now().date()
                if current_date <= tournament.submission_deadline:
                    existing_ranking = TournamentRanking.objects.filter(student=student, tournament=tournament).exists()
                    if not existing_ranking:
                        student.tournaments.add(tournament)
                        tournament_ranking = TournamentRanking (
                            student = student,
                            tournament = tournament
                        )
                        tournament_ranking.save()
                return JsonResponse({'joined': joined})
        else:
            return JsonResponse({'joined': joined})


def evaluate_battle_view(request, battle_id):
    battle = Battle.objects.get(id=battle_id)
    tournament = Tournament.objects.get(id=battle.tournament.id)
    battle_teams = Team.objects.filter(battle=battle)

    # Create a dictionary to store the mapping between students and their teams
    battle_students = {}

    # Iterate over each battle team
    for team in battle_teams:
        # Retrieve all the students associated with the current team
        students_in_team = Student.objects.filter(teams=team)
        # Store the students and their team in the dictionary
        for student in students_in_team:
            battle_students[student] = team
    

    if request.method == 'POST':
        for team in battle_teams:
            # Retrieve form data
            score = int(request.POST.get(f'score_{team.id}'))
            team_id = request.POST.get(f'teamid_{team.id}')
            team = Team.objects.get(id=team_id)
            team_battle_ranking = TeamBattleRanking.objects.get(team=team, battle=battle)
            team_battle_ranking.score = (team_battle_ranking.score + score)/2
            team_battle_ranking.save()
        for student in battle_students:
            # Retrieve form data
            score = int(request.POST.get(f'score_{student.id}'))
            student_battle_ranking = StudentBattleRanking.objects.get(student=student, battle=battle)
            student_battle_ranking.score = int((student_battle_ranking.score + score)/2)
            student_battle_ranking.save()
            tournament_ranking = TournamentRanking.objects.get(student=student, tournament=tournament)
            tournament_ranking.score = tournament_ranking.score + student_battle_ranking.score
            tournament_ranking.save()
        battle.manually_evaluated = True
        battle.save()
        return redirect('tournament-details', tournament_id=tournament.id)

    context = {
        'battle_teams' : battle_teams,
        'battle_students': battle_students,
    }

    return render(request, 'CKBApp/Evaluate.html', context)

@csrf_exempt
def manage_payload(request):
    print(request)
    if request.method == 'POST':
        # Extract data from the request
        data = json.loads(request.body)
        github_username = data.get('students_email')
        tests_output = data.get('tests_output')
        repo = data.get('repo')
        url_repository = "https://github.com/" + repo

        stringa_senza_spazi = tests_output.replace(" ", "")

        # Rimuovi i caratteri '{' e '}' per ottenere un oggetto JSON valido
        stringa_json = stringa_senza_spazi.replace("'", "\"")

        # Carica la stringa JSON in un dizionario
        dati = json.loads(stringa_json)

        # Estrai i valori di test_failed e test_collected
        tests_failed = int(dati.get('tests_failed'))
        tests_collected = int(dati.get('tests_collected'))
        test_passed = tests_collected-tests_failed

        print(github_username)
        print(tests_output)
        print(url_repository)
        print(test_passed)

        # Find the user
        user = User.objects.get(github_username=github_username)
        #Find the student
        student = Student.objects.get(user=user)
        print(student)
        # Find the battle
        battle = Battle.objects.get(url_repository=url_repository)
        #!!!!!!!!url_repository dovrebbe essere unique per fare sta cosa quindi
        #vorrei cambiare il nome con cui la crea concatenando il nome del torneo
        
        #Get the team
        team = student.teams.filter(battle=battle).first()
        print(team.name)

        # Update TeamBattleRanking score
        team_battle_ranking = TeamBattleRanking.objects.get(team=team)
        team_battle_ranking.score = test_passed*10
        team_battle_ranking.save()
        
        # Update StudentBattleRanking score
        student_battle_ranking = StudentBattleRanking.objects.get(student=student,battle=battle)
        student_battle_ranking.score = test_passed*10
        student_battle_ranking.save()
    return HttpResponse(status=200) 
    #else:
            #return HttpResponse(status=405)  # Method Not Allowed