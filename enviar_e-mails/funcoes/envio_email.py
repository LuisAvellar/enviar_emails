from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import csv
from datetime import datetime


def enviar_emails(lista, configuracoes):
    meu_email = str(configuracoes['meu_email'])
    mensagens = []
    configuracoes['senha'] = input(f'Digite a senha de {meu_email}:')
    for i, z in enumerate(lista):
        if z['vencimento'] == 'a vencer':
            z['caminho_template'] = 'static/template_socios_vencendo.html'
            z['assunto'] = 'Lembrete de vencimento de anuidade.'
        elif (z['vencimento'] == 'vencida') or (z['vencimento'] == 'desligando'):
            z['caminho_template'] = 'static/template_socios_atrasado.html'
            z['assunto'] = 'Aviso de vencimento da anuidade.'
        else:
            continue
        mensagem = substituir_no_email(z, configuracoes['email_from'])
        if mensagem:
            mensagens.append({'e-mail': z['e-mail'], 'nome': z['nome'], 'mensagem': mensagem})
    erro_login, erros_envios = logar_enviar(configuracoes, mensagens)  # Tentar tirar do for e enviar todos de uma vez
    if erro_login or erros_envios:
        imprimir_erros(erro_login, erros_envios)


def substituir_no_email(lista_mensagem, email_de):
    with open(lista_mensagem['caminho_template'], 'r') as html:
        template = Template(html.read())
        corpo_msg = template.substitute(nome=lista_mensagem['nome'], data=lista_mensagem['data_vencimento'])
    msg = MIMEMultipart()
    msg['from'] = email_de
    msg['to'] = lista_mensagem['e-mail']
    msg['subject'] = lista_mensagem['assunto']
    corpo = MIMEText(corpo_msg, 'html')
    msg.attach(corpo)
    return msg


def logar_enviar(configuracoes, mensagens):
    with smtplib.SMTP(host=configuracoes['host'], port=configuracoes['porta']) as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(configuracoes['meu_email'], configuracoes['senha'])
            erro_envio = enviar(mensagens, smtp)
            return 0, erro_envio
        except Exception:
            return 'Erro de login', 0


def enviar(mensagens, smtp):
    lista_erros = []
    print('Enviando...')
    tam = len(mensagens)
    for i, mensagem in enumerate(mensagens):
        erro = []
        try:
            smtp.send_message(mensagem['mensagem'])
        except Exception:
            print("\r", end="")
            nome = mensagem['nome']
            email = mensagem['e-mail']
            erro = [nome, email]
        if erro:
            lista_erros.append(erro)
        progresso = (i + 1) * 100 / tam
        print("\r", end="")
        print(f"{progresso:.0f}%", end="")
    return lista_erros


def imprimir_erros(erros_login, erros_envios):
    if erros_login:
        print('Erro no login')
    if erros_envios:
        print('\nOs e-mail a seguir não foram enviados:')
        print('Nome   ---   e-mail')
        for erros in erros_envios:
            print(f'{erros[0]}   ---   {erros[1]}')
        data_atual = datetime.now().strftime('%H-%M-%S--%d-%m-%Y')
        with open(f'emails_nao_enviados_{data_atual}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(erros_envios)
        print(f'\nRelatório de erros gravado no arquivo:\nemails_nao_enviados_{data_atual}.csv')
