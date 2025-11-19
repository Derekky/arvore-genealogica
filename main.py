import networkx as nx
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.colors as mcolors
import random
import sys

# Carrega os dados da planilha
dfPessoas = pd.read_excel("info.xlsx", sheet_name="Pessoas")
dfRelações = pd.read_excel("info.xlsx", sheet_name="Relacoes")

# Converte para dicionários: {Nome, @telegram, Geracao}
pessoas = []

for _, row in dfPessoas.iterrows():
    pessoa = {
        "Nome": row.get("Nome"),
        "foto": row.get("@telegram"),
        "ano": row.get("Geracao")
    }
    if pessoa["Nome"]:  # Ignora se não tem nome
        pessoas.append(pessoa)

#DEBUG
#print(pessoas)

# Converte para dicionários: {pai/mãe, filho}
relacoes = []

for _, row in dfRelações.iterrows():
    pai_mae = row.get("Pai/Mãe")
    filho = row.get("Filho")

    if pd.notna(pai_mae) and pd.notna(filho):
        relacao = {
            "pai_mae": pai_mae,
            "filho": filho
        }
        relacoes.append(relacao)


# Constrói o dicionário de informações
info = {
    p["Nome"]: {
        "geracao": p["ano"],
        "ano": p["ano"],
        "foto": p["foto"]
    }
    for p in pessoas
}

# Para ajustar as gerações estou ordenando os anos e mapeando de 0 a n
# De acordo com a ordem de aparição dos anos de ingresso
anos = [
    dados["ano"] for dados in info.values()
    if pd.isna(dados["ano"]) is not True
]
anos_unicos_ordenados = sorted(set(anos))
mapa_anos = {
    ano: idx for idx, ano in enumerate(anos_unicos_ordenados)
}

# Atribui as gerações
for pessoa in info.values():
    if pd.isna(pessoa["ano"]) is not True:
        pessoa["geracao"] = mapa_anos[pessoa["ano"]]

# Foto padrão pros vértices sem
nophoto = "fotos/no-photo.jpg"

# Função para arrendondar as fotos
def imagem_redonda(path, size=200):
    img = Image.open(path).convert("RGBA").resize((size, size))
    np_img = np.array(img)

    # Máscara circular
    h, w = size, size
    y, x = np.ogrid[:h, :w]
    mask = (x - w/2)**2 + (y - h/2)**2 > (w/2)**2

    # Aplica transparência fora do círculo
    np_img[mask, 3] = 0
    return np_img

# Cria o grafo
G = nx.DiGraph()
G.add_edges_from([(r["pai_mae"], r["filho"]) for r in relacoes])

# Calcula posições para formar uma árvore (outras opções para prog são "fdp", "twopi" e "sfdp")
try:
    # Usa Graphviz 'dot' para layout hierárquico (é o layout que deixa com cara de árvore genealógica)
    pos = graphviz_layout(G, prog="dot")
except (FileNotFoundError, OSError) as e:
    # Falha comum: Graphviz não está instalado
    print("Graphviz não encontrado. Saindo do programa.")
    print("Por favor instale o Graphviz (link: https://graphviz.org/download/)")
    print("    ou pip install graphviz")
    sys.exit(1)

# Randomiza uma lista de cores
colors = list(mcolors.CSS4_COLORS.values())
random.shuffle(colors)

node_colors = {node: colors[i % len(colors)] for i, node in enumerate(G.nodes)}

# Visualização
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor("#1a1a1a")

# Desenha os vértices
nx.draw_networkx_nodes(G, pos, node_size=1000, node_color="#32a8a2", ax=ax)

# Desenhar as arestas com as cores de acordo com o pai/mãe
for node in G.nodes:
    edge_color = node_colors[node]
    edges = [(node, target) for target in G.successors(node)]
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=edge_color, arrows=True,arrowsize=20,connectionstyle="arc3,rad=0.1", ax=ax, node_size=1400)

# Adiciona os nomes e imagens relativos às coordenadas de cada vértice
for nome, (x, y) in pos.items():
    dados = info[nome]

    # Foto, se existir e for acessível
    try:
        nomeFoto = dados.get("foto")  # Get the 'foto' field
        if not nomeFoto or pd.isna(nomeFoto):
            print(f"Imagem não encontrada para {nome}. Usando a imagem padrão.")
            nomeFoto = "no-photo"
            img = imagem_redonda(nophoto, size=100)
        caminhoFoto = os.path.join("fotos/", nomeFoto) + ".jpg"
        if os.path.exists(caminhoFoto):
            img = imagem_redonda(caminhoFoto, size=100)
        else:
            print(f"Imagem não encontrada para {nome}. Usando a imagem padrão.")
            img = imagem_redonda(nophoto, size=100)
        imagebox = OffsetImage(img, zoom=0.4)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False, bboxprops=dict(boxstyle="circle"))
        ax.add_artist(ab)
    except Exception as e:
        print(f"Erro ao carregar imagem de {nome}: {e}")
        img = imagem_redonda(nophoto, size=100)  # Fallback pra imagem padrão
    
    # Texto: nome + ano (se existir)
    label = nome
    """ Colocar ano embaixo do nome
    if dados.get("ano"):
        label += f"\n({dados['ano']})"
    """
    ax.text(x, y - 10, label, ha="center", va="top", fontsize=8, color="white", family="serif", wrap=True)

# Finaliza visualização
ax.set_title("Família!❤️", fontsize=36, color="white")
ax.axis('off')
plt.tight_layout()
plt.show()
