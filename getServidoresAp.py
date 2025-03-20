import requests
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd
import os

# Diretórios
base_dir = os.path.dirname(os.path.abspath(__file__))
downloads_dir = os.path.join(base_dir, "Downloads")
basepronta_dir = os.path.join(base_dir, "BasePronta")

# Criar as pastas se não existirem
os.makedirs(downloads_dir, exist_ok=True)
os.makedirs(basepronta_dir, exist_ok=True)

# Entrada do usuário
while True:
    ano_consulta = input("Digite o ano da consulta (ex: 2024): ").strip()
    if ano_consulta.isdigit() and 2000 <= int(ano_consulta) <= 2100:
        break

while True:
    mes_consulta = input("Digite o mês da consulta (ex: 01 para Janeiro): ").strip()
    if mes_consulta.isdigit() and 1 <= int(mes_consulta) <= 12:
        mes_consulta = mes_consulta.zfill(2)
        break

# Arquivos
nome_arquivo_saida_api = os.path.join(downloads_dir, f'servidores_api_AP_{mes_consulta}{ano_consulta}.csv')
nm_arq_final = os.path.join(basepronta_dir, f'AP_{mes_consulta}{ano_consulta}_limpo.csv')

# Função para limpar as linhas do arquivo
def limpar_linhas(arquivo_entrada, arquivo_saida):
    with open(arquivo_entrada, "r", encoding="utf-8") as f_in, open(arquivo_saida, "w", encoding="utf-8", newline="") as f_out:
        
        #leitor = csv.reader(f_in, delimiter=';')
        #escritor = csv.writer(f_out, delimiter=';')
        
        part_linha=0
        linha_anterior = ['','']
        campo_mod = ''

        for linha in f_in:
            
            # Ignora linhas vazias
            if not linha:
                exit  
            
            teste_count = linha.count(';')
            
            #Se a linha n tiver problema de quebra de texto
            if teste_count >= 7:
                #limpando linhas que possuem números no campo de nome
                campo_mod = pega_campo(linha, 1, ';')  # Pega o campo 1 da linha 0
                if campo_mod.isdigit() or campo_mod == '':
                    linha = linha.replace(campo_mod+';', '')
                             
            else:
                part_linha = part_linha + 1
                if linha_anterior[0]:

                    linha_anterior[1] = ";" + linha
                    #linha_anterior.extend(linha[1:])
                    linha_anterior[0] = linha_anterior[0].replace('\n', '')
                    linha = " ".join(linha_anterior)
                    f_out.write(linha)
                   
                    part_linha = 0
                    linha_anterior = ['','']
                    continue

                linha_anterior[0] = linha
                continue
            
            #escreve a linha no arquivo de saída
            f_out.write(linha)
            
def pega_campo(texto, ncampo, padrao):
    pedaco = 0  # Inicializa como inteiro
    vcampo = ''
    vposicao = 0  # Inicializa como inteiro

    for i in range(len(texto)):
        if texto[vposicao:vposicao+1] != padrao:  # Simula SUBSTR(texto, vposicao, 1)
            vcampo += texto[vposicao:vposicao+1]
        else:
            pedaco += 1
            if pedaco == ncampo:
                return vcampo.strip()
            vcampo = ''  # Reseta o campo para o próximo pedaço

        vposicao += 1  # Incrementa a posição

    return vcampo.strip()  # Retorna o último campo, caso necessário


# Função para extrair a tabela da resposta HTML
def retornarTabela(html_string: str):
    soup = BeautifulSoup(html_string, 'html.parser')
    tabela = soup.select('.tab-content table tbody td')
    resultado = [x.text.strip() for x in tabela]
    return re.split(r';;\d+', ";".join(resultado))

# Função para fazer a requisição e salvar os dados
def fazerConsulta(pagina: str) -> None:
    cookies = {
        'MINIME_SESSAO': 'o6lk94ipoe47j8qkmk3ospus36',
        '_gid': 'GA1.4.1909324950.1739906047',
        '_ga_99NVV0VZ96': 'GS1.1.1739905900.1.1.1739906068.0.0.0',
        '_ga': 'GA1.4.510970547.1739906047',
        '_ga_HEPRG9MJ35': 'GS1.1.1739906047.1.1.1739906119.0.0.0',
        '_ga_K4WQFLYGJ7': 'GS1.1.1739905900.1.1.1739906120.0.0.0',
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://www.transparencia.ap.gov.br',
        'Referer': 'http://www.transparencia.ap.gov.br/consulta/3/41/pessoal/folha-de-pagamento-por-servidor/detalhes/2',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    }
    data = {
        'parametros[pANO]': f'{ano_consulta}',
        'parametros[]': [
            f'{mes_consulta}',
            '',
        ],
        'filtro[NOME]': '',
        'filtro[SIGLA]': '',
        'filtro[CARGOEFETIVO]': '',
        'filtro[DATA_ADMISSAO]': '',
        'filtro[DATADEMISSAO ]': '',
        'filtro[LOTACAO ]': '',
        'filtro[CARGAHORARIA]': '',
        'filtro[BRUTO]': '',
        'filtro[DESCONTO]': '',
        'filtro[LIQUIDO]': '',
    }

    # Fazer requisição
    response = requests.post(
        f'http://www.transparencia.ap.gov.br/consulta/3/41/pessoal/folha-de-pagamento-por-servidor/detalhes/{pagina}',
        cookies=cookies,
        headers=headers,
        data=data,
        verify=False,
    )

    # Pegar tabela e salvar no arquivo de saída
    dados = retornarTabela(response.text)
    with open(f'{nome_arquivo_saida_api}', 'a', encoding='utf-8') as arquivo:
        for d in dados:
            arquivo.write(d[1:] + '\n')

# Loop para coletar os dados
if __name__ == '__main__':
    for x in range(1, 101):  #-> modificar para testes (original: 1470)
        fazerConsulta(str(x))
        print(f"Página {x} concluída!")

# Limpeza das linhas do arquivo
limpar_linhas(nome_arquivo_saida_api, nm_arq_final)

# Padronizar as colunas do arquivo final
colunas = ['NOME', 'ORGAO', 'CARGO', 'DATA_ADMISSAO', 'vazio', 'LOTACAO', 'CARGA_HORARIA', 'BRUTO', 'DESCONTOS', 'LIQUIDO']
df = pd.read_csv(nm_arq_final, on_bad_lines='skip', encoding="utf-8", sep=';', names=colunas)

# Remover coluna "vazio" que é um erro do CSV
df = df.drop("vazio", axis=1)

# Nome final da base tratada
arquivo_final = os.path.join(basepronta_dir, f'AP_{mes_consulta}{ano_consulta}.csv')

# Salvar CSV final na pasta BasePronta
df.to_csv(arquivo_final, index=False, encoding='utf-8', sep=';')

print("✅ Processo finalizado! Os arquivos foram organizados nas pastas corretamente.")
