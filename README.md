<h1>Calculadora de Bonificação</h1>

> [!NOTE]
> - Esse aplicativo ainda encontra-se em fase de desenvolvimento
> - Para realizar a instalação do app é necessário ter uma versão do Python instalada no seu computador, mas foco em trazer uma solução melhor, incluindo executaveis
> - Para testar esse app é necessário ter acesso a uma planilha de fechamento de caixa do webPosto

## Instalando o app

Para instalarmos o app precisamos seguir os seguintes passos:

```bash
git clone https://github.com/DabGias/calculadora-de-bonificacao
cd calculadora-de-bonificacao
python -m venv .venv

# Windows

./.venv/Scripts/activate

# Linux

source .venv/bin/activate

pip install -r ./requirements.txt
```

Para gerarmos o executável devemos usar os seguintes comandos:

### Linux

```bash
pyinstaller -F main.py models.py views.py components.py utils.py -n "Calculadora de Bonificação"
```

### Windows/MacOS

```bash
pyinstaller -F main.py models.py views.py components.py utils.py -n "Calculadora de Bonificação" -w -i ./icon.ico
```
