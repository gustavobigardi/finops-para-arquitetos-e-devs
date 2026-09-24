#!/usr/bin/env python3
"""Reproduz os números da palestra "FinOps para arquitetos e devs" (MVP Conf 2026).

Preços: Azure Retail Prices API (preço de lista, USD, pay-as-you-go).
Câmbio: PTAX de venda do Banco Central do Brasil. É só uma estimativa: a sua
fatura usa a taxa do seu contrato (no MCA, a taxa é fixada uma vez por mês).

Só usa a biblioteca padrão do Python 3.

    python3 cenarios.py                    # PTAX mais recente
    python3 cenarios.py --data 2026-09-21  # PTAX de um dia específico
    python3 cenarios.py --json resultados.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview"
PTAX = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{data}'&$format=json"
)
CACHE = Path(__file__).parent / ".cache"
HORAS_MES = 730
BR, EUA, EUA2 = "brazilsouth", "eastus", "eastus2"


# --------------------------------------------------------------------------- #
# Acesso às APIs (com cache local e backoff, porque a API de preços devolve 429)
# --------------------------------------------------------------------------- #

def _get_json(url: str) -> dict:
    for tentativa in range(6):
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as erro:
            if erro.code == 429:
                time.sleep(5 * (tentativa + 1))
                continue
            raise
    raise RuntimeError(f"a API continua devolvendo 429: {url}")


def precos(filtro: str) -> list[dict]:
    """Todos os itens da Retail Prices API para um filtro OData (com cache)."""
    CACHE.mkdir(exist_ok=True)
    arquivo = CACHE / f"{hashlib.sha1(filtro.encode()).hexdigest()[:16]}.json"
    if arquivo.exists():
        return json.loads(arquivo.read_text())
    url, itens = f"{API}&$filter={urllib.parse.quote(filtro)}", []
    while url:
        pagina = _get_json(url)
        itens += pagina["Items"]
        url = pagina.get("NextPageLink")
        time.sleep(1)
    arquivo.write_text(json.dumps(itens))
    return itens


def item(itens: list[dict], **criterios) -> dict:
    """Escolhe exatamente um item. Critério terminado em `__contem` testa substring."""
    achados = []
    for it in itens:
        ok = True
        for chave, valor in criterios.items():
            if chave.endswith("__contem"):
                ok &= valor in it[chave.removesuffix("__contem")]
            elif chave.endswith("__sem"):
                ok &= valor not in it[chave.removesuffix("__sem")]
            else:
                ok &= it.get(chave) == valor
        if ok:
            achados.append(it)
    if len(achados) != 1:
        nomes = [(a["productName"], a["skuName"], a["meterName"], a.get("tierMinimumUnits")) for a in achados]
        raise LookupError(f"{criterios} → {len(achados)} itens: {nomes[:5]}")
    return achados[0]


def preco(servico: str, regiao: str, **criterios) -> float:
    filtro = f"serviceName eq '{servico}' and armRegionName eq '{regiao}'"
    if "priceType" not in criterios:
        criterios["type"] = criterios.get("type", "Consumption")
    return item(precos(filtro), **criterios)["unitPrice"]


def ptax(data: dt.date | None) -> tuple[float, dt.date]:
    dia = data or dt.date.today()
    for _ in range(10):  # volta até achar um dia útil com cotação
        valores = _get_json(PTAX.format(data=dia.strftime("%m-%d-%Y")))["value"]
        if valores:
            return valores[-1]["cotacaoVenda"], dia
        dia -= dt.timedelta(days=1)
    raise RuntimeError("PTAX não encontrada nos últimos 10 dias")


# --------------------------------------------------------------------------- #
# Preços usados nos cenários
# --------------------------------------------------------------------------- #

def vm_d4s_v5(regiao: str) -> dict:
    itens = precos(
        f"serviceName eq 'Virtual Machines' and armRegionName eq '{regiao}' "
        "and armSkuName eq 'Standard_D4s_v5'"
    )
    linux = [i for i in itens if "Windows" not in i["productName"]]
    payg = item(linux, type="Consumption", meterName="D4s v5")
    plano = {p["term"]: p["unitPrice"] for p in payg.get("savingsPlan", [])}
    return {
        "payg": payg["unitPrice"],
        "sp1": plano.get("1 Year"),
        "sp3": plano.get("3 Years"),
        "ri1": item(linux, type="Reservation", reservationTerm="1 Year")["unitPrice"] / (12 * HORAS_MES),
        "ri3": item(linux, type="Reservation", reservationTerm="3 Years")["unitPrice"] / (36 * HORAS_MES),
        "spot": item(linux, type="Consumption", meterName="D4s v5 Spot")["unitPrice"],
    }


def app_service(regiao: str, sku: str) -> float:
    return preco("Azure App Service", regiao, productName="Azure App Service Premium v3 Plan - Linux",
                 skuName=sku, meterName=f"{sku} App") if sku.startswith("P") else \
        preco("Azure App Service", regiao, productName="Azure App Service Basic Plan - Linux",
              skuName=sku, meterName=sku)


def log_analytics(regiao: str) -> dict:
    analytics = item(
        precos(f"serviceName eq 'Log Analytics' and armRegionName eq '{regiao}'"),
        type="Consumption", meterName="Analytics Logs Data Ingestion", tierMinimumUnits=5.0,
    )["unitPrice"]
    monitor = precos(f"serviceName eq 'Azure Monitor' and armRegionName eq '{regiao}'")
    return {
        "analytics": analytics,
        "basic": item(monitor, type="Consumption", meterName="Basic Logs Data Ingestion")["unitPrice"],
        "auxiliary": item(monitor, type="Consumption", meterName="Auxiliary Logs Data Ingestion")["unitPrice"],
    }


def foundry(meter: str) -> float:
    """Preço por 1M de tokens de um deployment Global Standard (igual em qualquer região)."""
    itens = precos(
        "serviceName eq 'Foundry Models' and armRegionName eq 'eastus2' and "
        "(productName eq 'Azure OpenAI GPT5' or productName eq 'Azure OpenAI GPT6')"
    )
    return item(itens, type="Consumption", meterName=meter)["unitPrice"]


def cosmos(regiao: str) -> dict:
    itens = precos(f"serviceName eq 'Azure Cosmos DB' and armRegionName eq '{regiao}'")
    return {
        "manual_100": item(itens, type="Consumption", productName="Azure Cosmos DB",
                           skuName="RUs", meterName="100 RU/s")["unitPrice"],
        "autoscale_100": item(itens, type="Consumption", productName="Azure Cosmos DB autoscale", meterName="AP1 100 RUs",
                              skuName="AP1")["unitPrice"],
        "serverless_1m": item(itens, type="Consumption", productName="Azure Cosmos DB serverless",
                              meterName="1M RUs")["unitPrice"],
    }


def blob_hot(regiao: str, redundancia: str) -> float:
    itens = precos(
        f"serviceName eq 'Storage' and armRegionName eq '{regiao}' "
        "and productName eq 'General Block Blob v2'"
    )
    return item(itens, type="Consumption", meterName=f"Hot {redundancia} Data Stored",
                tierMinimumUnits=0.0)["unitPrice"]


# --------------------------------------------------------------------------- #
# Cenários
# --------------------------------------------------------------------------- #

def cenario_hospedagem() -> dict:
    """3 APIs pequenas + 2 workers de fila, tráfego em horário comercial."""
    aks = preco("Azure Kubernetes Service", BR, meterName="Standard Uptime SLA")
    vm = vm_d4s_v5(BR)["payg"]
    p0v3 = app_service(BR, "P0v3")
    aca = precos(f"serviceName eq 'Azure Container Apps' and armRegionName eq '{BR}'")
    vcpu_s = item(aca, type="Consumption", meterName="Standard vCPU Active Usage")["unitPrice"]
    gib_s = item(aca, type="Consumption", meterName="Standard Memory Active Usage")["unitPrice"]

    # Container Apps: 0,5 vCPU / 1 GiB por réplica; APIs ativas 12 h/dia em 22 dias úteis,
    # workers ativos 4 h/dia; fora disso escalam a zero. Franquia mensal por subscription:
    # 180.000 vCPU-s e 360.000 GiB-s (requisições abaixo de 2 milhões/mês são grátis).
    segundos = 3 * 12 * 22 * 3600 + 2 * 4 * 22 * 3600
    vcpu_total, gib_total = 0.5 * segundos, 1.0 * segundos
    aca_mes = max(0, vcpu_total - 180_000) * vcpu_s + max(0, gib_total - 360_000) * gib_s

    return {
        "titulo": "Hospedagem: plataforma do tamanho do workload",
        "premissas": [
            "3 APIs pequenas + 2 workers de fila, uso em horário comercial (Brazil South, Linux)",
            "AKS tier Standard com 3 nós D4s v5 (12 vCPU/48 GiB) 24/7 — o mínimo comum para HA",
            "App Service: 1 plano P0v3 com 2 instâncias (2 vCPU/8 GiB) 24/7",
            "Container Apps (consumo): 0,5 vCPU/1 GiB por réplica, escala a zero fora do horário",
            "Só compute: sem discos, load balancer, egress ou logs",
        ],
        "linhas": [
            ("AKS Standard + 3× D4s v5", aks * HORAS_MES + 3 * vm * HORAS_MES),
            ("App Service 2× P0v3", 2 * p0v3 * HORAS_MES),
            ("Container Apps (consumo, com franquia)", aca_mes),
        ],
    }


def cenario_nao_prod() -> dict:
    itens = precos(f"serviceName eq 'API Management' and armRegionName eq '{BR}'")
    unid = lambda m: item(itens, type="Consumption", meterName=m)["unitPrice"] * HORAS_MES
    premium, standard_v2, developer = unid("Premium Unit"), unid("Standard v2 Unit"), unid("Developer Unit")
    vm = vm_d4s_v5(BR)["payg"]
    horario = 12 * 22  # 12 h/dia em 22 dias úteis
    return {
        "titulo": "Ambientes não produtivos",
        "premissas": [
            "APIM: o módulo de prod (Premium, 1 unidade) copiado para dev, qa, hml e prod",
            "Alternativa: Developer em dev/qa, Standard v2 em hml, Premium só em prod",
            "VMs de dev: 4× D4s v5 ligadas 24/7 × só em horário comercial (12 h × 22 dias)",
        ],
        "linhas": [
            ("APIM Premium nos 4 ambientes", 4 * premium, "apim"),
            ("APIM com SKU por ambiente", 2 * developer + standard_v2 + premium, "apim"),
            ("Dev: 4× D4s v5 ligadas 24/7", 4 * vm * HORAS_MES, "vm"),
            ("Dev: 4× D4s v5 em horário comercial", 4 * vm * horario, "vm"),
        ],
    }


def cenario_observabilidade() -> dict:
    br, eua2 = log_analytics(BR), log_analytics(EUA2)
    gb_mes = lambda gb_dia: gb_dia * 30
    franquia = 5  # GB/mês grátis por conta de cobrança (Analytics Logs, pay-as-you-go)

    antes = (gb_mes(50) - franquia) * br["analytics"]
    # Depois: 30 GB/dia de logs de container caem 70% com nível Warning e vão para Basic;
    # 15 GB/dia de telemetria do App Insights com sampling de 25%; 5 GB/dia de outros
    # continuam em Analytics.
    depois = (gb_mes(15 * 0.25 + 5) - franquia) * br["analytics"] + gb_mes(30 * 0.30) * br["basic"]
    return {
        "titulo": "Observabilidade",
        "premissas": [
            "50 GB/dia em Analytics Logs: 30 GB de logs de container, 15 GB de App Insights, 5 GB de outros",
            "Otimização: nível Warning nos containers (−70%) e tabela em Basic Logs; sampling de 25% no App Insights",
            f"Franquia de {franquia} GB/mês por conta de cobrança; retenção dentro dos 31 dias inclusos",
        ],
        "linhas": [
            ("50 GB/dia em Analytics (Brazil South)", antes),
            ("Mesmo volume em East US 2", (gb_mes(50) - franquia) * eua2["analytics"]),
            ("Otimizado (Brazil South)", depois),
        ],
    }


def cenario_ia() -> dict:
    conversas, chamadas, tok_in, tok_out = 100_000, 3, 3_000, 400
    m_in = conversas * chamadas * tok_in / 1e6    # milhões de tokens de entrada
    m_out = conversas * chamadas * tok_out / 1e6  # milhões de tokens de saída

    def custo(modelo: str, cache: float = 0.0) -> float:
        entrada = foundry(f"{modelo} ShortCo Inp Std Gl 1M Tokens")
        lido = foundry(f"{modelo} ShortCo Cd Inp Std Gl 1M Tokens")
        escrito = foundry(f"{modelo} ShortCo Cd Wr Std Gl 1M Tokens")
        saida = foundry(f"{modelo} ShortCo Opt Std Gl 1M Tokens")
        # cache: fração da entrada lida do cache; 1% dela é reescrita quando o cache expira
        return (m_in * (1 - cache) * entrada + m_in * cache * lido
                + m_in * cache * 0.01 * escrito + m_out * saida)

    sol, terra, luna = custo("5.6 sol"), custo("5.6 terra"), custo("5.6 luna")
    return {
        "titulo": "IA: o modelo certo para cada tarefa",
        "premissas": [
            f"{conversas:,} conversas/mês × {chamadas} chamadas × {tok_in:,} tokens de entrada e {tok_out} de saída",
            "Global Standard, contexto curto; preços por 1M de tokens da família GPT-5.6",
            "Roteamento: 80% das chamadas no luna, 20% no terra; cache: 70% da entrada vem do cache",
        ],
        "linhas": [
            ("gpt-6-astra", custo("6-astra")),
            ("gpt-5.6-sol", sol),
            ("gpt-5.6-terra", terra),
            ("gpt-5.6-luna", luna),
            ("Roteamento 80% luna / 20% terra", 0.8 * luna + 0.2 * terra),
            ("Roteamento + cache de prompt", 0.8 * custo("5.6 luna", 0.7) + 0.2 * custo("5.6 terra", 0.7)),
        ],
    }


def cenario_rodada_rapida() -> dict:
    fw = precos(f"serviceName eq 'Azure Firewall' and armRegionName eq '{BR}'")
    fw_h = lambda m: item(fw, type="Consumption", meterName=m)["unitPrice"] * HORAS_MES
    c = cosmos(BR)
    pico, base = 5_000, 1_000  # RU/s
    return {
        "titulo": "Rodada rápida: rede, escala e resiliência",
        "premissas": [
            "Firewall Premium em cada um de 4 spokes × um Standard compartilhado no hub (só a hora fixa)",
            "Cosmos DB: pico de 5.000 RU/s por 2 h/dia; no resto do dia, ~1.000 RU/s (média de 300 RU/s consumidos no serverless)",
            "Blob Hot, 10 TB: LRS × ZRS × GRS (o GRS do Brazil South replica para South Central US)",
        ],
        "linhas": [
            ("Firewall Premium × 4 spokes", 4 * fw_h("Premium Deployment"), "fw"),
            ("Firewall Standard no hub", fw_h("Standard Deployment"), "fw"),
            ("Cosmos manual 5.000 RU/s 24/7", pico / 100 * c["manual_100"] * HORAS_MES, "cosmos"),
            ("Cosmos autoscale (máx. 5.000)", (2 * pico + 22 * base) / 100 * c["autoscale_100"] * 30, "cosmos"),
            ("Cosmos serverless (média 300 RU/s)", 300 * HORAS_MES * 3600 / 1e6 * c["serverless_1m"], "cosmos"),
            ("Blob Hot 10 TB LRS", 10_240 * blob_hot(BR, "LRS"), "blob"),
            ("Blob Hot 10 TB ZRS", 10_240 * blob_hot(BR, "ZRS"), "blob"),
            ("Blob Hot 10 TB GRS", 10_240 * blob_hot(BR, "GRS"), "blob"),
        ],
    }


def cenario_compra() -> dict:
    br, eua2 = vm_d4s_v5(BR), vm_d4s_v5(EUA2)
    return {
        "titulo": "Comprar melhor, por último (1 VM D4s v5 Linux)",
        "premissas": ["Brazil South, 730 h/mês; Spot pode ser despejada com 30 s de aviso"],
        "linhas": [
            ("Pay-as-you-go", br["payg"] * HORAS_MES),
            ("Savings plan 1 ano", br["sp1"] * HORAS_MES),
            ("Savings plan 3 anos", br["sp3"] * HORAS_MES),
            ("Reserva 1 ano", br["ri1"] * HORAS_MES),
            ("Reserva 3 anos", br["ri3"] * HORAS_MES),
            ("Spot", br["spot"] * HORAS_MES),
            ("Pay-as-you-go em East US 2", eua2["payg"] * HORAS_MES),
        ],
    }


def cenario_regiao() -> dict:
    """Ágio do Brazil South sobre East US 2, serviço a serviço (preço unitário)."""
    la_br, la_us = log_analytics(BR), log_analytics(EUA2)
    cos_br, cos_us = cosmos(BR), cosmos(EUA2)
    apim = lambda r: preco("API Management", r, meterName="Standard v2 Unit")
    fw = lambda r: preco("Azure Firewall", r, meterName="Standard Deployment")
    aca = lambda r: preco("Azure Container Apps", r, meterName="Standard vCPU Active Usage")
    aks = lambda r: preco("Azure Kubernetes Service", r, meterName="Standard Uptime SLA")
    pares = [
        ("VM D4s v5 (Linux)", vm_d4s_v5(BR)["payg"], vm_d4s_v5(EUA2)["payg"]),
        ("App Service P1v3 (Linux)", app_service(BR, "P1 v3"), app_service(EUA2, "P1 v3")),
        ("Log Analytics (Analytics)", la_br["analytics"], la_us["analytics"]),
        ("Log Analytics (Basic)", la_br["basic"], la_us["basic"]),
        ("Blob Hot LRS (GB)", blob_hot(BR, "LRS"), blob_hot(EUA2, "LRS")),
        ("Cosmos DB (100 RU/s)", cos_br["manual_100"], cos_us["manual_100"]),
        ("Container Apps (vCPU-s)", aca(BR), aca(EUA2)),
        ("AKS tier Standard", aks(BR), aks(EUA2)),
        ("API Management Standard v2", apim(BR), apim(EUA2)),
        ("Azure Firewall Standard", fw(BR), fw(EUA2)),
    ]
    return {
        "titulo": "Brazil South × East US 2 (preço unitário)",
        "premissas": ["Ágio = preço Brazil South ÷ preço East US 2 − 1"],
        "agio": [(nome, br, us, br / us - 1) for nome, br, us in pares],
    }


def cenario_preview() -> dict:
    """Caso de Vitória: plano compartilhado × um plano por preview (East US 2)."""
    b1, p0v3 = app_service(EUA2, "B1"), app_service(EUA2, "P0v3")
    previews, dias = 10, 7
    return {
        "titulo": "Preview environments (caso Data Saturday Vitória)",
        "premissas": [
            f"{previews} previews por mês, cada um vivo por {dias} dias (TTL padrão), East US 2",
            "Compartilhado: um App Service Plan B1 24/7 para main + todos os previews",
            "Sem compartilhar: cada preview com o próprio plano (B1, ou P0v3 para paridade com prod)",
            "Deployment GlobalStandard do modelo não tem custo fixo: tokens são consumo nos dois casos",
        ],
        "linhas": [
            ("Plano B1 compartilhado (total do mês)", b1 * HORAS_MES),
            ("Um B1 por preview", previews * dias * 24 * b1),
            ("Um P0v3 por preview", previews * dias * 24 * p0v3),
        ],
    }


CENARIOS = [cenario_hospedagem, cenario_nao_prod, cenario_observabilidade, cenario_ia,
            cenario_rodada_rapida, cenario_compra, cenario_regiao, cenario_preview]


# --------------------------------------------------------------------------- #
# Saída
# --------------------------------------------------------------------------- #

def brl(valor: float, cambio: float) -> str:
    return f"R$ {valor * cambio:,.0f}".replace(",", ".")


def usd(valor: float) -> str:
    return f"US$ {valor:,.0f}".replace(",", ".") if valor >= 10 else f"US$ {valor:.2f}".replace(".", ",")


def main() -> None:
    args = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    args.add_argument("--data", help="data da PTAX (AAAA-MM-DD); padrão: hoje ou o último dia útil")
    args.add_argument("--json", help="grava os resultados neste arquivo")
    opcoes = args.parse_args()

    cambio, dia = ptax(dt.date.fromisoformat(opcoes.data) if opcoes.data else None)
    print(f"# Cenários — preços de lista (Azure Retail Prices API), {dt.date.today():%d/%m/%Y}")
    print(f"Câmbio: PTAX de venda de {dia:%d/%m/%Y} = R$ {cambio:.4f} (estimativa; a fatura usa a taxa do contrato)\n")

    resultados = {"ptax": cambio, "data_ptax": dia.isoformat(), "cenarios": []}
    for funcao in CENARIOS:
        c = funcao()
        resultados["cenarios"].append(c)
        print(f"## {c['titulo']}")
        for premissa in c["premissas"]:
            print(f"- {premissa}")
        print()
        if "agio" in c:
            print("| Serviço | Brazil South | East US 2 | Ágio |\n|---|---:|---:|---:|")
            for nome, br, us, agio in c["agio"]:
                print(f"| {nome} | {br:.6g} | {us:.6g} | {agio:+.0%} |")
        else:
            print("| Opção | USD/mês | ≈ BRL/mês |\n|---|---:|---:|")
            bases: dict = {}
            for rotulo, valor, *grupo in c["linhas"]:
                base = bases.setdefault(grupo[0] if grupo else None, valor)
                delta = "" if valor == base or not base else f" ({valor / base - 1:+.0%})"
                print(f"| {rotulo} | {usd(valor)}{delta} | {brl(valor, cambio)} |")
        print()

    if opcoes.json:
        Path(opcoes.json).write_text(json.dumps(resultados, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
