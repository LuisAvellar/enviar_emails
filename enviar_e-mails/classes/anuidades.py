from datetime import datetime, timedelta
import csv
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class Anuidades:
    def __init__(self, configuracoes):
        self.meu_email = configuracoes['meu_email']
        self.email_from = configuracoes['email_from']
        self.host = configuracoes['host']
        self.porta = configuracoes['porta']
        self.caminho_anuidades = configuracoes['caminho_anuidades']
        self.cabecalho_anuidade = configuracoes['cabecalho_anuidade']
        self.caminho_dados = configuracoes['caminho_dados']
        self.lista_verificacao = []
        self.mensagens = []
        self.erros = []
        self.senha = None
        self.erros_login = []
        self.erros_envio = []

    def verificar_emails(self):
        checagem = input('Já atualizou as planilhas de dados para este mês?'
                         '\nDigite "y" para continuar:')
        if checagem.lower() != 'y':
            return 0
        lista, dados, anuidade = self._importacao()
        for z in lista:
            try:
                data_vencimento = datetime.strptime(anuidade[z]['fim'], '%Y-%m-%d')
                x = data_vencimento - datetime.now()
                data_vencimento = data_vencimento.strftime("%d/%m/%Y")
                anuidade[z]['dias_vencer'] = x
                if x > timedelta(days=30):
                    continue
                dados_vencimento = {'nome': z, 'status': dados[z]['First Role'], 'e-mail': dados[z]['Email'],
                                    'data_vencimento': data_vencimento
                                    }
                if x > timedelta(days=0):
                    dados_vencimento['vencimento'] = 'a vencer'
                    self.lista_verificacao.append(dados_vencimento)
                elif x > - timedelta(days=90):
                    dados_vencimento['vencimento'] = 'vencida'
                    self.lista_verificacao.append(dados_vencimento)
                else:
                    dados_vencimento['vencimento'] = 'desligando'
                    self.lista_verificacao.append(dados_vencimento)
            except KeyError as e:
                self.erros.append([z, e])

    def _importacao(self):
        with open(self.caminho_dados, 'r') as arquivo:
            dados_socios = [x for x in csv.reader(arquivo)]
        cabecalho_dados = dados_socios.pop(0)
        coluna_ref = 3  # Posição do nome de ref na tabela
        del cabecalho_dados[coluna_ref]
        lista_socios = []
        dicto_dados = {}
        status_ativos = ['Guia', 'Sócio Ativo', 'Administrador', 'CFG', 'Diretoria']
        for x in dados_socios:
            z = x.pop(coluna_ref)
            if x[4] not in status_ativos:
                continue
            dicto_temp = {cabecalho_dados[i]: x[i] for i in range(1, 5)}
            lista_socios.append(z)
            dicto_dados[z] = dicto_temp

        with open(self.caminho_anuidades, 'r') as arquivo:
            dados_anuidade = [x for x in csv.reader(arquivo)]
        dicto_anuidades = {}
        for x in dados_anuidade:
            z = x.pop(0)
            dicto_temp = {self.cabecalho_anuidade[i]: y for i, y in enumerate(x)}
            dicto_anuidades[z] = dicto_temp
        return lista_socios, dicto_dados, dicto_anuidades

    def enviar_emails(self):
        meu_email = str(self.meu_email)
        self.senha = input(f'Digite a senha de {meu_email}:')
        for i, z in enumerate(self.lista_verificacao):
            if z['vencimento'] == 'a vencer':
                z['caminho_template'] = 'static/template_socios_vencendo.html'
                z['assunto'] = 'Lembrete de vencimento de anuidade.'
            elif (z['vencimento'] == 'vencida') or (z['vencimento'] == 'desligando'):
                z['caminho_template'] = 'static/template_socios_atrasado.html'
                z['assunto'] = 'Aviso de vencimento da anuidade.'
            else:
                continue
            msg = self._substituir_no_email(z)
            if msg:
                self.mensagens.append({'e-mail': z['e-mail'], 'nome': z['nome'], 'mensagem': msg})
        self._logar_enviar()  # Tentar tirar do for e enviar todos de uma vez
        if self.erro_login or self.erros_envio:
            self.imprimir_erros()

    def _substituir_no_email(self, lista_mensagem):
        with open(lista_mensagem['caminho_template'], 'r') as html:
            template = Template(html.read())
            corpo_msg = template.substitute(nome=lista_mensagem['nome'], data=lista_mensagem['data_vencimento'])
        msg = MIMEMultipart()
        msg['from'] = self.email_from
        msg['to'] = lista_mensagem['e-mail']
        msg['subject'] = lista_mensagem['assunto']
        corpo = MIMEText(corpo_msg, 'html')
        msg.attach(corpo)
        return msg

    def _logar_enviar(self):
        with smtplib.SMTP(host=self.host, port=self.porta) as smtp:
            try:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(self.meu_email, self.senha)
                self._enviar(smtp)
            except Exception:
                self.erro_login = 'Erro de login'
                self.erros_envio = []

    def _enviar(self, smtp):
        lista_erros = []
        print('Enviando...')
        tam = len(self.mensagens)
        for i, mensagem in enumerate(self.mensagens):
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
        self.erro_login = []
        self.erros_envio = lista_erros

    def imprimir_erros(self):
        if self.erros_login:
            print('Erro no login')
        if self.erros_envio:
            print('\nOs e-mail a seguir não foram enviados:')
            print('Nome   ---   e-mail')
            for erros in self.erros_envio:
                print(f'{erros[0]}   ---   {erros[1]}')
            data_atual = datetime.now().strftime('%H-%M-%S--%d-%m-%Y')
            with open(f'emails_nao_enviados_{data_atual}.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(self.erros_envio)
            print(f'\nRelatório de erros gravado no arquivo:\nemails_nao_enviados_{data_atual}.csv')
