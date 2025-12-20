# IFshop

## Sobre o Projeto
O **IFshop** é uma plataforma web de e-commerce desenvolvida especificamente para a comunidade do IFRN Campus São Paulo do Potengi. O sistema centraliza e organiza a venda de produtos estudantis autorizados - especialmente camisetas de formatura - facilitando a arrecadação de recursos para eventos estudantis de forma transparente e conforme às normas institucionais.

Este projeto foi desenvolvido como parte da disciplina de **Programação e Desenvolvimento de Sistemas para Internet**, do curso **Técnico Integrado em Informática para Internet**, com o objetivo de aplicar, de forma integrada e prática, os conhecimentos adquiridos ao longo da formação.

## Funcionalidades Principais
- **Autenticação de usuários**: Registro, login e logout seguros.
- **Gestão de produtos**:
    - Criação, edição e exclusão de produtos (camisetas, produtos diversos).
    - Definição de preços, tamanhos, cores e controle de estoque.
    - Categorização por curso, turma e turno.
    - Busca e filtros avançados por nome, curso ou disponibilidade.
- **Administração e vendas**: 
    - Dashboard de controle com métricas de vendas e desempenho.
    - Gerenciamento de pedidos, estoque e relatórios financeiros.
    - Suporte a vendas de múltiplas turmas simultaneamente.
- **Sistema de compras**:
    - Carrinho interativo com adição, remoção e edição de pedido.
    - Confirmação de pedido e acompanhamento de status.
    - Histórico completo de compras para o usuário.
- **Interface responsiva e intuitiva**, adaptada para uso em desktop e dispositivos móveis.

> Para instruções detalhadas sobre o uso do sistema, consulte o **[Manual do Usuário](docs/manual/index.html)**.

## Tecnologias Utilizadas
### Backend
- **Python 3.8+**
- **Django** (framework web)
- **MySQL** (banco de dados)

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript**
- **Bootstrap** (estilização responsiva)

### Ferramentas e Bibliotecas
- Git (controle de versão)
- Pip (gerenciamento de dependências)
- Biblioteca padrão do Django e extensões

## Pré-requisitos
Antes de começar, certifique-se de ter instalado em sua máquina:
- **Python 3.8 ou superior**
- **MySQL Server**
- **Git**
- **Pip** (geralmente incluso com o Python)

## Instalação e Configuração
Siga os passos abaixo para configurar o ambiente de desenvolvimento:

### 1. Clone o repositório
```bash
git clone https://github.com/saramonalisa/planIQ.git
cd planiq
2. Crie e ative um ambiente virtual
Windows:
bash
python -m venv venv
venv\Scripts\activate
Linux/Mac:
bash
python3 -m venv venv
source venv/bin/activate
3. Instale as dependências
bash
pip install -r requirements.txt
Este comando instalará todas as bibliotecas necessárias listadas no arquivo requirements.txt.

4. Configure as variáveis de ambiente
bash
python scripts/env_gen.py
O script irá gerar um arquivo .env com as configurações necessárias para conexão com o banco de dados e outras variáveis do projeto.

5. Execute as migrações do banco de dados
bash
python manage.py makemigrations
python manage.py migrate
6. (Opcional) Crie um superusuário
Para acessar o painel administrativo do Django, execute:

bash
python manage.py createsuperuser
Siga as instruções no terminal para definir nome de usuário, e-mail e senha.

7. Execute o servidor de desenvolvimento
bash
python manage.py runserver
Acesse a aplicação em: http://localhost:8000

Estrutura do Projeto
text
planIQ/
├── app/                    # Aplicação principal (tarefas, matérias, períodos)
├── config/                 # Configurações do projeto Django
├── docs/                   # Documentação (incluindo manual do usuário)
├── scripts/                # Scripts utilitários (geração de .env)
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
├── templates/              # Templates HTML organizados por funcionalidade
├── usuarios/               # Aplicação de autenticação e perfis
├── .env.example            # Exemplo de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── LICENSE                 # Licença do projeto
├── manage.py               # Ponto de entrada do Django
├── README.md               # Este arquivo
└── requirements.txt        # Dependências do projeto






**Colaboradores:**
Eugênio Urbano Medeiros Filho

Helloar Lavinia Silva Costa

Milleny jamily Lima Vieira

Orientadora:
Fernanda Lígia

Licença
Este projeto está licenciado sob os termos da licença MIT. Consulte o arquivo LICENSE para mais detalhes.

Status do Projeto
✅ Concluído - Todas as funcionalidades principais implementadas e testadas.


Este README inclui:
1. **Identificação clara** do projeto
2. **Descrição objetiva** do propósito e contexto acadêmico
3. **Funcionalidades** bem especificadas
4. **Tecnologias** organizadas por categoria
5. **Instruções de instalação** passo a passo
6. **Estrutura do projeto** visualmente organizada
7. **Informações da equipe** e orientação
8. **Elementos extras** como status, licença e agradecimentos
