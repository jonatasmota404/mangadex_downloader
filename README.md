# MangaDex Downloader

Este projeto é um script em Python para buscar e baixar mangás do MangaDex, armazenando os dados em um banco de dados SQLite.

## Requisitos

Antes de executar o script, instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

## Configuração e Uso

1. **Criar o banco de dados**

   - Execute a função `criar_banco()` para criar o banco `mangas.db`.

2. **Buscar Mangás**

   - Execute `buscar_mangas()` para buscar os mangás disponíveis na API do MangaDex e armazená-los no banco de dados.

3. **Baixar um Mangá**

   - Execute `baixar_manga(nome_manga)` e informe o nome do mangá que deseja baixar.
   - Escolha um dos mangás listados.
   - Escolha um idioma disponível.
   - Escolha um capítulo ou baixe todos.

4. **Baixar Todos os Mangás do Banco de Dados**

   - Execute `baixar_todos_mangas()` para baixar automaticamente todos os mangás armazenados no banco.

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

