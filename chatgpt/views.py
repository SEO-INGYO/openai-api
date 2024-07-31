from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils.crypto import get_random_string
from .models import ChatSession, ChatMessage


@csrf_exempt
def get_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        model = request.POST.get('model')
        api_key = request.POST.get('key')
        session_id = request.POST.get('session_id')

        if not api_key:
            return JsonResponse({'error': 'API key is required'}, status=400)

        client = OpenAI(api_key=api_key)

        if user_message:
            if not session_id:
                session_id = get_random_string(24)
                chat_session = ChatSession.objects.create(session_id=session_id)
            else:
                chat_session = get_object_or_404(ChatSession, session_id=session_id)

            ChatMessage.objects.create(chat_session=chat_session, sender='user', message=user_message)

            messages = []
            previous_conversations = chat_session.messages.all().order_by('created_at')
            for conv in previous_conversations:
                messages.append({"role": "user", "content": conv.message} if conv.sender == 'user' else {"role": "assistant", "content": conv.message})

            messages.append({"role": "user", "content": user_message})

            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                )

                final_answer = []

                for chunk in completion:
                    chunk_content = chunk.choices[0].delta.content
                    if chunk_content is not None:
                        final_answer.append(chunk_content)

                bot_response = ''.join([str(content) for content in final_answer if content is not None])

                print(bot_response)

                ChatMessage.objects.create(
                    chat_session=chat_session,
                    sender='assistant',
                    message=bot_response
                )

                return JsonResponse({'response': bot_response, 'session_id': session_id})
            except Exception as e:
                print(e)
                return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def home(request):
    sessions = ChatSession.objects.all()
    return render(request, 'chatgpt/chat.html', {'sessions': sessions})


def get_session_history(request):
    session_id = request.GET.get('session_id')
    chat_session = get_object_or_404(ChatSession, session_id=session_id)
    messages = chat_session.messages.all().order_by('created_at')
    history = []
    for message in messages:
        history.append({
            'user': message.message if message.sender == 'user' else None,
            'bot': message.message if message.sender == 'assistant' else None
        })
    return JsonResponse({'history': history})
