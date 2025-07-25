from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)
import logging
from docling.document_converter import DocumentConverter, PdfFormatOption
from dotenv import load_dotenv
from docling.models.picture_description_api_model import PictureDescriptionApiOptions
import os
_log = logging.getLogger(__name__)
def chatgpt_vlm_options(api_key:str="",modelo_usado:str="o4-mini") -> PictureDescriptionApiOptions:
    """
    Configura as opções para a API da OpenAI, deixando o docling
    montar o corpo da requisição.
    """
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")

    # A gente só precisa passar os parâmetros que a API da OpenAI exige e
    # que o docling não sabe, como o nome do modelo e o limite de tokens.
    api_parameters = {
        "model": modelo_usado,
        "max_completion_tokens": 10000,
    }

    options = PictureDescriptionApiOptions(
        url="https://api.openai.com/v1/chat/completions",
        # O corpo da requisição agora é montado pelo docling.
        # Passamos nossos parâmetros específicos aqui.
        params=api_parameters,
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        # O 'docling' vai pegar esse prompt e a imagem do PDF
        # e montar o 'messages' pra gente.
        prompt="Descreva esta imagem em detalhes. Seja preciso e conciso. Sua resposta deve ser no seguinte formato: {'Descrição da imagem':'A imagem é...'}",
        timeout=300
    )
    return options


def gerar_markdown(caminho_arquivo_referencia:str):

    logging.basicConfig(level=logging.INFO)
    pipeline_options = PdfPipelineOptions(
        enable_remote_services=True
    )
    pipeline_options.do_picture_description = True
    pipeline_options.picture_description_options = chatgpt_vlm_options()

    doc_converter = (
        DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.IMAGE,
                InputFormat.DOCX,
                InputFormat.HTML,
                InputFormat.PPTX,
                InputFormat.ASCIIDOC,
                InputFormat.CSV,
                InputFormat.MD,
            ],
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            },
        )
    )

    conv_results = doc_converter.convert(caminho_arquivo_referencia).document
    # print(conv_results.export_to_markdown())
    return conv_results

# --- Executa a função ---
if __name__ == "__main__":
    texto = gerar_markdown('uploads/Curriculo_Jose_Freitas_Alves_Neto.pdf')
    print(texto.export_to_markdown())