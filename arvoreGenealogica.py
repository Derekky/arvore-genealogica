import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
from PIL import Image
import numpy as np
import pandas as pd
import pandas as pd
from random import randint as rand

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

# Função para criar a árvore (estéticamente falando)
def calcularPosicao(G):
    pos = {}
    try:
        for node in G.nodes:
            x=0
            y=0

            #Temporário só pra deixar a galera espalhada
            x = rand(-50,50)

            if pd.isna(info[node].get("geracao")): 
                y = -10
            elif info[node].get("geracao") != 0:
                y = info[node].get("geracao")  # Calcula a posição y com base na geração
            pos[node] = (x, -y*10)
        return pos
    except Exception as e:
        print(f"Erro ao calcular posição: {e}")
        return pos

#Tenta inferir a geração dos restantes caso possível
def infereGeracao(G): #Estou rodando isso n² vezes de propósito
    for node in G.nodes:
        for node in G.nodes:
            predecessors = list(G.predecessors(node))
            if not predecessors:
                continue
            elif pd.isna(info[node].get("geracao")):
                #Caso exista predecessor usar sua geração + 1
                    info[node]["geracao"] = info[predecessors[0]].get("geracao") + 1

infereGeracao(G)
pos = calcularPosicao(G)
print(f"pos:{pos}")

# Visualização
fig, ax = plt.subplots(figsize=(12, 7))
nx.draw(G, pos, with_labels=False, arrows=True, node_size=2600, edge_color="#FFFFFF", node_color="#00bf2232")
fig.patch.set_facecolor("#1a1a1a")

# Adiciona imagem e/ou texto
for nome, (x, y) in pos.items():
    dados = info[nome]

    # Foto, se existir e for acessível
    try:
        nomeFoto = dados.get("foto")  # Get the 'foto' field
        if not nomeFoto or pd.isna(nomeFoto):
            print(f"Imagem não encontrada para {nome}. Usando a imagem padrão.")
            nomeFoto = "no-photo"

        caminhoFoto = os.path.join("fotos/", nomeFoto) + ".jpg"
        img = imagem_redonda(caminhoFoto, size=100)

        imagebox = OffsetImage(img, zoom=0.5)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False, bboxprops=dict(boxstyle="circle"))
        ax.add_artist(ab)
    except Exception as e:
        print(f"Erro ao carregar imagem de {nome}: {e}")
        img = imagem_redonda(nophoto, size=100)  # Fallback to default image in case of an error
    
    # Texto: nome + ano (se existir)
    label = nome
    """ Colocar ano embaixo do nome
    if dados.get("ano"):
        label += f"\n({dados['ano']})"
    """
    ax.text(x, y - 0.15, label, ha="center", va="top", fontsize=16, color="blue", family="serif")
      

for node in G.nodes:
    antecessor = list(G.predecessors(node))
    print(f"Antecessores de {node}: {antecessor}")


# Visualização
ax.set_title("Família!❤️", fontsize=36, color="white")
ax.axis('off')
plt.tight_layout()
plt.show()
