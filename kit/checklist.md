# Checklist de revisão de arquitetura orientada a custo

Use em design review, ADR ou PR de infraestrutura. Cada item aponta o item correspondente do checklist do pilar de custo do Azure Well-Architected Framework (CO:01 a CO:14, tabela no fim).

## Antes de desenhar

- [ ] Qual é a unidade de negócio (pedido, cliente, tenant) e o custo-alvo por unidade? (CO:01, CO:02)
- [ ] O workload tem dono (tag `owner`), centro de custo e budget definidos? (CO:03, CO:04)
- [ ] Região decidida com critério: tem dado pessoal ou regulado? Qual a latência aceitável? Por que Brazil South ou por que EUA? (CO:05, LGPD)

## Serviço e escala

- [ ] A plataforma é do tamanho do workload (capacidade real, horas de uso, pico)? (CO:07, CO:12)
- [ ] Onde o uso é intermitente, escala a zero ou tem autoscale? (CO:12)
- [ ] O modelo de cobrança combina com o perfil de carga: provisionado, autoscale ou serverless? (CO:06)

## Ambientes

- [ ] Dev e QA têm SKU próprio, sem copiar o de produção? (CO:08)
- [ ] Não-prod tem horário comercial, auto-shutdown ou TTL? (CO:08)
- [ ] Ambientes efêmeros compartilham o que é caro e isolam o que carrega estado? (CO:08, CO:14)

## Dados, rede e resiliência

- [ ] A redundância (LRS, ZRS, GRS, multirregião) está justificada por RTO/RPO? O GRS do Brazil South replica para South Central US. (CO:10)
- [ ] O tráfego entre regiões está mapeado? Sair do Brasil custa US$ 0,16/GB. App e banco ficam na mesma região? (CO:09)
- [ ] Firewall, Private Endpoints e gateways estão consolidados no hub, e não um por ambiente? (CO:14)
- [ ] Blob tem lifecycle (tiers) e o backup tem retenção definida? (CO:10)

## Observabilidade

- [ ] O nível de log é definido por ambiente, e o App Insights tem sampling? (CO:11)
- [ ] Tabelas verbosas usam Basic ou Auxiliary, e a DCR descarta o ruído na ingestão? (CO:10)
- [ ] Commitment tier só entra com 100 GB/dia ou mais? O daily cap é tratado como cinto de segurança, e não como otimização? (CO:05)

## IA

- [ ] Cada tarefa usa o menor modelo que resolve, com roteamento? (CO:07)
- [ ] Cache de prompt e Batch para o que pode esperar? (CO:06, CO:11)
- [ ] O custo de tokens de um deployment compartilhado é rateado por produto ou ambiente? (CO:03)

## Operação e cultura

- [ ] Há tags obrigatórias e herança por Policy? (CO:03)
- [ ] O budget avisa em 90, 100 e 110% e na previsão, e o alerta de anomalia manda e-mail para alguém de verdade? (CO:04)
- [ ] O PR mostra o custo estimado e o ADR tem seção de custo? (CO:01)
- [ ] O time faz o ritual mensal de 30 minutos com caça ao desperdício? (CO:13)
- [ ] Reserva e savings plan só entram depois do right-size? (CO:05)

## Referência: checklist CO do Well-Architected

| Item | Recomendação |
|---|---|
| CO:01 | Criar uma cultura de responsabilidade financeira |
| CO:02 | Criar e manter um modelo de custo |
| CO:03 | Coletar e revisar dados de custo |
| CO:04 | Definir guardrails de gasto |
| CO:05 | Obter as melhores taxas dos provedores |
| CO:06 | Alinhar o uso aos incrementos de cobrança |
| CO:07 | Otimizar o custo dos componentes |
| CO:08 | Otimizar o custo dos ambientes |
| CO:09 | Otimizar o custo dos fluxos |
| CO:10 | Otimizar o custo dos dados |
| CO:11 | Otimizar o custo do código |
| CO:12 | Otimizar o custo de escala |
| CO:13 | Otimizar o tempo das pessoas |
| CO:14 | Consolidar recursos e responsabilidades |

Fonte: [Azure Well-Architected Framework, Cost Optimization checklist](https://learn.microsoft.com/azure/well-architected/cost-optimization/checklist).
