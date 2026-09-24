# Guardrails de custo

Terraform que aplica numa subscription o mínimo de governança de custo mostrado na palestra:

| Guardrail | Como | Observação |
|---|---|---|
| Resource group com dono | Policy "Require a tag on resource groups" (Deny) | Uma atribuição por tag em `tags_obrigatorias` |
| Recursos herdam as tags | Policy "Inherit a tag from the resource group if missing" (Modify) | Grava a tag no recurso. Funciona em qualquer tipo de conta, ao contrário da tag inheritance do Cost Management (só EA/MCA) |
| Regiões permitidas | Policy "Allowed locations" | Região é decisão de custo, latência e LGPD |
| SKUs de VM em não-prod | Policy "Allowed virtual machine size SKUs" | Só nos resource groups de `resource_groups_nao_prod` |
| Budget mensal | 90%, 100% e 110% do real e 110% da previsão | Recomendação do WAF (CO:03). **Budget não desliga nada: ele avisa** |
| Anomalias | Alerta de anomalia de custo | Só existe em escopo de subscription; roda cerca de 36 h depois do fim do dia |

## Uso

```bash
cp terraform.tfvars.example terraform.tfvars   # preencha subscription, e-mails e valor do budget
terraform init
terraform plan
terraform apply
```

- **Deny e Modify impactam deploys.** Aplique primeiro numa subscription de testes. Para só observar, troque o efeito para `Audit`.
- A policy de herança só age em recursos novos ou atualizados. Para os existentes, crie uma remediation task.
- `emails` é obrigatório. Um budget sem destinatário não avisa ninguém; foi exatamente o que aconteceu no setup de Vitória.
