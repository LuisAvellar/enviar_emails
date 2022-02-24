from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from funcoes.configuracoes import *

dados_venc = {'nome': 'nome', "status": 'First Role', "e-mail": 'laam88@gmail.com', 'data_vencimento': 'fim',
              'vencimento': 'a vencer'}


def enviar_emails(lista):
    tam = len(lista)
    print('Enviando...')
    for i, z in enumerate(lista):
        if z['vencimento'] == 'a vencer':
            z['caminho_template'] = 'static/template_socios_vencendo.html'
            z['assunto'] = 'Lembrete de vencimento de anuidade.'
        elif (z['vencimento'] == 'vencida') or (z['vencimento'] == 'desligando'):
            z['caminho_template'] = 'static/template_socios_atrasado.html'
            z['assunto'] = 'Aviso de vencimento da anuidade.'
        else:
            continue
        mensagem = substituir_no_email(z)
        logar_enviar(mensagem)
        progresso = i * 100 / tam
        print("\r", end="")
        print(f"{progresso}%", end="")
    print("\r", end="")
    print("100%")
    print("concluido")
    return


def substituir_no_email(lista):
    with open(lista['caminho_template'], 'r') as html:
        template = Template(html.read())
        corpo_msg = template.substitute(nome=lista['nome'], data=lista['data_vencimento'])
    msg = MIMEMultipart()
    msg['from'] = meu_email
    msg['to'] = lista['e-mail']
    msg['subject'] = lista['assunto']  # Pegar assunto e-mail
    corpo = MIMEText(corpo_msg, 'html')
    msg.attach(corpo)
    return msg


def logar_enviar(msg):
    with smtplib.SMTP(host=host, port=porta) as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(meu_email, minha_senha)
            smtp.send_message(msg)
        except Exception:
            print('Erro')
            # raise Exception(f'Erro no envio do e-mail.')
