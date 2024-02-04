from django.db import models
from django.contrib.auth.models import User

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    submission_deadline = models.DateField()
    ending_date = models.DateField()
    def __str__(self):
        return self.name

class Battle(models.Model):
    name = models.CharField(max_length=100)
    registration_deadline = models.DateField()
    submission_deadline = models.DateField()
    max_team_students = models.IntegerField()
    min_team_students = models.IntegerField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    manually_evaluated = models.BooleanField(default=False)
    code_kata = models.FileField(upload_to='media/', blank= False, default= None)
    repository_created = models.BooleanField(default=False)
    url_repository = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.name


class User(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    user_type = models.CharField(max_length=50)
    github_username = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"{self.name} {self.surname}"

class Team(models.Model):
    name = models.CharField(max_length=100)
    num_members = models.IntegerField()
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, default=None)
    def __str__(self):
        return self.name
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tournaments = models.ManyToManyField(Tournament, related_name='students', blank=True)
    teams = models.ManyToManyField(Team, related_name='students', blank=True)
    def __str__(self):
        return f"Student: {self.user.name} {self.user.surname}"

class Educator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tournaments = models.ManyToManyField(Tournament, related_name='educators', blank=True)
    battles_managed = models.ManyToManyField(Battle, related_name='educators', blank=True)
    def __str__(self):
        return f"Educator: {self.user.name} {self.user.surname}"

class Invite(models.Model):
    user_invited = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invites_received')
    user_who_invite = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invites_sent')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    def __str__(self):
        return f"Invite from {self.user_who_invite} to {self.user_invited} for team {self.team}"

class TournamentRanking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank= False)
    score = models.IntegerField(default=0)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, blank= False)
    def __str__(self):
        return f"Tournament Ranking: Student {self.student.user.name} - Score: {self.score} - Tournament: {self.tournament.name}"
    
class TeamBattleRanking(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank= False)
    score = models.IntegerField(default=0)
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, blank= False)
    def __str__(self):
        return f"Team: {self.team.name} | Battle: {self.battle.name} | Score: {self.score}"
    
class StudentBattleRanking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank= False)
    score = models.IntegerField(default=0)
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, blank= False)
    def __str__(self):
        return f"Student: {self.student.user.name} {self.student.user.surname} | Battle: {self.battle.name} | Score: {self.score}"
    
class Repository(models.Model):
    battle = models.ForeignKey('Battle', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    link = models.CharField(max_length=255)