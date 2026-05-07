from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from .models import ChatMessage
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def home(request):
    return render(request, 'home.html')


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('chat')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')



@login_required
def clear_chat(request):

    ChatMessage.objects.filter(
        user=request.user
    ).delete()

    return redirect('chat')
def chat_view(request):
    chats = ChatMessage.objects.filter(
        user=request.user
    ).order_by('created_at')

    if request.method == 'POST':
        user_message = request.POST.get('message')

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        bot_response = completion.choices[0].message.content

        ChatMessage.objects.create(
            user=request.user,
            user_message=user_message,
            bot_response=bot_response
        )

        return redirect('chat')

    return render(request, 'chat.html', {'chats': chats})