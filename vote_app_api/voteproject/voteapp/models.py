from django.db import models

# Create your models here.
class Election(models.Model):
    name          = models.CharField(max_length=100, unique = True)
    election_date = models.DateTimeField()
    is_active     = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
#Candidat    
class Candidate(models.Model):
    election       = models.ForeignKey(Election, on_delete=models.CASCADE)
    first_name     = models.CharField(max_length=100)
    last_name      = models.CharField(max_length=100)
    tagline        = models.CharField(max_length=250, null=True)
    vote_count     = models.IntegerField(default = 0,editable=False)
    picture        = models.ImageField(upload_to='photos/', null=True)
    
    class Meta:
        unique_together = ('election', 'first_name','last_name')
    
    def __str__(self):
        return self.name
    
#Votant    
class Voter(models.Model):
    email    = models.EmailField(unique=True)
    is_valid = models.BooleanField(default=False)   
    otp      = models.CharField(max_length=100)
    # token = models.CharField(max_length=100, unique=True)
    # has_voted = models.BooleanField(default=False)
    # voted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email
    
    
class Subscribe(models.Model):
    election  = models.ForeignKey(Election, on_delete=models.CASCADE)
    voter     = models.ForeignKey(Voter, on_delete=models.CASCADE)
    token     = models.CharField(max_length=100, unique=True)
    has_voted = models.BooleanField(default=False)
    vote_date = models.DateTimeField(null=True, blank=True)
    # Autres champs pour les propriétés supplémentaires
    class Meta:
        unique_together = ('election', 'voter',)

    def __str__(self):
        return f"{self.voter.email} voted for {self.election.name}"


