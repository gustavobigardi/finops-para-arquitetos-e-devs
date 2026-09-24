#!/usr/bin/env bash
# Caça ao desperdício: roda todas as queries .kql desta pasta no Azure Resource Graph.
#
#   ./cacar.sh                      # subscription atual do az CLI
#   ./cacar.sh <subscription-id>    # outra subscription
#
# Pré-requisitos: az login e a extensão resource-graph (az extension add --name resource-graph).
set -euo pipefail

pasta="$(cd "$(dirname "$0")" && pwd)"
subscription="${1:-$(az account show --query id -o tsv)}"
total=0

# O Resource Graph consulta o tenant do contexto atual do az: a subscription precisa estar nele.
tenant_alvo="$(az account show --subscription "$subscription" --query tenantId -o tsv)"
tenant_atual="$(az account show --query tenantId -o tsv)"
if [ "$tenant_alvo" != "$tenant_atual" ]; then
  echo "A subscription $subscription está em outro tenant. Rode antes:"
  echo "  az account set --subscription $subscription"
  exit 1
fi

echo "Subscription: $(az account show --subscription "$subscription" --query name -o tsv) ($subscription)"
for arquivo in "$pasta"/*.kql; do
  titulo="$(head -1 "$arquivo" | sed 's#^// *##')"
  # remove comentários e junta em uma linha para o az graph query
  query="$(grep -v '^[[:space:]]*//' "$arquivo" | tr '\n' ' ')"
  quantidade="$(az graph query -q "$query | count" --subscriptions "$subscription" --query 'data[0].Count' -o tsv)"
  total=$((total + quantidade))
  echo
  echo "== $(basename "$arquivo" .kql): $quantidade encontrado(s)"
  echo "   $titulo"
  if [ "$quantidade" -gt 0 ]; then
    az graph query -q "$query" --subscriptions "$subscription" --first 50 -o table
  fi
done
echo
echo "Total de achados: $total"
