import json
from datetime import datetime
import math

def ler_dados_no_intervalo(caminho_arquivo, inicio_str, fim_str):
    # Convertendo as strings de tempo para objetos datetime
    tempo_inicio = datetime.strptime(inicio_str, '%d/%m/%y %H:%M:%S')
    tempo_fim = datetime.strptime(fim_str, '%d/%m/%y %H:%M:%S')

    dados_selecionados = []

    with open(caminho_arquivo, 'r') as arquivo:
        for linha in arquivo:
            partes_dados = linha.strip().split(';')
            dicionario_dados = {p.split('=')[0]: p.split('=')[1] for p in partes_dados}

            # Convertendo o campo DATETIME em objeto datetime
            tempo_dado = datetime.strptime(dicionario_dados['DATETIME'], '%d/%m/%y %H:%M:%S')

            # Verificando se o tempo está dentro do intervalo
            if tempo_inicio <= tempo_dado <= tempo_fim:
                dados_selecionados.append(linha.strip())

    return dados_selecionados

def extrair_dados_para_listas(lista_dados):
    latitudes = []
    longitudes = []
    altitudes = []
    velocidades = []

    for dado_str in lista_dados:
        partes_dados = dado_str.split(';')
        dicionario_dados = {p.split('=')[0]: p.split('=')[1] for p in partes_dados}

        latitudes.append(float(dicionario_dados['LAT']))
        longitudes.append(float(dicionario_dados['LON']))
        altitudes.append(float(dicionario_dados['ALTITUDE']))
        velocidades.append(float(dicionario_dados['SPEED']))

    return latitudes, longitudes, altitudes, velocidades

def calcular_deslocamento(latitudes, longitudes):
    if not latitudes or not longitudes:
        return 0

    latitude_inicial = latitudes[0]
    longitude_inicial = longitudes[0]
    latitude_final = latitudes[-1]
    longitude_final = longitudes[-1]

    deslocamento = haversine(latitude_inicial, longitude_inicial, latitude_final, longitude_final)
    return deslocamento

def haversine(lat1, lon1, lat2, lon2):
    # Raio da Terra em metros
    R = 6371000

    # Converte coordenadas de graus para radianos
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Diferenças nas coordenadas
    dif_lon = lon2_rad - lon1_rad
    dif_lat = lat2_rad - lat1_rad

    # Fórmula de Haversine
    a = math.sin(dif_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dif_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distância total
    distancia = R * c
    return distancia

def calcular_distancia_3d(lat1, lon1, alt1, lat2, lon2, alt2):
    # Distância horizontal entre os pontos
    distancia_horizontal = haversine(lat1, lon1, lat2, lon2)

    # Diferença de altitude (vertical)
    distancia_vertical = alt2 - alt1

    # Distância total 3D usando o Teorema de Pitágoras
    distancia = math.sqrt(distancia_horizontal**2 + distancia_vertical**2)
    return distancia

def calcular_distancia_total_3d(latitudes, longitudes, altitudes):
    distancia_total = 0.0
    
    # apenas soma tudo com o return da função
    for i in range(1, len(latitudes)):
        distancia_total += calcular_distancia_3d(
            latitudes[i-1], longitudes[i-1], altitudes[i-1],
            latitudes[i], longitudes[i], altitudes[i]
        )

    return distancia_total

def calcular_aceleracao_instantanea(velocidades):
    aceleracoes = [0]  # A primeira aceleração é 0 pois não temos um ponto anterior para comparar

    for i in range(1, len(velocidades)):
        # Aceleração = Variação da velocidade / Variação do tempo (assumindo que o tempo entre medições é constante)
        aceleracao = velocidades[i] - velocidades[i - 1]
        aceleracoes.append(aceleracao)

    return aceleracoes

def montar_json(id_lancamento, volume, peso, angulo, pressao, deslocamento, latitudes, longitudes, altitudes, velocidades):
    aceleracoes = calcular_aceleracao_instantanea(velocidades)
    passeio = []
    # print(aceleracoes)

    for i in range(len(latitudes)):
        ponto = {
            "latitude": latitudes[i],
            "longitude": longitudes[i],
            "altitude": altitudes[i],
            "velocidadeInst": velocidades[i],
            "aceleracaoInst": aceleracoes[i]
        }
        passeio.append(ponto)

    dados_json = {
        "idLancamento": id_lancamento,
        "volume": volume,
        "peso": peso,
        "angulo": angulo,
        "pressao": pressao,
        "distancia": deslocamento,
        "passeio": passeio
    }

    return json.dumps(dados_json, indent=4)

id_lancamento = 0
volume = 4.4
peso = 700
angulo = 45
pressao = 217 

# Caminho para o arquivo
caminho_arquivo = 'dados_gps.txt'

# Definindo o intervalo de tempo desejado
inicio_str = '01/12/23 10:00:00'
fim_str = '01/12/23 10:00:04'

# Lendo os dados dentro do intervalo de tempo
dados_no_intervalo = ler_dados_no_intervalo(caminho_arquivo, inicio_str, fim_str)

# Usando a função para extrair os dados
latitudes, longitudes, altitudes, velocidades = extrair_dados_para_listas(dados_no_intervalo)

# Calculando o deslocamento total
deslocamento = calcular_deslocamento(latitudes, longitudes)

# Calculando a distância total 3D percorrida pelo foguete
distancia_total_3d_metros = calcular_distancia_total_3d(latitudes, longitudes, altitudes)

json_final = montar_json(id_lancamento, volume, peso, angulo, pressao, deslocamento, latitudes, longitudes, altitudes, velocidades)

print(f"O deslocamento total da trajetória do foguete é: {deslocamento} metros")
print(f"A distância total 3D percorrida pelo foguete é: {distancia_total_3d_metros} metros")
json_final = montar_json(id_lancamento, volume, peso, angulo, pressao, deslocamento, latitudes, longitudes, altitudes, velocidades)
# print(json_final)