from funcoes.verificacao_socios import verificar_emails
from funcoes.envio_email import enviar_emails
from configuracoes import configuracoes

lista = verificar_emails()
enviar_emails(lista, configuracoes)

