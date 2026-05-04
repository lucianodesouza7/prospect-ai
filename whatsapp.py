"""
Utilitários para geração de links WhatsApp com mensagens personalizadas.
"""

import urllib.parse
from scraper import limpar_numero


# Modelos de mensagem pré-definidos
MODELOS_MENSAGEM = {
    "🤝 Comercial Direta": (
        "Olá, vi que a {nome} é referência em {segmento} aqui na região. "
        "Gostaria de saber quem é o responsável pelas parcerias/compras "
        "para apresentarmos uma solução. Podemos falar?"
    ),
    "💬 Consultiva / Suave": (
        "Oi! Tudo bem? Encontrei o contato de vocês e fiquei interessado "
        "nos serviços da {nome}. Vocês atendem pelo WhatsApp para tirar "
        "algumas dúvidas?"
    ),
    "🌐 Networking": (
        "Olá! Sou do setor de {segmento} e estou expandindo meus contatos "
        "com empresas da área. Gostaria de enviar nosso catálogo para a "
        "{nome}. Qual o melhor e-mail ou contato?"
    ),
    "✏️ Personalizada": "",  # O usuário escreve a mensagem
}


def gerar_link_whatsapp(
    telefone: str,
    nome_empresa: str = "",
    segmento: str = "",
    modelo: str = "🤝 Comercial Direta",
    mensagem_custom: str = "",
) -> str:
    """
    Gera um link wa.me com mensagem personalizada.

    Args:
        telefone: Número do telefone (com ou sem formatação).
        nome_empresa: Nome da empresa para personalizar a mensagem.
        segmento: Segmento de atuação para personalizar a mensagem.
        modelo: Chave do modelo de mensagem a usar.
        mensagem_custom: Mensagem personalizada (quando modelo = "✏️ Personalizada").

    Returns:
        URL formatada do WhatsApp Web.
    """
    numero_limpo = limpar_numero(telefone)
    if not numero_limpo:
        return ""

    if modelo == "✏️ Personalizada" and mensagem_custom:
        mensagem = mensagem_custom.format(
            nome=nome_empresa, segmento=segmento
        )
    elif modelo in MODELOS_MENSAGEM:
        template = MODELOS_MENSAGEM[modelo]
        mensagem = template.format(nome=nome_empresa, segmento=segmento)
    else:
        mensagem = f"Olá, {nome_empresa}!"

    texto_codificado = urllib.parse.quote(mensagem)
    return f"https://wa.me/{numero_limpo}?text={texto_codificado}"


def formatar_botao_whatsapp(link: str) -> str:
    """Retorna HTML para um botão estilizado de WhatsApp."""
    if not link:
        return '<span style="color: #888;">Sem telefone</span>'
    return (
        f'<a href="{link}" target="_blank" '
        f'style="background: linear-gradient(135deg, #25D366, #128C7E); '
        f"color: white; padding: 6px 16px; border-radius: 20px; "
        f"text-decoration: none; font-weight: 600; font-size: 13px; "
        f'display: inline-flex; align-items: center; gap: 6px;">'
        f"📱 WhatsApp</a>"
    )
