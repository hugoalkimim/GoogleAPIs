#
# Hugo Danilo Santos Alkimim
#

import argparse
import io
import matplotlib.pyplot as plt
from google.cloud import vision
from PIL import Image, ImageDraw, ImageFont

# CONSTANTES
ERRO_MAXIMO = 0.0001
LARGURA_RETA_ROTULO = 5
TAMANHO_FONTE_ROTULO = 14
#

def rotula_objetos(caminho_entrada, caminho_saida):
    client = vision.ImageAnnotatorClient()

    img = Image.open(caminho_entrada)
	
    with open(caminho_entrada, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content = content)

    objetos = client.object_localization(image = image).localized_object_annotations

    rotulos = dict(()) # Dicionário com a lista e quantidade de rótulos utilizados até o momento.
    rt = list(()) # Lista de retângulos desenhados até o momento.

    largura, altura = img.size
	
    # Objetos estão ordenados pelo tamanho da certeza de que aquele rótulo se aplica a ele
	  # Taxas maiores tem prioridade
    for obj in objetos:
        pontos = obj.bounding_poly.normalized_vertices
        draw = ImageDraw.Draw(img)

        flag = 0
        for r in rt:
            if abs(r[0].x - pontos[0].x) <= ERRO_MAXIMO: # Verifica se o rótulo atual tem um ponto superior esquerdo igual ao de algum que ja foi desenhado
                flag = 1
                break

        # Se a flag for igual a zero, é possível começar um retângulo no ponto atual.
        if flag == 0:
            rt.append(pontos)
        else:
            continue

        # Verifica se este rótulo foi utilizado anteriormente.
        if obj.name in rotulos:
            rotulos[obj.name] += 1
        else:
            rotulos[obj.name] = 1

        #pontos[0] é o do canto superior esquerdo
        #pontos[1] é o do canto superior direito
        #pontos[2] é o do canto inferior direito
        #pontos[3] é o do canto inferior esquerdo

        draw.polygon([
        pontos[0].x * largura, pontos[0].y * altura,
        pontos[1].x * largura, pontos[1].y * altura,
        pontos[2].x * largura, pontos[2].y * altura,
        pontos[3].x * largura, pontos[3].y * altura], None, 'green')

        draw.line( [pontos[0].x * largura - LARGURA_RETA_ROTULO // 2, pontos[0].y * altura - 26,
                    pontos[1].x * largura + LARGURA_RETA_ROTULO // 2, pontos[1].y * altura - 26], 'black', LARGURA_RETA_ROTULO, None) # segmento horizontal superior -- esquerda -> direita
        draw.line( [pontos[1].x * largura, pontos[1].y * altura - 23,
                    pontos[1].x * largura, pontos[1].y * altura - 2], 'black', LARGURA_RETA_ROTULO, None) # segmento vertical da direita -- cima -> baixo
        draw.line([pontos[1].x * largura + LARGURA_RETA_ROTULO // 2, pontos[1].y * altura - 2,
                   pontos[0].x * largura - LARGURA_RETA_ROTULO // 2, pontos[0].y * altura - 2], 'black', LARGURA_RETA_ROTULO, None) # segmento horizontal inferior -- direita -> esquerda
        draw.line([pontos[0].x * largura, pontos[0].y * altura - 2,
		           pontos[0].x * largura, pontos[0].y * altura - 23], 'black', LARGURA_RETA_ROTULO, None) # segmento vertical da esquerda -- baixo -> cima

        font = ImageFont.truetype("arial.ttf", TAMANHO_FONTE_ROTULO)
        draw.text([pontos[0].x * largura + 7, pontos[0].y * altura - 23], (obj.name + " {}").format(rotulos[obj.name]), 'black', font)

    img.save(caminho_saida, 'JPEG')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('caminho_entrada', help = 'O arquivo que você utilizará como entrada.')
    parser.add_argument('caminho_saida', help = 'O caminho do arquivo em que o resultado será salvo.')
    args = parser.parse_args()
    parser = argparse.ArgumentParser()

    rotula_objetos(args.caminho_entrada, args.caminho_saida)
