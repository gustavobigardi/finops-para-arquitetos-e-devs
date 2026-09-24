# Referências

Fontes usadas na palestra, com a data de publicação quando existe. Os preços foram coletados em 21/09/2026.

## Preços e câmbio

- [Azure Retail Prices API](https://learn.microsoft.com/rest/api/cost-management/retail-prices/azure-retail-prices): preço de lista em USD, pay-as-you-go. Todos os cenários saem de `kit/calculos/cenarios.py`.
- [PTAX do Banco Central (API Olinda)](https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/aplicacao#!/recursos): R$ 5,1117 de venda em 21/09/2026. É só estimativa: no MCA a fatura vem em BRL com a taxa do contrato, fixada no mês ([FAQ do MCA](https://learn.microsoft.com/azure/cost-management-billing/microsoft-customer-agreement/microsoft-customer-agreement-faq)).
- [Bandwidth pricing](https://azure.microsoft.com/pricing/details/bandwidth/): US$ 0,16/GB da América do Sul para outros continentes e US$ 0,05/GB no sentido inverso.

## Mercado

- Flexera, [State of the Cloud 2026](https://www.flexera.com/about-us/press-center/flexera-finds-cloud-value-is-rising-while-ai-waste-grows) (18/03/2026): 29% de desperdício estimado; 85% dizem que custo é o maior desafio.
- FinOps Foundation, [State of FinOps 2026](https://www.linuxfoundation.org/press/state-of-finops-survey-ai-value-and-skills-top-priorities-as-finops-matures-across-technology-value-98-manage-ai-90-saas-64-licensing-48-data-center-1) (19/02/2026): 98% gerenciam gasto com IA; orientação de arquitetura antes do deploy é a capacidade de ferramenta mais pedida.
- [Radar da Nuvem](https://canaltech.com.br/mercado/pesquisa-revela-que-65-das-empresas-brasileiras-nao-sabem-onde-gastam-com-nuvem/) (09/04/2026): 65% das empresas brasileiras não sabem onde gastam. **Ressalva:** a pesquisa tem apoio da Magalu Cloud.
- Grafana Labs, [Observability Survey 2025](https://grafana.com/observability-survey/2025/): observabilidade custa em média 17% do gasto de compute.
- Gartner via [CIO Dive](https://www.ciodive.com/news/ai-inference-costs-drop-2030-gartner/815725/) (25/03/2026): consultas agênticas usam de 5 a 30 vezes mais tokens.

## Ideias e frameworks

- Erik Peterson, CloudZero: "Every engineering decision is a buying decision" ([erikpeterson.com](https://erikpeterson.com/)).
- [The Frugal Architect](https://thefrugalarchitect.com/): lei III ("Architecting is a series of trade-offs") e lei VII ("Unchallenged success leads to assumptions").
- [FinOps Framework no Microsoft Learn](https://learn.microsoft.com/cloud-computing/finops/framework/finops-framework) e [FinOps Framework 2026](https://www.finops.org/insights/2026-finops-framework/).
- Azure Well-Architected Framework: [princípios de custo](https://learn.microsoft.com/azure/well-architected/cost-optimization/principles), [checklist CO:01–CO:14](https://learn.microsoft.com/azure/well-architected/cost-optimization/checklist) e [trade-offs](https://learn.microsoft.com/azure/well-architected/cost-optimization/tradeoffs).

## Casos públicos

- Prime Video: monitoramento −90% ao trocar serverless por um processo único ([InfoQ, 03/05/2023](https://www.infoq.com/news/2023/05/prime-ec2-ecs-saves-costs/)). **Ressalva:** o post original agora redireciona; use o Wayback Machine.
- Microsoft Inside Track: [otimização de custo no Azure dentro da Microsoft](https://www.microsoft.com/insidetrack/blog/implementing-microsoft-azure-cost-optimization-internally-at-microsoft/) (07/06/2022): Functions −82%, troca de tier do SQL −97%. **Ressalva:** é de 2022.
- Capacity: [4,2× mais barato com Phi-4](https://www.microsoft.com/en/customers/story/24201-capacity-azure-phi) (Microsoft, 29/05/2025).

## Azure: serviços e custos

- Log Analytics: [custos e table plans](https://learn.microsoft.com/azure/azure-monitor/logs/cost-logs), [daily cap](https://learn.microsoft.com/azure/azure-monitor/logs/daily-cap), [transformações de DCR](https://learn.microsoft.com/azure/azure-monitor/data-collection/data-collection-transformations), [sampling no App Insights](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-configuration).
- [Billing do Container Apps](https://learn.microsoft.com/azure/container-apps/billing): franquia de 180 mil vCPU-s, 360 mil GiB-s e 2 milhões de requisições por mês.
- Cosmos DB: [performance do serverless](https://learn.microsoft.com/azure/cosmos-db/serverless-performance) (5 mil RU/s por partição) e [como escolher a oferta](https://learn.microsoft.com/azure/cosmos-db/how-to-choose-offer).
- [Tráfego entre zonas de disponibilidade gratuito](https://learn.microsoft.com/azure/reliability/availability-zones-overview).
- [Savings plan (inclui bancos de dados)](https://learn.microsoft.com/azure/cost-management-billing/savings-plan/savings-plan-overview), [savings plan × reserva](https://learn.microsoft.com/azure/cost-management-billing/savings-plan/decide-between-savings-plan-reservation) e [fim da troca de reservas em 01/02/2027](https://learn.microsoft.com/azure/cost-management-billing/reservations/reservation-exchange-policy-changes).
- Foundry: [tipos de deployment](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/deployment-types), [disponibilidade por região](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure-region-availability), [privacidade de dados](https://learn.microsoft.com/azure/foundry/responsible-ai/openai/data-privacy), [prompt caching](https://learn.microsoft.com/azure/foundry/openai/how-to/prompt-caching) e [model router](https://learn.microsoft.com/azure/foundry/openai/concepts/model-router).

## Azure: regiões

- [Pares de regiões](https://learn.microsoft.com/azure/reliability/regions-paired): Brazil South é pareada com South Central US.
- [Residência de dados](https://azure.microsoft.com/explore/global-infrastructure/data-residency/).
- [Latência entre regiões](https://learn.microsoft.com/azure/networking/azure-network-latency): dados de julho de 2026.
- [Backups automáticos do Azure SQL](https://learn.microsoft.com/azure/azure-sql/database/automated-backups-overview): o padrão é GRS.

## Azure: governança e ferramentas

- [Budgets](https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets), [anomalias](https://learn.microsoft.com/azure/cost-management-billing/understand/analyze-unexpected-charges), [tag inheritance](https://learn.microsoft.com/azure/cost-management-billing/costs/enable-tag-inheritance) e [ofertas suportadas pelo Cost Management](https://learn.microsoft.com/azure/cost-management-billing/costs/understand-cost-mgt-data).
- [Azure Copilot para custos](https://learn.microsoft.com/azure/copilot/analyze-cost-management).
- [FinOps toolkit](https://learn.microsoft.com/cloud-computing/finops/toolkit/finops-toolkit-overview) e o [catálogo de boas práticas com queries do Resource Graph](https://learn.microsoft.com/cloud-computing/finops/best-practices/networking), base das queries do kit.
- [Advisor: recomendações de custo](https://learn.microsoft.com/azure/advisor/advisor-cost-recommendations).
- [Policies built-in](https://learn.microsoft.com/azure/governance/policy/samples/built-in-policies).

## Legislação (informativo, não é aconselhamento jurídico)

- [LGPD, Lei 13.709/2018](https://www2.camara.leg.br/legin/fed/lei/2018/lei-13709-14-agosto-2018-787077-publicacaooriginal-156212-pl.html), arts. 3º, 5º, 11 e 33 a 36.
- [Resolução CD/ANPD nº 19/2024](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd/resolucao-cd-anpd-no-19-de-23-de-agosto-de-2024): transferência internacional e cláusulas-padrão, com prazo de adoção até 23/08/2025.
- [Resolução CD/ANPD nº 32/2026](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/outros-documentos-e-publicacoes-institucionais/resolucao-no-32-decisao-de-adequacao-uniao-europeia-em-lingua-inglesa.pdf): adequação da União Europeia (26/01/2026). Veja também a [página da ANPD sobre transferência internacional](https://www.gov.br/anpd/pt-br/assuntos/assuntos-internacionais/transferencia-internacional-de-dados).
- [Resolução CMN nº 4.893/2021](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=4893), arts. 15 a 17 (nuvem em instituições financeiras), e Resolução BCB nº 85/2021.
- [IN GSI/PR nº 5/2021](https://www.legisweb.com.br/legislacao/?id=419510), art. 18, e [IN GSI/PR nº 8/2025](https://www.in.gov.br/en/web/dou/-/instrucao-normativa-gsi/pr-n-8-de-6-de-outubro-de-2025-660716869): nuvem no setor público federal.
- [Portaria SGD/MGI nº 5.950/2023](https://www.gov.br/governodigital/pt-br/contratacoes-de-tic/legislacao/modelo-de-contratacao-de-software-e-servicos-em-nuvem/vigentes/portaria-sgd-mgi-no-5-950-de-26-de-outubro-de-2023).
- [Resolução CFM nº 2.314/2022](https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2022/2314_2022.pdf) (telemedicina e guarda de prontuário).
- [Decreto nº 8.771/2016](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/decreto/d8771.htm), art. 14 (identificadores eletrônicos como dado pessoal).
