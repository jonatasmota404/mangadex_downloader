# MangaDex Downloader

Este projeto é um script em Python para buscar e baixar mangás do MangaDex, armazenando os dados em um banco de dados SQLite.

## Requisitos

Antes de executar o script, instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

## Como Usar

### 1. Criar o Banco de Dados

Antes de qualquer operação, é necessário criar o banco de dados para armazenar as informações dos mangás. Isso pode ser feito automaticamente na primeira execução do programa, pois a função `criar_banco()` é chamada dentro do `menu()`.

### 2. Atualizar Lista de Mangás

O primeiro passo para utilizar o programa é atualizar a lista de mangás no banco de dados. Isso pode ser feito executando a função `buscar_mangas()`, que obtém os mangás da API do MangaDex e os armazena no banco de dados local.

No menu interativo, essa opção pode ser acessada digitando `1`.

### 3. Buscar Idiomas Disponíveis para um Mangá

Após atualizar a lista de mangás, é possível pesquisar um título específico e verificar quais idiomas estão disponíveis para download.

No menu interativo, essa opção pode ser acessada digitando `2`.

### 4. Baixar Capítulos de um Mangá

Depois de identificar o idioma desejado, é possível baixar capítulos específicos ou todos os capítulos disponíveis de um mangá.

No menu interativo, essa opção pode ser acessada digitando `3`.

### 5. Baixar Todos os Mangás do Banco de Dados

Para baixar todos os mangás armazenados no banco de dados em todos os idiomas disponíveis, selecione esta opção no menu.

No menu interativo, essa opção pode ser acessada digitando `4`.

### 6. Sair do Programa

Para encerrar o programa, basta escolher a opção de saída.

## Menu Interativo

O programa conta com um menu interativo que facilita a execução das funções. Para utilizá-lo, basta rodar o script principal e escolher as opções conforme desejado.

```python
def menu():
    criar_banco()
    while True:
        print("\n=== Menu ===")
        print("1. Atualizar lista de mangás")
        print("2. Buscar idiomas disponíveis para um mangá")
        print("3. Baixar capítulos de um mangá")
        print("4. Baixar todos os mangás do banco de dados")
        print("5. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            buscar_mangas()
        elif escolha == "2":
            nome_manga = input("Digite o nome do mangá: ")
            buscar_idiomas_disponiveis(nome_manga)
        elif escolha == "3":
            nome_manga = input("Digite o nome do mangá: ")
            baixar_manga(nome_manga)
        elif escolha == "4":
            baixar_todos_mangas()
        elif escolha == "5":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")
```

Para rodar o menu interativo, basta adicionar esta linha ao final do script:

```python
if __name__ == "__main__":
    menu()
```

## Estrutura do Banco de Dados

O banco `mangas.db` contém a tabela `mangas` com as colunas:

- `id` (PRIMARY KEY) - Identificador do mangá na API
- `title` - Título do mangá
- `tags` - Tags associadas (ainda não implementadas)
- `languages` - Idiomas disponíveis

## Organização dos Arquivos Baixados

Os capítulos são salvos no diretório `mangas/`, com a seguinte estrutura:

```
mangas/
  ├── Nome_do_Manga/
  │   ├── Idioma/
  │   │   ├── Número_do_Capítulo_Título/
  │   │   │   ├── 1.jpg
  │   │   │   ├── 2.jpg
  │   │   │   ├── ...
```

## Funções Principais

- `criar_banco()` → Cria o banco de dados SQLite.
- `buscar_mangas()` → Obtém a lista de mangás da API e salva no banco.
- `buscar_idiomas_disponiveis(nome_manga)` → Retorna os idiomas disponíveis para um mangá.
- `baixar_manga(nome_manga)` → Baixa capítulos de um mangá específico.
- `baixar_todos_mangas()` → Baixa todos os mangás registrados no banco.
- `baixar_capitulo(chapter_id, manga_id, idioma)` → Baixa imagens de um capítulo.

## Observações

- O script só baixa imagens de capítulos públicos disponíveis no MangaDex.
- Para evitar bloqueios, pode ser necessário usar proxies ou adicionar delays entre requisições.

---

Este projeto é um downloader simples para uso pessoal. Não é afiliado ao MangaDex e não deve ser usado para redistribuição ilegal de conteúdo.

