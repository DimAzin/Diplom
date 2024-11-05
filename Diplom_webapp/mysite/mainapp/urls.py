from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Основная страница, например, описание
    path('psychologist_selection/', views.psychologist_selection, name='psychologist_selection'),
    path('psychologist/', views.psychologist, name='psychologist'),
    path('tests/', views.tests, name='tests'),  # Страница Тесты
    path('tests/color/', views.color_test, name='color_test'),  # Страница Цветового теста
    path('tests/anxiety/', views.anxiety_test, name='anxiety_test'),  # Страница Теста тревожности
    path('tests/color/', views.color_test, name='color_test'),
    path('tests/color/symptom/', views.symptom_input, name='symptom_input'),
    path('tests/color/associate/', views.associate_words, name='associate_words'),
    path('tests/color/results/', views.interpret_results, name='interpret_results'),
    path('submit-anxiety-test', views.submit_anxiety_test, name='submit_anxiety_test'),  # Обработка теста
    path('interpretation/<int:total_score>/', views.interpretation, name='interpretation'),  # Интерпретация результатов
]
