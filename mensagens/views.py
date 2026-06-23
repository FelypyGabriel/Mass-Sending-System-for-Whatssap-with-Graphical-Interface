from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
import threading
import time
import random
import urllib.parse
import os
import queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from .models import Contato, Mensagem, LogEnvio
from .forms import ContatoForm
driver_global = None
fila_envio = queue.Queue()
worker_ativo = False
def index(request):
    return render(request, 'mensagens/index.html')
def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('page_system')
        messages.error(request, 'Usuário ou senha inválidos')
    return render(request, 'mensagens/login.html')
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not username or not email or not password:
            messages.error(request, 'Preencha todos os campos')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe')
            return redirect('register')
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        messages.success(request, 'Cadastro realizado com sucesso!')
        return redirect('login')
    return render(request, 'mensagens/register.html')
@login_required
def page_system(request):
    contatos = Contato.objects.filter(usuario=request.user).order_by('-id')
    form = ContatoForm()
    return render(request, 'mensagens/page_system.html', {
        'form': form,
        'contatos': contatos
    })
def iniciar_navegador():
    options = webdriver.ChromeOptions()
    profile_path = os.path.join(os.getcwd(), "selenium_profile")
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )
def clicar_botao_envio(driver, timeout=30):
    try:
        seletores = [
            '//span[@data-icon="send"]/ancestor::button',
            '//button[@aria-label="Enviar"]',
            '//button[@data-testid="compose-btn-send"]',
            '//footer//button[span[@data-icon="send"]]'
        ]
        for seletor in seletores:
            try:
                botao = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, seletor))
                )
                botao.click()
                return True
            except:
                continue
        return False
    except:
        return False
def worker_envio():
    global driver_global, worker_ativo
    worker_ativo = True
    while not fila_envio.empty():
        usuario, mensagem_obj, contatos = fila_envio.get()
        try:
            if not driver_global:
                driver_global = iniciar_navegador()
                driver_global.get("https://web.whatsapp.com")
                WebDriverWait(driver_global, 120).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
                )
            mensagem_url = urllib.parse.quote(mensagem_obj.texto)
            for contato in contatos:
                telefone = ''.join(c for c in contato.telefone if c.isdigit())
                try:
                    url = f"https://web.whatsapp.com/send?phone={telefone}&text={mensagem_url}"
                    driver_global.get(url)
                    WebDriverWait(driver_global, 45).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                    )
                    time.sleep(3)
                    enviado = clicar_botao_envio(driver_global)
                    LogEnvio.objects.create(
                        usuario=usuario,
                        contato=contato,
                        mensagem=mensagem_obj,
                        status="ENVIADO" if enviado else "ERRO"
                    )
                    time.sleep(random.randint(3, 6))
                except Exception as e:
                    LogEnvio.objects.create(
                        usuario=usuario,
                        contato=contato,
                        mensagem=mensagem_obj,
                        status="ERRO",
                        erro=str(e)
                    )
        except Exception as e:
            print("Erro geral:", e)
        fila_envio.task_done()
    worker_ativo = False
@login_required
def enviar_view(request):
    global worker_ativo
    if request.method != "POST":
        return JsonResponse({"status": "erro"}, status=405)
    data = json.loads(request.body)
    mensagem_texto = data.get("mensagem")
    telefones = data.get("contatos", [])
    if not mensagem_texto or not telefones:
        return JsonResponse({"status": "erro"}, status=400)
    contatos = Contato.objects.filter(
        usuario=request.user,
        telefone__in=telefones,
        ativo=True
    )
    mensagem_obj = Mensagem.objects.create(
        usuario=request.user,
        texto=mensagem_texto
    )
    fila_envio.put((request.user, mensagem_obj, list(contatos)))
    if not worker_ativo:
        threading.Thread(target=worker_envio, daemon=True).start()
    return JsonResponse({"status": "ok", "msg": "Entrou na fila"})
@login_required
def desconectar_whatsapp(request):
    global driver_global
    try:
        if driver_global:
            driver_global.quit()
            driver_global = None
            return JsonResponse({"status": "ok", "msg": "WhatsApp desconectado"})
        else:
            return JsonResponse({"status": "erro", "msg": "Nenhuma sessão ativa"})
    except Exception as e:
        return JsonResponse({"status": "erro", "msg": str(e)})
@login_required
def pagina_qr(request):
    return render(request, 'mensagens/qr.html')
@login_required
def gerar_qr(request):
    global driver_global
    if not driver_global:
        driver_global = iniciar_navegador()
        driver_global.get("https://web.whatsapp.com")
    try:
        qr = WebDriverWait(driver_global, 20).until(
            EC.presence_of_element_located((By.XPATH, '//canvas'))
        )
        return JsonResponse({
            "qr": qr.screenshot_as_base64
        })
    except:
        return JsonResponse({"erro": "QR não encontrado"})
@login_required
@require_POST
def salvar_contato(request):
    data = json.loads(request.body)
    nome = data.get("nome")
    telefone = data.get("telefone")
    if not nome or not telefone:
        return JsonResponse({"status": "erro"}, status=400)
    contato = Contato.objects.create(
        usuario=request.user,
        nome=nome,
        telefone=telefone
    )
    return JsonResponse({"status": "ok", "id": contato.id})
@login_required
def excluir_contato(request, contato_id):
    contato = get_object_or_404(Contato, id=contato_id, usuario=request.user)
    contato.delete()
    return JsonResponse({"status": "ok"})
