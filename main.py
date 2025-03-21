import requests
import sqlite3
import os
import re

def criar_banco():
    conn = sqlite3.connect("mangas.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mangas (
            id TEXT PRIMARY KEY,
            title TEXT,
            tags TEXT,
            languages TEXT
        )
    """)
    conn.commit()
    conn.close()

def buscar_mangas():
    url = "https://api.mangadex.org/manga"
    params = {"limit": 100, "offset": 0}
    
    todos_mangas = []
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            todos_mangas.extend(data["data"])
            if len(data["data"]) < 100:
                break
            params["offset"] += 100
        else:
            print(f"Erro ao buscar mangás: {response.status_code} - {response.text}")
            break
    salvar_mangas(todos_mangas)

def salvar_mangas(mangas):
    conn = sqlite3.connect("mangas.db")
    cursor = conn.cursor()
    for manga in mangas:
        manga_id = manga["id"]
        title = manga["attributes"]["title"].get("en", "Desconhecido")
        languages = ",".join(lang for lang in manga["attributes"].get("availableTranslatedLanguages", []) if lang)
        tags = "Sem tag"
        
        cursor.execute("""
        INSERT INTO mangas (id, title, tags, languages) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET title=excluded.title, tags=excluded.tags, languages=excluded.languages
        """, (manga_id, title, tags, languages))
    
    conn.commit()
    conn.close()

def buscar_idiomas_disponiveis(nome_manga):
    conn = sqlite3.connect("mangas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, languages FROM mangas WHERE title LIKE ?", (f"%{nome_manga}%",))
    resultados = cursor.fetchall()
    conn.close()
    
    if not resultados:
        print("Mangá não encontrado.")
        return None, []
    
    print("Mangás encontrados:")
    for i, (manga_id, title, languages) in enumerate(resultados, 1):
        print(f"{i}. {title} (ID: {manga_id})")
    
    escolha = input("Escolha um número correspondente ao mangá desejado: ")
    try:
        escolha = int(escolha)
        manga_id, title, idiomas = resultados[escolha - 1]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return None, []
    
    return manga_id, idiomas.split(",")

def baixar_manga(nome_manga):
    manga_id, idiomas_disponiveis = buscar_idiomas_disponiveis(nome_manga)
    if not manga_id:
        return
    
    print("Idiomas disponíveis:", ", ".join(idiomas_disponiveis))
    idioma = input("Escolha um idioma: ")
    if idioma not in idiomas_disponiveis:
        print("Idioma indisponível para este mangá.")
        return
    
    url = f"https://api.mangadex.org/manga/{manga_id}/feed"
    params = {"limit": 100, "offset": 0, "translatedLanguage[]": idioma}
    capitulos = {}
    
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for c in data["data"]:
                num_capitulo = c["attributes"].get("chapter", "0")  # Garante que há um número de capítulo
                titulo_capitulo = c["attributes"].get("title", "")  # Pode estar ausente
                try:
                    num_capitulo = float(num_capitulo)  # Converte para número para ordenação correta
                except ValueError:
                    num_capitulo = float("inf")  # Se não puder converter, coloca no final
                
                capitulos[num_capitulo] = (c["id"], titulo_capitulo)
            
            if len(data["data"]) < 100:
                break
            params["offset"] += 100
        else:
            print(f"Erro ao buscar capítulos: {response.status_code} - {response.text}")
            return
    
    if not capitulos:
        print("Nenhum capítulo encontrado para este mangá.")
        return

    # Ordena os capítulos por número antes de exibir
    capitulos_ordenados = sorted(capitulos.items())  # Ordena por chave (número do capítulo)

    for num_cap, (cap_id, cap_title) in capitulos_ordenados:
        if cap_title:
            print(f"{int(num_cap) if num_cap.is_integer() else num_cap}. Capítulo {num_cap} - {cap_title}")
        else:
            print(f"{int(num_cap) if num_cap.is_integer() else num_cap}. Capítulo {num_cap}")

    escolha = input("Digite o número do capítulo ou 'todos' para baixar todos: ")

    if escolha.lower() == "todos":
        for _, (cap_id, _) in capitulos_ordenados:
            baixar_capitulo(cap_id, manga_id, idioma)
    else:
        try:
            escolha = float(escolha)  # Permite entrada de capítulos com numeração decimal
            for num_cap, (cap_id, _) in capitulos_ordenados:
                if num_cap == escolha:
                    baixar_capitulo(cap_id, manga_id, idioma)
                    break
            else:
                print("Capítulo inválido.")
        except ValueError:
            print("Entrada inválida.")


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename) if filename else None

def baixar_capitulo(chapter_id, manga_id, idioma):
    # Buscar título do mangá no banco de dados
    conn = sqlite3.connect("mangas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM mangas WHERE id = ?", (manga_id,))
    resultado = cursor.fetchone()
    conn.close()
    
    if not resultado:
        print("Título do mangá não encontrado no banco de dados.")
        return

    titulo_manga = resultado[0]

    # Buscar título do capítulo na API
    url_capitulo = f"https://api.mangadex.org/chapter/{chapter_id}"
    response_capitulo = requests.get(url_capitulo)
    if response_capitulo.status_code == 200:
        data_capitulo = response_capitulo.json()
        titulo_capitulo = data_capitulo["data"]["attributes"].get("title", f"Capítulo_{chapter_id}")
        numero_capitulo = data_capitulo["data"]["attributes"].get("chapter", f"Desconhecido_{chapter_id}")
    else:
        print(f"Erro ao buscar informações do capítulo {chapter_id}.")
        return
    # Criar a pasta com os títulos formatados
    pasta = os.path.join(
    "mangas",
    sanitize_filename(titulo_manga) or "Desconhecido",
    idioma or "Desconhecido",
    f"{numero_capitulo}_{sanitize_filename(titulo_capitulo)}" if sanitize_filename(titulo_capitulo) else f"{numero_capitulo}"
    )
    os.makedirs(pasta, exist_ok=True)

    # Buscar imagens do capítulo
    url_imagens = f"https://api.mangadex.org/at-home/server/{chapter_id}"
    response_imagens = requests.get(url_imagens)
    if response_imagens.status_code == 200:
        try:
            data = response_imagens.json()
            images = data["chapter"].get("data", [])
            if not images:
                print(f"Nenhuma imagem encontrada para o capítulo {titulo_capitulo}.")
                return
            
            formato = "jpg"
            
            for i, img in enumerate(images, start=1):
                img_url = f"{data['baseUrl']}/data/{data['chapter']['hash']}/{img}"
                salvar_imagem(img_url, pasta, f"{i}.{formato}")
        except Exception as e:
            print(f"Erro ao processar capítulo {titulo_capitulo}: {e}")
    else:
        print(f"Erro ao acessar API para o capítulo {titulo_capitulo}: {response_imagens.status_code} - {response_imagens.text}")

def salvar_imagem(url, pasta, nome):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(pasta, nome), "wb") as file:
            file.write(response.content)
        print(f"Imagem {nome} salva.")
    else:
        print(f"Erro ao baixar {nome}.")

def baixar_todos_mangas():
    conn = sqlite3.connect("mangas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, languages FROM mangas")
    mangas = cursor.fetchall()
    conn.close()
    
    for manga_id, title, languages in mangas:
        idiomas_disponiveis = languages.split(",")
        if not idiomas_disponiveis:
            continue
        
        for idioma in idiomas_disponiveis:
            baixar_todos_capitulos(manga_id, title, idioma)

def baixar_todos_capitulos(manga_id, titulo_manga, idioma):
    url = f"https://api.mangadex.org/manga/{manga_id}/feed"
    params = {"limit": 100, "offset": 0, "translatedLanguage[]": idioma}
    
    capitulos = {}
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            novos_capitulos = {len(capitulos) + i + 1: c["id"] for i, c in enumerate(data["data"])}
            capitulos.update(novos_capitulos)
            if len(data["data"]) < 100:
                break
            params["offset"] += 100
        else:
            print(f"Erro ao buscar capítulos de {titulo_manga}: {response.status_code} - {response.text}")
            return
    
    if not capitulos:
        print(f"Nenhum capítulo encontrado para {titulo_manga} ({idioma}).")
        return
    
    for cap_id in capitulos.values():
        baixar_capitulo(cap_id, manga_id, idioma)

def buscar_manga_por_nome(nome_manga):
    """Busca um mangá específico pelo nome na API do MangaDex e salva no banco."""
    url = "https://api.mangadex.org/manga"
    params = {"title": nome_manga, "limit": 5}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        mangas_encontrados = data["data"]
        
        if not mangas_encontrados:
            print("Nenhum mangá encontrado com esse nome.")
            return
        
        print("\nMangás encontrados:")
        for i, manga in enumerate(mangas_encontrados, 1):
            title = manga["attributes"]["title"].get("en", "Desconhecido")
            print(f"{i}. {title} (ID: {manga['id']})")
        
        escolha = input("Escolha um número para salvar ou pressione Enter para cancelar: ")
        try:
            escolha = int(escolha)
            manga_selecionado = mangas_encontrados[escolha - 1]
            salvar_mangas([manga_selecionado])
            print(f"Mangá '{manga_selecionado['attributes']['title'].get('en', 'Desconhecido')}' salvo com sucesso!")
        except (ValueError, IndexError):
            print("Escolha inválida.")
    else:
        print(f"Erro ao buscar mangá: {response.status_code} - {response.text}")

def menu():
    criar_banco()
    while True:
        print("\nMenu:")
        print("1. Atualizar lista de mangás")
        print("2. Baixar mangá específico")
        print("3. Baixar todos os mangás")
        print("4. Buscar e salvar um mangá específico")
        print("5. Sair")
        escolha = input("Escolha uma opção: ")
        
        if escolha == "1":
            buscar_mangas()
        elif escolha == "2":
            nome_manga = input("Digite o nome do mangá: ")
            baixar_manga(nome_manga)
        elif escolha == "3":
            baixar_todos_mangas()
        elif escolha == "4":
            nome_manga = input("Digite o nome do mangá para buscar e salvar: ")
            buscar_manga_por_nome(nome_manga)
        elif escolha == "5":
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()
