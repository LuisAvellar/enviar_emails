from datetime import datetime, timedelta
import csv


def verificar_emails():
    lista, dados, anuidade = importacao()
    erros = []
    lista_verificacao = []
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
                lista_verificacao.append(dados_vencimento)
            elif x > - timedelta(days=90):
                dados_vencimento['vencimento'] = 'vencida'
                lista_verificacao.append(dados_vencimento)
            else:
                dados_vencimento['vencimento'] = 'desligando'
                lista_verificacao.append(dados_vencimento)
        except KeyError as e:
            erros.append([z, e])
    return lista_verificacao


def importacao(caminho_anuidades='Planilha sem título - Página1.csv', cabecalho_anuidade=('pagamento', 'inicio', 'fim'),
               caminho_dados='userlist.csv'):
    with open(caminho_dados, 'r') as arquivo:
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

    with open(caminho_anuidades, 'r') as arquivo:
        dados_anuidade = [x for x in csv.reader(arquivo)]
    dicto_anuidades = {}
    for x in dados_anuidade:
        z = x.pop(0)
        dicto_temp = {cabecalho_anuidade[i]: y for i, y in enumerate(x)}
        dicto_anuidades[z] = dicto_temp
    return lista_socios, dicto_dados, dicto_anuidades
