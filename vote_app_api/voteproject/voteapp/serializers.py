from rest_framework import serializers
from django.core.mail import send_mail
import pyotp
import secrets
import os
from datetime import date
from voteapp.models import *
from voteproject.settings import MEDIA_ROOT

def verifier_extension(fichier):
    extension = os.path.splitext(fichier)[1].lower()  # Obtenir l'extension du fichier en minuscules
    extensions_acceptees = ['.xls', '.xlsx', '.csv']  # Extensions autorisées
    
    if extension  in ['.xls', '.xlsx']:
        return "EXCEL"
    elif extension == '.csv':
        return "CSV"
    else :
        return False


def token_vote ():
    return secrets.token_urlsafe(8)
    

def generate_otp():
    # Crée un générateur OTP
    gen = pyotp.random_base32()

    totp = pyotp.TOTP(gen, digits=6,  interval=600)  # digits=6 spécifie la longueur de l'OTP à 6 chiffres
    
    # Génère l'OTP
    otp = totp.now()
    
    return otp,gen

def validate_otp_for_user(user_id, user_otp):
    # Récupérez l'utilisateur depuis la base de données (supposons que vous avez l'ID de l'utilisateur)
    user = Voter.objects.get(id=user_id)
    
    # Créez un objet TOTP avec la clé secrète de l'utilisateur (supposons que la clé secrète est stockée dans le champ 'secret_key')
    totp = pyotp.TOTP(user.otp, digits=6, interval=600)  # Utilisez les mêmes paramètres que pour la génération

    # Vérifie si l'OTP saisi correspond à celui stocké pour l'utilisateur et généré pour la même clé secrète et dans la même fenêtre de temps
    return totp.verify(user_otp)


class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = '__all__' 
        read_only_fields = ['is_active']

    
class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__' 
    
    
class VoterSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Voter
        fields = '__all__' 
        read_only_fields = ['is_valid', 'otp']
        
    def create(self, validated_data):
        email = validated_data.get('email')

        # Enregistrer l'email dans la base de données
        voter = Voter.objects.create(**validated_data)
        otp = generate_otp()
        voter.otp = otp[1]
        
        # Envoyer l'e-mail de vérification
        sujet = "   NOTIFICATION D'INSCRIPTION"
        message = f'''Bonjour ! Vous avez bien été enregistré sur la liste electorale  '''
        de = 'adsa.vote@gmail.com'  # Remplacez par votre adresse e-mail
        a = [email]  # Adresse e-mail de l'utilisateur

        send_mail(sujet, message, de, a, fail_silently=False)
        voter.save()
        return voter



class SubscribeSerializer(serializers.ModelSerializer):
    voter = serializers.PrimaryKeyRelatedField(queryset=Voter.objects.all())
    election = serializers.PrimaryKeyRelatedField(queryset=Election.objects.all())
    token = serializers.CharField(read_only=True)
    vote_date = serializers.DateTimeField(read_only=True)
    has_voted = serializers.SerializerMethodField() 
    
    class Meta:
        model = Subscribe   
        fields = ['voter', 'election', 'token', 'has_voted', 'vote_date']
        read_only_fields = ['token', 'vote_time', 'has_voted']
        unique_together = ('election', 'voter')

    
    def create(self, validated_data):
        voter = validated_data.get('voter')
        election = validated_data.get('election')
        
        
        # Enregistrer l'email dans la base de données
        vote = Subscribe.objects.create(**validated_data)
        # vote.has_voted = False
        token = token_vote()
        vote.token = token
        vote.save()

        # Envoyer l'e-mail de vérification
        sujet = f'TOKEN DE VOTE {election.name.upper()}'
        message = f'''Voici votre token pour {election.name} : {token}'''
        de = 'adsa.vote@gmail.com'  # Remplacez par votre adresse e-mail
        a = [voter.email]  # Adresse e-mail de l'utilisateur

        send_mail(sujet, message, de, a, fail_silently=False)
        return vote

    def get_has_voted(self, obj):
        # Logique pour déterminer si le vote est valide
        # Vous pouvez implémenter ici votre logique de validation du vote
        # Par exemple, vérifier si le vote a été validé ou non, etc.
        # Cette méthode renverra True ou False en fonction de votre logique
        return False 
    
    
@DeprecationWarning
class ValidateOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=100)  # Supposons que l'OTP a une longueur maximale de 6 caractères
    
    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            # Récupérez l'utilisateur depuis la base de données en fonction de l'adresse e-mail
            votant = Voter.objects.get(email=email)
            # Validez l'OTP avec celui enregistré pour cet utilisateur
            
            is_valid_otp = validate_otp_for_user(votant.id, otp)# Utilisez la méthode adaptée de votre modèle Votant pour valider l'OTP
            
            print(is_valid_otp)
            
            if not is_valid_otp:
                raise serializers.ValidationError("L'OTP saisi est incorrect.")
            else :
                votant.is_valid = True
                votant.save()
                sujet = 'Re:Vérification de votre adresse e-mail'
                message = '''Votre adresse mail a bien été validé!!!!'''
                de = 'adsa.vote@gmail.com'  # Remplacez par votre adresse e-mail
                a = [email]  # Adresse e-mail de l'utilisateur

                send_mail(sujet, message, de, a, fail_silently=False)
        except Voter.DoesNotExist:
            raise serializers.ValidationError("Aucun utilisateur avec cette adresse e-mail.")

        return attrs
    
    
    
class VoteSerializer(serializers.Serializer):
    token       = serializers.CharField(max_length=100) 
    election    = serializers.PrimaryKeyRelatedField(queryset=Election.objects.all())
    candidate   = serializers.PrimaryKeyRelatedField(queryset=Candidate.objects.all())
    
    def validate(self, attrs):
        token     = attrs.get('token')
        candidate = attrs.get('candidate')
        election  = attrs.get('election')
        

        # Enregistrer l'email dans la base de données
        subscribe = Subscribe.objects.get(token=token, election=election)
        if subscribe.has_voted:
            raise serializers.ValidationError(f"Vous avez déja voté pour : {election.name}")    
        else:
            candidate.vote_count += 1
            candidate.save()
            
            subscribe.has_voted = True
            subscribe.vote_date = date.today()
            subscribe.save()

            # Envoyer l'e-mail de vérification
            sujet = f'CONFIRMATION DE VOTE : {election.name.upper()}'
            message = f'''Votre vote a bien été pris en compte pour {election.name} '''
            de = 'adsa.vote@gmail.com'  # Remplacez par votre adresse e-mail
            a = [subscribe.voter.email]  # Adresse e-mail de l'utilisateur

            send_mail(sujet, message, de, a, fail_silently=False)
        return attrs
    
    
class BatchEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchEmail
        fields = '__all__' 
        
    def create(self, validated_data):
        import pandas as pd
        # Une fois les données validées, accédez au champ 'fichier' pour obtenir le chemin d'accès
        fichier = validated_data.get('fichier')
        fichier_ = super().create(validated_data)
        chemin_acces = os.path.join(MEDIA_ROOT,'documents',fichier.name)
        # Autres opérations après validation et accès au chemin du fichier
        # ...
        extension = verifier_extension(chemin_acces)
        if extension == "EXCEL":
            df = pd.read_excel(chemin_acces).iloc[:,0]
        elif extension == "CSV":
            df = pd.read_csv(chemin_acces, sep=';').iloc[:,0]
            
        for email in df:
            voter_serializer = VoterSerializer(data = {"email": email})
            if voter_serializer.is_valid():
                voter_instance = voter_serializer.save()

        return fichier_
    
