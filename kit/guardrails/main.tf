# Guardrails de custo para uma subscription: tags, regiões, SKUs de não-prod, budget e anomalias.
# Guardrail avisa e orienta; não bloqueia o time sem motivo. Budget não desliga nada.

terraform {
  required_version = ">= 1.6"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

data "azurerm_subscription" "atual" {}

# Policies built-in, buscadas pelo nome de exibição
data "azurerm_policy_definition" "tag_no_rg" {
  display_name = "Require a tag on resource groups"
}

data "azurerm_policy_definition" "herdar_tag_do_rg" {
  display_name = "Inherit a tag from the resource group if missing"
}

data "azurerm_policy_definition" "regioes" {
  display_name = "Allowed locations"
}

data "azurerm_policy_definition" "skus_vm" {
  display_name = "Allowed virtual machine size SKUs"
}

resource "azurerm_resource_group" "finops" {
  name     = "rg-finops-guardrails"
  location = var.location
  tags     = var.tags
}

# 1. Todo resource group nasce com dono e ambiente
resource "azurerm_subscription_policy_assignment" "tag_no_rg" {
  for_each             = toset(var.tags_obrigatorias)
  name                 = "tag-obrigatoria-rg-${each.value}"
  display_name         = "Resource group precisa da tag ${each.value}"
  subscription_id      = data.azurerm_subscription.atual.id
  policy_definition_id = data.azurerm_policy_definition.tag_no_rg.id
  parameters           = jsonencode({ tagName = { value = each.value } })
}

# 2. Recursos herdam essas tags do resource group (grava no recurso; funciona até em pay-as-you-go)
resource "azurerm_subscription_policy_assignment" "herdar_tag" {
  for_each             = toset(var.tags_obrigatorias)
  name                 = "herdar-tag-${each.value}"
  display_name         = "Herdar a tag ${each.value} do resource group"
  subscription_id      = data.azurerm_subscription.atual.id
  policy_definition_id = data.azurerm_policy_definition.herdar_tag_do_rg.id
  location             = var.location
  parameters           = jsonencode({ tagName = { value = each.value } })

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "herdar_tag" {
  for_each             = azurerm_subscription_policy_assignment.herdar_tag
  scope                = data.azurerm_subscription.atual.id
  role_definition_name = "Tag Contributor"
  principal_id         = each.value.identity[0].principal_id
}

# 3. Regiões permitidas (decisão de custo, latência e LGPD)
resource "azurerm_subscription_policy_assignment" "regioes" {
  name                 = "regioes-permitidas"
  display_name         = "Regiões permitidas"
  subscription_id      = data.azurerm_subscription.atual.id
  policy_definition_id = data.azurerm_policy_definition.regioes.id
  parameters           = jsonencode({ listOfAllowedLocations = { value = var.regioes_permitidas } })
}

# 4. SKUs de VM permitidos nos resource groups de não-prod
resource "azurerm_resource_group_policy_assignment" "skus_vm_nao_prod" {
  for_each             = toset(var.resource_groups_nao_prod)
  name                 = "skus-vm-nao-prod"
  display_name         = "SKUs de VM permitidos em não-prod"
  resource_group_id    = "${data.azurerm_subscription.atual.id}/resourceGroups/${each.value}"
  policy_definition_id = data.azurerm_policy_definition.skus_vm.id
  parameters           = jsonencode({ listOfAllowedSKUs = { value = var.skus_vm_nao_prod } })
}

# 5. Quem recebe os avisos
resource "azurerm_monitor_action_group" "finops" {
  name                = "ag-finops"
  resource_group_name = azurerm_resource_group.finops.name
  short_name          = "finops"
  tags                = var.tags

  dynamic "email_receiver" {
    for_each = { for i, email in var.emails : tostring(i) => email }
    content {
      name          = "email-${email_receiver.key}"
      email_address = email_receiver.value
    }
  }
}

# 6. Budget mensal: 90/100/110% do real e 110% da previsão (WAF CO:03)
resource "azurerm_consumption_budget_subscription" "mensal" {
  name            = "budget-mensal"
  subscription_id = data.azurerm_subscription.atual.id
  amount          = var.budget_mensal
  time_grain      = "Monthly"

  time_period {
    start_date = var.inicio_budget
  }

  dynamic "notification" {
    for_each = {
      real-90      = { limite = 90, tipo = "Actual" }
      real-100     = { limite = 100, tipo = "Actual" }
      real-110     = { limite = 110, tipo = "Actual" }
      previsao-110 = { limite = 110, tipo = "Forecasted" }
    }
    content {
      enabled        = true
      threshold      = notification.value.limite
      threshold_type = notification.value.tipo
      operator       = "GreaterThanOrEqualTo"
      contact_emails = var.emails
      contact_groups = [azurerm_monitor_action_group.finops.id]
    }
  }

  lifecycle {
    ignore_changes = [time_period]
  }
}

# 7. Alerta de anomalia de custo (só existe em escopo de subscription)
resource "azurerm_cost_anomaly_alert" "finops" {
  name            = "anomalia-de-custo"
  display_name    = "Anomalia de custo"
  subscription_id = data.azurerm_subscription.atual.id
  email_subject   = "Anomalia de custo detectada"
  email_addresses = var.emails
}
