from django.shortcuts import render, redirect
import openai
from django.conf import settings
import logging
import json
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'mainapp/home.html')


def tests(request):
    return render(request, 'mainapp/tests.html')


def anxiety_test(request):
    return render(request, 'mainapp/anxiety_test.html')



openai.api_key = settings.OPENAI_API_KEY
yandex_Key = settings.YANDEX_KEY
yandex_Catalog = settings.YANDEX_CATALOG

from django.http import JsonResponse
from django.shortcuts import render
import json


def psychologist_selection(request):
    """
    Представляет собой обработчик выбора психолога.
    """
    if request.method == 'GET':
        # Показ страницы выбора психолога
        return render(request, 'mainapp/psychologist_selection.html')
    elif request.method == 'POST':
        try:
            # Получаем данные из тела запроса
            data = json.loads(request.body)
            psychologist = data.get('psychologist')

            # Проверка на пустое сообщение
            if not psychologist:
                return JsonResponse({'message': 'Ошибка: не выбран психолог.'}, status=400)

            return JsonResponse({'message': f'Вы выбрали психолога: {psychologist}'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Ошибка: некорректный формат данных.'}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)
    else:
        return JsonResponse({'message': 'Ошибка: поддерживаются только методы GET и POST.'}, status=405)


def call_yandexgpt_api(messages):
    prompt = {
        "modelUri": "gpt://"+ yandex_Catalog+"/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты психолг с опытом работы более 5 лет."
            }
        ]
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key "+yandex_Key
    }

    try:
        response = requests.post(url, headers=headers, json=prompt)
        result = response.text
        print(result)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"Ошибка при обращении к YandexGPT API: {e}"

def psychologist(request):
    if request.method == 'GET':
        psychologist_name = request.GET.get('psychologist')
        return render(request, 'mainapp/psychologist.html', {'psychologist': psychologist_name})

    elif request.method == 'POST':
        try:
            # Загружаем данные из тела запроса
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            psychologist_choice = data.get('psychologist', '').strip()

            # Проверка на пустое сообщение
            if not user_message:
                return JsonResponse({'message': 'Ошибка: пустое сообщение.'}, status=400)

            # Проверка выбора психолога
            if psychologist_choice not in ['chatgpt', 'yandexgpt']:
                return JsonResponse({'message': 'Ошибка: неверный выбор психолога.'}, status=400)

            # Формирование сообщений для YandexGPT и ChatGPT
            messages = [{"role": "user", "content": user_message}]

            # Получаем ответ от соответствующей функции
            if psychologist_choice == 'chatgpt':
                bot_response = psychologist_ChatGPT(messages)
            else:
                bot_response = call_yandexgpt_api(messages)

            return JsonResponse({'message': bot_response}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Ошибка: некорректный формат данных.'}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)
    else:
        return JsonResponse({'message': 'Ошибка: поддерживается только метод POST.'}, status=405)

def psychologist_ChatGPT(messages):
    """
    Функция взаимодействия с моделью ChatGPT для генерации ответа на заданный вопрос.
    Принимает сообщения пользователя и возвращает ответ от ChatGPT.
    """
    try:
        # Отправка запроса к ChatGPT через API OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant psychologist."}] + messages
        )

        # Извлечение текста ответа из ответа API
        bot_message = response['choices'][0]['message']['content']
        return bot_message

    except Exception as e:
        # Логирование ошибки и возвращение сообщения об ошибке
        print(f"Ошибка при запросе к API OpenAI: {e}")
        return "Извините, произошла ошибка при обработке вашего запроса - " + messages[-1]['content']

def color_test(request):
    if request.method == 'POST':
        selected_colors = request.POST.getlist('colors')  # Здесь 'colors' — это name вашего input
        request.session['color_order'] = selected_colors  # Сохраняем выбранные цвета в сессии
        # Логируем состояние сессии для отладки
        print("Сохраненные цвета в сессии:", selected_colors)

        return redirect('symptom_input')

    return render(request, 'mainapp/color_test.html')



def symptom_input(request):
    if request.method == 'POST':
        symptom = request.POST.get('symptom')
        request.session['symptom'] = symptom

        # Логируем текущее состояние сессии для отладки
        print("Текущие данные сессии:", request.session.items())

        # Проверяем наличие данных о цветах в сессии
        if 'color_order' in request.session:
            return redirect('associate_words')  # Переход на страницу ассоциаций
        else:
            print("Цвета не найдены в сессии, перенаправление обратно на тест цветов.")
            return redirect('color_test')

    return render(request, 'mainapp/symptom_input.html')


from django.shortcuts import render


def associate_words(request):
    symptom = request.session.get('symptom')
    color_order = request.session.get('color_order', [])

    colors = ['blue', 'green', 'red', 'yellow', 'purple', 'brown', 'black', 'gray']
    selected_colors = [colors[int(color) - 1] for color in color_order]

    concepts = [
        "Семейная жизнь", "Настоящий/-ая Я", "Будущее", "Здоровье", "Прошлое", "Развод",
        "Болезнь", "Одиночество", "1-я любовь", "Мама", "Деньги", "Секс", "Работа",
        "Измена", "Самоубийство", "Алкоголь", "Дом", "Дети", symptom, "Обида",
        "Наркотики", "Скука", "Собственный характер", "Идеальный мужчина",
        "Мой характер — когда симптом исчезнет", "Характер мамы", "Обман", "Смерть",
        "Проблемы", "Общение с людьми", "Партнер(супруг)", "Мой характер с моим симптомом",
        "Отдых", "Радость", "Отец", "Симулирование", "Неудача", "Усталость",
        "Свободное время", "Идеальная женщина", "Моя профессия", "Характер отца",
        "Гнев", "Спокойствие", "Машина", "Достижение успеха", "Мои обязанности",
        "Презрение", "Печаль", "Учеба", "Кровать", "Награда", "Тревога",
        "Страх", "Родина", "Риск", "Грусть", "Любовь", "Депрессия",
        "Вдохновение", "Угроза", "Хобби", "Дружба"
    ]

    return render(request, 'mainapp/associate_words.html', {
        'symptom': symptom,
        'selected_colors': selected_colors,
        'color_order': color_order,
        'concepts': concepts,
    })


def interpret_results(request):
    # Получаем порядок цветов и понятия из сессии
    color_order = request.session.get('color_order')
    word_associations = request.session.get('word_associations')
    # Обрабатываем результаты и отображаем интерпретацию
    return render(request, 'mainapp/interpret_results.html', {
        'color_order': color_order,
        'word_associations': word_associations,
    })


def submit_anxiety_test(request):
    if request.method == 'POST':
        # Сбор результатов теста
        total_score = 0

        for i in range(1, 22):  # 21 симптом
            score = request.POST.get(f'symptom{i}', 0)  # Получаем значение от 0 до 3
            total_score += int(score)

        # Перенаправляем на страницу интерпретации с общим баллом
        return redirect('interpretation', total_score=total_score)

    return redirect('home')  # Если метод не POST, перенаправляем на главную

def interpretation(request, total_score):
    # Определяем уровень тревоги
    if total_score <= 21:
        result = "Незначительный уровень тревоги."
    elif 22 <= total_score <= 35:
        result = "Средняя выраженность тревоги."
    else:
        result = "Очень высокая тревога."

    return render(request, 'mainapp/interpretation.html', {'total_score': total_score, 'result': result})
