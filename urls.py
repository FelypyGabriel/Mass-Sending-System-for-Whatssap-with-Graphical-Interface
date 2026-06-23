from django.contrib import admin
from django.urls import path
from mensagens import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('painel/', views.page_system, name='page_system'),
    path('salvar_contato/', views.salvar_contato, name='salvar_contato'),
    path('enviar/', views.enviar_view, name='enviar_view'),
    path('excluir_contato/<int:contato_id>/', views.excluir_contato, name='excluir_contato'),

]
