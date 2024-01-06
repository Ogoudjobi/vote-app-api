from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from django.urls import reverse
from django.http import HttpResponse

from voteapp.models import *
from voteapp.serializers import *


# Create your views here.
class ElectionViewSet(viewsets.ModelViewSet):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer
    
    
class VoterViewSet(viewsets.ModelViewSet):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer
    
    
class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    
    
class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer
    
    
class ValidateOTPView(APIView):
    def post(self, request):
        serializer = ValidateOTPSerializer(data=request.data)
        if serializer.is_valid():
            
            # Le serializer a validé l'adresse e-mail et l'OTP avec succès
            # Mettez à jour votre logique ici après la validation réussie de l'OTP
            # Par exemple, activez le votant ou effectuez toute autre action requise
            # return Response({"message": "L'OTP a été validé avec succès."})
            votant = Voter.objects.get(email=serializer["email"].value)
            # return redirect('/api/subscribe-election/',kwargs={'voter_id': serializer["email"]})
            # redirection_url = reverse('subscribe_election', kwargs={'voter_id': f'{votant.id}'})
            redirection_url = '/api/vote/'
            return redirect(redirection_url)
        else:
            return Response(serializer.errors, status=400)
        
        
def subscribe_election(request, voter_id ):
    if voter_id:
        # Faites quelque chose avec l'email, comme valider, enregistrer, etc.
        return HttpResponse(f"L'id récupéré depuis l'URL est : {voter_id}")
    else:
        return HttpResponse("Aucun email n'a été spécifié dans l'URL.")
    
    
class VoteCreateAPIView(APIView):
    def post(self, request, format=None):
        serializer = VoteSerializer(data=request.data)
        if serializer.is_valid():
            # Ajoutez ici la logique pour valider et enregistrer le vote
            # Exemple : serializer.save()

            # Renvoie une réponse appropriée si le vote a été enregistré avec succès
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class BatchEmailViewSet(viewsets.ModelViewSet):
    queryset = BatchEmail.objects.all()
    serializer_class = BatchEmailSerializer

    def create(self, request, *args, **kwargs):
        # Récupérer les données de la requête POST
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Valider et enregistrer le vote
        serializer.save()  # Cela dépendra de la logique de votre application pour enregistrer le vote
        
        return Response(serializer.data)