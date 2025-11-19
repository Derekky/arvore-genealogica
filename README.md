# Árvore Genealógica (arvoreFamilia)

Projeto simples para gerar uma visualização em forma de árvore genealógica a partir de uma planilha Excel e fotos locais.

**Arquivo principal**: `arvore_genealogica.py`

**Estrutura esperada do repositório**:

- `arvore_genealogica.py`  - script principal (usa `info.xlsx` e a pasta `fotos/`)
- `info.xlsx`              - planilha com duas abas: `Pessoas` e `Relacoes` (não comitado)
- `fotos/`                 - imagens JPEG das pessoas (ex.: `@telegram.jpg`) (não comitado)
- `requirements.txt`      - dependências Python

## Dependências principais

- `networkx`  - construção do grafo
- `pydot`     - integração com Graphviz para layout de árvore
- `matplotlib`- desenho/visualização
- `Pillow`    - manipulação de imagens
- `numpy`     - operações com arrays de imagem
- `pandas`    - leitura/transformação dos dados Excel
- `openpyxl`  - engine para `pandas.read_excel`

Observação: o pacote de sistema `graphviz` (binário) também é necessário para o layout `dot`. Instale-o antes de prosseguir (instruções abaixo).

## 1) Instalar Graphviz (passo obrigatório)

Windows (PowerShell):

```powershell
# Com Chocolatey (se você tiver):
choco install graphviz -y

# Ou baixe o instalador em https://graphviz.org/download/ e instale manualmente.
# Depois da instalação, confirme que o executável `dot` está no PATH:
dot -V
```

Linux (Debian/Ubuntu):

```bash
sudo apt update; sudo apt install -y graphviz
```

Se `dot -V` não mostrar a versão, verifique o PATH do sistema.

## 2) Criar e ativar um ambiente Python e instalar dependências

```bash
# 1) Crie e ative um virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 2) Instale dependências Python
pip install -r requirements.txt
```

## Como usar

1. Prepare `info.xlsx` com as abas e colunas abaixo:

- Aba `Pessoas`: colunas mínimas `Nome`, `@telegram`, `Geracao`
  - Exemplo:

  | Nome       | @telegram   | Geracao |
  |------------|-------------|---------|
  | João Silva | @joao123    | 3       |

- Aba `Relacoes`: colunas mínimas `Pai/Mãe`, `Filho`
  - Exemplo:

  | Pai/Mãe    | Filho       |
  |------------|-------------|
  | @joao123   | @maria45    |

2. Fotos

- Coloque as fotos em `fotos/` com nomes exatamente iguais ao campo `@telegram` da planilha e extensão `.jpg`.
  - Exemplo de nome de arquivo: `fotos/@joao123.jpg`
  - Se o nome de usuário contiver caracteres especiais, use o mesmo texto presente na coluna `@telegram`.
  - Atenção: em sistemas Linux o sistema de arquivos pode ser case-sensitive — mantenha correspondência exata.
- Há um arquivo de fallback `fotos/no-photo.jpg` usado para quem não tiver foto.

3. Execute o script:

```bash
python3 arvore_genealogica.py
```

## Privacidade / Git

- Por motivo de privacidade, **não** comite a sua planilha `info.xlsx` nem a pasta `fotos/` com imagens pessoais.

## Saídas / comportamento

- O script abre uma janela do `matplotlib` com a árvore de relações gerada.
- As fotos são cortadas em círculo e inseridas nos nós.

## Problemas comuns

- Erro relacionado ao Graphviz (ex.: "Graphviz's executables not found"):
  - Instale o pacote do sistema `graphviz` e confirme que `dot` está no PATH.
- `pandas.read_excel` falha com formato XLSX:
  - Certifique-se de ter `openpyxl` instalado (já listado em `requirements.txt`).
- Falha ao encontrar imagens:
  - Verifique os nomes na planilha e os arquivos em `fotos/` (extensão `.jpg`).

## Contribuições

- Contribuições são bem-vindas! Abra issues para discutir melhorias ou envie pull requests com correções e novos recursos.

## Licença

- MIT
