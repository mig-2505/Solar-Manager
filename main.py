import requests
import time
import json
import matplotlib.pyplot as plt

# Nome do json
ARQUIVO_BATERIA = "bateria.json"

# Coordenadas de São Paulo (troque para a sua região)
latitude = -23.55
longitude = -46.63

# Endpoint da API Open-Meteo
url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=direct_radiation,temperature_2m,cloudcover,sunshine_duration&timezone=America/Sao_Paulo"

# Faz a requisição GET
response = requests.get(url)
data = response.json()

# Pegar as primeiras 24 horas de dados
horas = data["hourly"]["time"][:24]
radiacao = data["hourly"]["direct_radiation"][:24]
temperatura = data["hourly"]["temperature_2m"][:24]
nuvens = data["hourly"]["cloudcover"][:24]
sol = data["hourly"]["sunshine_duration"][:24]

# Funções auxiliares
# Função para recomendar horarios para recarregar bateria
def escolherhorario(horario, radiation, duracao_sol, nuvem):
    if radiation > 300 and duracao_sol > 40 and nuvem < 80:
        print(f"Horas:{horario} - Radiação: {radiation} W/m² | "
            f"Duração do sol: {duracao_sol:.1f} min | "
            f"Nuvens: {nuvem}% | Recomendação: É recomendado recarregar\n")
    else:
        return "Não recomendado para carregar"

# Função para configurar a bateria
def configurarbateria():
    nome = input("Digite um identificador para a bateria: ")

    while True:
        capacidade_bat = int(input("Digite a capacidade da bateria (0-100): "))
        if 0 <= capacidade_bat <= 100:
            break
        print("Digite um valor válido (0-100).")

    while True:
        nivel_bat = int(input("Digite o nível atual da bateria (0-100): "))
        if 0 <= nivel_bat <= capacidade_bat:
            break
        print(f"Digite um valor válido (0-{capacidade_bat}).")

    return capacidade_bat, nivel_bat, nome

# Função para salvar os dados da bateria no json
def salvar_bateria(dado):
    historico_existente = carregar_bateria()
    historico_existente.append(dado)
    with open(ARQUIVO_BATERIA, "w") as arquivo:
        json.dump(historico_existente, arquivo, indent=4)

# Função para carregar os dados da bateria no json
def carregar_bateria():
    try:
        with open(ARQUIVO_BATERIA, "r") as arquivo:
            conteudo = arquivo.read().strip()
            if not conteudo:
                return []
            return json.loads(conteudo)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Função para mostrar o grafico dos dados: Nome e nivel final da bateria
def mostrar_grafico():
    # Exibe grafico com Horas e dias e Porcentagem final da bateria ( mostrando se foi carregada ou nn )
    dados = carregar_bateria()
    if not dados:
        print("Nenhum dado encontrado no JSON.")
        return

    valores_hora = [item['Nome'] for item in dados]
    valores_nivel_final = [item['Nivel_final'] for item in dados]

    plt.bar(valores_hora, valores_nivel_final)
    plt.xlabel('Horas e Dias')
    plt.ylabel('Nível Final da Bateria (%)')
    plt.title('Relação Horas/Dias e Carregamento de Baterias')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

# Simulação de um assistente virtual
def assistente_virtual():
    while True:
        print("\n=== Assistente Virtual ===")
        comando = input("Diga um comando (ex: 'status', 'limpar histórico', 'recomendar horário', 'sair', etc): ").lower()
        if comando == "status":
            nome = input("Digite o nome da bateria que quer saber os status: ")
            dados = carregar_bateria()
            encontrada = False
            for bat in dados:
                if bat["Nome"].lower() == nome.lower():
                    print(f"\n Status da bateria '{bat['Nome']}':")
                    print(f"   Capacidade: {bat['Capacidade']}%")
                    print(f"   Nível inicial: {bat['Nivel_inicial']}%")
                    print(f"   Nível final: {bat['Nivel_final']}%")
                    print(f"   Carregada: {'Sim' if bat['Carregado'] == 's' else 'Não'}")
                    print(f"   Hora e Dia: {bat['Hora e Dia']}")
                    print(f"   Energia ac: {bat['Energia_AC']}")
                    encontrada = True
                    break
            if not encontrada:
                print(f"⚠️ Não foi encontrada bateria com o nome '{nome}'.")

        elif comando == "limpar histórico":
            confirmacao = input("Tem certeza que deseja limpar o historico?(s/n): ")
            if confirmacao == "s":
                with open(ARQUIVO_BATERIA, "w") as arquivo:
                    arquivo.write("[]")
                print("Historico apagado com sucesso!")
            else:
                print("Operacao cancelada")


        elif comando == "recomendar horário":
            recomendados = []
            for n in range(24):
                sol_minuto = sol[n] / 60
                result = escolherhorario(horas[n], radiacao[n], sol_minuto, nuvens[n])
                if result is None:  # se for recomendado
                    recomendados.append(horas[n])
            if recomendados:
                print("Horários recomendados:")
                for z in recomendados:
                    print(" -", z)
            else:
                print("Nenhum horário ideal encontrado hoje.")
        elif comando == "sair":
            print("Desligando assistente virtual...")
            break
        else:
            print("Desculpe, não entendi o comando.")

# Simulação básica de inversor DC -> AC
def inversor(energia_entrada, capacidade_maxima=3000, eficiencia=0.95):
    energia_convertida = energia_entrada * eficiencia
    if energia_convertida > capacidade_maxima:
        energia_convertida = capacidade_maxima
    print(f"Inversor converteu {energia_entrada:.0f} W em {energia_convertida:.0f} W AC")
    return energia_convertida

# Função para mostrar o menu
def exibirmenu():
    print("==== MENU ====")
    print("1. Exibir recomendações de horários para carregar")
    print("2. Cadastrar Bateria")
    print("3. Exibir Baterias cadastradas")
    print("4. Exibir Gráfico das Baterias")
    print("5. Assistente Virtual")
    print("6. Sair")


# Taxas de carga/consumo
taxa_carregamento = 5  # % por hora
taxa_consumo = 2       # % por hora

# Programa principal:
historico_horas = []

while True:
    exibirmenu()
    opc = int(input("Opção...: "))

    if opc == 1:
        # Mostrar recomendações
        for i in range(24):
            sol_minutos = sol[i] / 60
            resultado = escolherhorario(horas[i], radiacao[i], sol_minutos, nuvens[i])
            if resultado is None:  # se recomendado
                historico_horas.append(horas[i])

        if historico_horas:
            print("Horários recomendados para carregar:")
            for h in historico_horas:
                print(h)
            opc_hora = input("Digite o horário que deseja usar para carregar: ")
            if opc_hora in historico_horas:
                print(f"Hora definida: {opc_hora}")
            else:
                print("Horário inválido.")
        else:
            print("Nenhum horário recomendado hoje.")

    elif opc == 2:
        # Configurar bateria
        capacidade_bateria, nivel_bateria, identificador = configurarbateria()
        nivel_inicial = nivel_bateria

        print(f"Nome: {identificador} | Capacidade: {capacidade_bateria} | Nível atual: {nivel_bateria}\n")

        resposta = input("Deseja carregar a bateria nesse horário? (s/n): ").lower()

        if resposta == "s":
            while nivel_bateria < capacidade_bateria:
                nivel_bateria += taxa_carregamento
                if nivel_bateria > capacidade_bateria:
                    nivel_bateria = capacidade_bateria
                print(f"Carregando... Nível atual: {nivel_bateria}%")
                time.sleep(1)  # simula o tempo passando
            print("Bateria totalmente carregada!\n")
        else:
            print("Carregamento cancelado.\n")

        energia_bateria = nivel_bateria * 30
        energia_ac = inversor(energia_bateria)  # converte para AC simulando inversores GoodWe

        novo_registro = {
            "Nome": identificador,
            "Capacidade": capacidade_bateria,
            "Nivel_inicial": nivel_inicial,
            "Nivel_final": nivel_bateria,
            "Carregado": resposta,
            "Hora e Dia": opc_hora if opc_hora else "Nao definido",
            "Energia_AC": energia_ac
        }

        salvar_bateria(novo_registro)

    elif opc == 3:
        print(carregar_bateria())

    elif opc == 4:
        mostrar_grafico()

    elif opc == 5:
        print("Chamando Assitente Virtual...")
        assistente_virtual()

    elif opc == 6:
        print("Saindo do programa...")
        break

    else:
        print("Opção inválida.")