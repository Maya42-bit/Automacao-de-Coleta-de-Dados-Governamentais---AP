import requests
from bs4 import BeautifulSoup, ResultSet, Tag
import re
import pandas as pd


while True:
    ano_consulta = input("Digite o ano da consulta (ex: 2024): ").strip()
    if ano_consulta.isdigit() and 2000 <= int(ano_consulta) <= 2100:
        break

while True:
    mes_consulta = input("Digite o mês da consulta (ex: 01 para Janeiro): ").strip()
    if mes_consulta.isdigit() and 1 <= int(mes_consulta) <= 12:
        mes_consulta = mes_consulta.zfill(2)
        break

nome_arquivo_saida_api = f'servidores_api_AP_{mes_consulta}{ano_consulta}.csv'

def limpar_linhas(arq_entrada, arq_saida):
    with open(arq_entrada, 'r', encoding='utf-8') as f_in, open(arq_saida, 'w', encoding='utf-8') as f_out:
        for linha in f_in:
            linha_corrigida = re.sub(r'^[0-9;]+', '', linha).strip()
            f_out.write(linha_corrigida +'\n')


def retornarTabela(html_string: str):
    soup = BeautifulSoup(html_string, 'html.parser')

    # Tabela
    tabela = soup.select('.tab-content table tbody td')
    resultado = [x.text.strip() for x in tabela]
    return re.split(r';;\d+', ";".join(resultado))


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

    # Fazer requisicao
    response = requests.post(
        f'http://www.transparencia.ap.gov.br/consulta/3/41/pessoal/folha-de-pagamento-por-servidor/detalhes/{pagina}',
        cookies=cookies,
        headers=headers,
        data=data,
        verify=False,
    )

    # Pegar tabela
    dados = retornarTabela(response.text)
    with open(f'{nome_arquivo_saida_api}', 'a', encoding='utf-8') as arquivo:
        for d in dados:
            arquivo.write(d[1:] + '\n')


# Looping principal para pegar os dados
if __name__ == '__main__':
    for x in range(1, 1470):
        fazerConsulta(str(x))
        print("Pagina concluída:"+str(x))
        
# Limpeza das linhas do arquivo
nm_arq_final = f'AP_{mes_consulta}{ano_consulta}_limpo.csv'

limpar_linhas(nome_arquivo_saida_api,nm_arq_final)

#Padronizar as colunas do arquivo final
colunas = ['NOME', 'ORGAO', 'CARGO', 'DATA_ADMISSAO','vazio','LOTACAO','CARGA_HORARIA', 'BRUTO', 'DECONTOS', 'LIQUIDO']
df = pd.read_csv('AP_022024_limpo.csv', on_bad_lines='skip', encoding="utf-8", sep=';', names=colunas)
df = df.drop("vazio", axis=1)
df.to_csv(f'AP_{mes_consulta}{ano_consulta}.csv', index=False, encoding='utf-8', sep=';') 

    
print("Cocnluido! Chefia!")
