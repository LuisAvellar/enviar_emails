from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import csv
from datetime import datetime


def enviar_emails(lista, configuracoes):
    tam = len(lista)
    meu_email = str(configuracoes['meu_email'])
    configuracoes['senha'] = input(f'Digite a senha de {meu_email}:')
    print('Enviando...')
    lista_erros = []
    for i, z in enumerate(lista):
        if z['vencimento'] == 'a vencer':
            z['caminho_template'] = 'static/template_socios_vencendo.html'
            z['assunto'] = 'Lembrete de vencimento de anuidade.'
        elif (z['vencimento'] == 'vencida') or (z['vencimento'] == 'desligando'):
            z['caminho_template'] = 'static/template_socios_atrasado.html'
            z['assunto'] = 'Aviso de vencimento da anuidade.'
        else:
            continue
        mensagem = substituir_no_email(z, configuracoes['meu_email'])
        resposta = logar_enviar(mensagem, configuracoes, z)
        if resposta:
            lista_erros.append(resposta)
        progresso = (i + 1) * 100 / tam
        print("\r", end="")
        print(f"{progresso:.0f}%", end="")
    print("\nConcluido")
    if not lista_erros:
        return
    imprimir_erros(lista_erros)
    return


def substituir_no_email(lista, meu_email):
    with open(lista['caminho_template'], 'r') as html:
        template = Template(html.read())
        corpo_msg = template.substitute(nome=lista['nome'], data=lista['data_vencimento'])
    msg = MIMEMultipart()
    msg['from'] = meu_email
    msg['to'] = lista['e-mail']
    msg['subject'] = lista['assunto']
    corpo = MIMEText(corpo_msg, 'html')
    msg.attach(corpo)
    return msg


def logar_enviar(msg, configuracoes, z):
    with smtplib.SMTP(host=configuracoes['host'], port=configuracoes['porta']) as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(configuracoes['meu_email'], configuracoes['senha'])
            smtp.send_message(msg)
            return False
        except Exception as e:
            print("\r", end="")
            nome = z['nome']
            email = z['e-mail']
            erro = [nome, email]
            return erro


def imprimir_erros(lista_erros):
    print('Os e-mail a seguir não foram enviados:')
    for erros in lista_erros:
        print(f'Nome: {erros[0]}     e-mail: {erros[1]}')
    data_atual = datetime.now().strftime('%H-%M-%S--%d-%m-%Y')
    with open(f'emails_nao_enviados_{data_atual}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(lista_erros)