from django.urls import path
from .views import GenerateTTSView

urlpatterns = [
    path("generate_tts/", GenerateTTSView.as_view(), name="generate_tts"),
]