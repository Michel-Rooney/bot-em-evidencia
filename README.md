# Bot em Evidência

Este é um projeto desenvolvido para suprir as necessidades do servidor do discord do youtuber Logan do canal Matemática em Evidência.

### 📷 Canal do Youtube
[Matemática em evidência](https://www.youtube.com/c/Matem%C3%A1ticaemEvid%C3%AAncia)

### 📋 Documentação
[Discord - DOCS](https://discordpy.readthedocs.io/en/stable/)

### 📌 On Air
[Discord - Deploy](https://discloud.com/)

## 🚀 Começando

Essas instruções permitirão que você obtenha uma cópia do projeto em operação na sua máquina local para fins de desenvolvimento e teste.

### 📋 Pré-requisitos

Você precisa do [Python](https://www.python.org/downloads/) instaldo na sua máquina

```
# Verificar se está instaldo
# Linux
python3 --version

# Windows
python --version
```

**Note:** Os comandos abaixo serão na maioria relacionados ao linux

### 🔧 Instalação

1. Clone o repositório do projeto:

```git
git clone https://github.com/Michel-Rooney/bot-em-evidencia.git
```

2. Entre na pasta:

```
cd bot-em-evidencia
```

3. Crie um ambiente virtual:

```
python3 -m venv venv
```

4. Ative o ambiente virtual:

```
# Linux
source venv/bin/activate

# Windows
venv/Scripts/activate

# Quando ativo, irar aparecer (venv) no inicio
(venv) user@maquina ~/bot-em-evidencia$
```

**Note:** Para desativar rode o comando
```
deactivate
```

5. Com o ambiente ativo, instale as dependencias:

```
pip install -r requirements.txt
```

6. Copie o arquivo .env-example para .env:

```
cp .env-example .env

# No arquivo .env substitua os CHANGE-ME
```

7. Inicie o projeto:

```
python man.py
```

## 🛠️ Construído com

* [Python](https://www.python.org/) - Linguagem
* [Discord](https://discordpy.readthedocs.io/en/stable/) - Api do Discord
* [Discord](https://discordpy.readthedocs.io/en/stable/) - Ambiente de bots do Discord
* [Concursos Brasil](https://concursosnobrasil.com/) - Site do Concursos Brasil

## ✒️ Autores

* [Michel Rooney](https://github.com/Michel-Rooney/) - *Dev*

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE.md](https://github.com/Michel-Rooney/bot-em-evidencia/blob/main/LICENSE) para detalhes.
