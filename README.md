# Wumpus: Echoes of the Lost

Wumpus: Echoes of the Lost é um jogo feito em Godot baseado no problema do Mundo de Wumpus descrito em https://moj.naquadah.com.br/new/treino/problem/?id=flia-problems.wumpus-medio. 
O diferencial desta implementação do Mundo de WUmpus é o uso de um agente inteligente baseado em lógica proposicional e SAT solving, que fornece dicas e verifica os movimentos do jogador.

## Descrição e regras

O ambiente segue as regras clássicas, com algumas adições/alterações:
 - A posição inicial e o tamanho do mapa são desconhecidos
 - Poços e Wumpus matam o jogador ao entrar na célula
 - Podem existir múltiplos Wumpus
 - O Jogador possui um número limitado de flechas e dicas
 - Flechas são disparadas na direção em que o jogador está voltado e percorrem uma linha reta até atingir um Wumpus ou uma Parede
 - Dicas destacam posições para onde o jogador deve se mover (em verde) ou disparar uma flecha (em vermelho)
 - O objetivo é chegar no ouro

## Controles

- A/D: girar para esquerda/direita
- W: mover para frente
- Espaço: atirar flecha
- H: pedir uma dica
- Esc: voltar para o menu

## Compilação

Para jogar, basta baixar a [release](https://github.com/TobiasSPerkowski/wumpus_world_godot/releases) mais recente, descompactar e executar o arquivo "wumpus".
Mas, caso deseje compilar o projeto, siga o passo a passo abaixo.

### 0. Pré-requisitos

- Python 3.12+
- pip

### 1. Instalar Dependências

Instale o PySAT com 
```bash
pip install python-sat
```
Instale o PyInstaller com
```bash
pip install pyinstaller
```
Os pacotes devem ser instalados system-wide. Caso ocorrer o erro **externally-managed-environment**, use
```bash
--break-system-packages
```
Instale o Godot versão 4.6.3-stable, disponível em https://godotengine.org/download/archive/4.6.3-stable/

### 2. Clonar o repositório

Clone o repositório com
```bash
git clone https://github.com/TobiasSPerkowski/wumpus_world_godot.git
```
ou baixe o ZIP

### 3. Compilar o conselheiro

Dentro do diretório do projeto, execute
```bash
pyinstaller --onefile advisor.py
```
O executável ("advisor") poderá ser encontrado no diretório "dist".

### 4. Exportar

Abra a Godot e clique em "Import";
Selecione o diretório do projeto, marque "Edit Now" e confirme;
Com o editor da Godot aberto, clique em "Project" e "Export...";
Na janela "Export", clique em "Export Project...";
Selecione o diretório onde deseja salvar o executável e clique em "Save".

### 5. Juntando tudo

Para o jogo funcionar:
- o diretório "Maps" com os arquivos .txt
- o executável do conselheiro
- o executável do jogo
**devem** estar no mesmo diretório.
