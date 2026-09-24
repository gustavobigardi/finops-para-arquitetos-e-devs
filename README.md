# FinOps para arquitetos e devs: como construir em Azure sem explodir o orçamento

Materiais da palestra apresentada no **MVP Conf 2026** (26/09/2026, São Paulo) por Gustavo Bigardi.

> Em nuvem, decisão arquitetural também é decisão financeira. A palestra mostra, com preços oficiais do Azure, como escolhas de serviço, integração, observabilidade, escala, resiliência e região afetam o custo. Também mostra como criar uma cultura de eficiência técnica com responsabilidade financeira dentro do time.

## A mensagem em uma frase

Toda decisão de engenharia é uma decisão de compra, e o momento mais barato para economizar é no desenho e no PR, não na fatura.

## Conteúdo

| Pasta/arquivo | O que é |
|---|---|
| [`slides.pdf`](slides.pdf) | Slides da palestra |
| [`kit/calculos/`](kit/calculos) | `cenarios.py`: reproduz todos os números dos slides (Azure Retail Prices API + PTAX) |
| [`kit/desperdicio/`](kit/desperdicio) | 8 queries do Resource Graph e o `cacar.sh`, que roda todas |
| [`kit/guardrails/`](kit/guardrails) | Terraform com policies de tags, regiões e SKUs de não-prod, budget e alerta de anomalia |
| [`kit/checklist.md`](kit/checklist.md) | Checklist de revisão de arquitetura orientada a custo (WAF CO:01–CO:14) |
| [`demo/desperdicio/`](demo/desperdicio) | Terraform que cria recursos órfãos baratos para a demo |
| [`referencias.md`](referencias.md) | Fontes |

## Como usar o kit

### Reproduzir os números

Só precisa de Python 3, sem dependências:

```bash
python3 kit/calculos/cenarios.py
```

Para fixar a data da PTAX e salvar em JSON:

```bash
python3 kit/calculos/cenarios.py --data 2026-09-21 --json resultados.json
```

Para testar com o seu volume ou a sua região, mude as premissas nas funções `cenario_*`.

### Caçar desperdício

Instale a extensão do Resource Graph:

```bash
az extension add --name resource-graph
```

Selecione a subscription:

```bash
az account set --subscription "<sua subscription>"
```

Rode todas as queries:

```bash
./kit/desperdicio/cacar.sh
```

As queries são só leitura. Rode primeiro numa subscription de testes e revise o resultado antes de apagar qualquer coisa.

### Aplicar os guardrails

Veja [`kit/guardrails/README.md`](kit/guardrails/README.md).

## Avisos

- Os preços são de lista, em USD, sem descontos de contrato. Os valores em real são estimativas pela PTAX; a sua fatura usa a taxa do seu contrato.
- O conteúdo sobre LGPD e regulação é informativo e não é aconselhamento jurídico.
- Os números mudam: rode o `cenarios.py` de novo antes de usá-los numa decisão.
