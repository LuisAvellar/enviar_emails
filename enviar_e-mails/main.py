from configuracoes import configuracoes
from classes.anuidades import Anuidades

verificacao = Anuidades(configuracoes)
verificacao.verificar_emails()
verificacao.imprimir_lista_na_tela()
verificacao.enviar_emails()

# from funcoes.verificacao_socios import verificar_emails
# from funcoes.envio_email import enviar_emails

# lista = verificar_emails(configuracoes)
# if lista:
#     enviar_emails(lista, configuracoes)
