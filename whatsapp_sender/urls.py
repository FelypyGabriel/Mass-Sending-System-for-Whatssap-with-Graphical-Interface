from django.contrib import admin
from django.urls import path
from mensagens import views

urlpatterns = [

    # ADMIN
    path('admin/', admin.site.urls),

    # =========================
    # AUTENTICAÇÃO
    # =========================
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),

    # =========================
    # SISTEMA PRINCIPAL
    # =========================
    path('painel/', views.page_system, name='page_system'),

    # =========================
    # WHATSAPP (QR + SESSÃO)
    # =========================
    path('qr/', views.pagina_qr, name='qr'),
    path('gerar_qr/', views.gerar_qr, name='gerar_qr'),
    path('desconectar/', views.desconectar_whatsapp, name='desconectar_whatsapp'),

    # =========================
    # ENVIO (FILA)
    # =========================
    path('enviar/', views.enviar_view, name='enviar_view'),

    # =========================
    # CONTATOS
    # =========================
    path('salvar_contato/', views.salvar_contato, name='salvar_contato'),
    path('excluir_contato/<int:contato_id>/', views.excluir_contato, name='excluir_contato'),

]