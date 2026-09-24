variable "subscription_id" {
  description = "Subscription onde os guardrails serão aplicados"
  type        = string
}

variable "location" {
  description = "Região do resource group de FinOps e da identidade da policy de herança"
  type        = string
  default     = "brazilsouth"
}

variable "emails" {
  description = "Quem recebe budget e anomalias (sem e-mail, o budget não serve para nada)"
  type        = list(string)

  validation {
    condition     = length(var.emails) > 0
    error_message = "Informe pelo menos um e-mail."
  }
}

variable "budget_mensal" {
  description = "Valor do budget mensal, na moeda da subscription"
  type        = number
}

variable "inicio_budget" {
  description = "Primeiro dia do mês em que o budget começa (RFC3339)"
  type        = string
  default     = "2026-10-01T00:00:00Z"
}

variable "tags_obrigatorias" {
  description = "Tags exigidas nos resource groups e herdadas pelos recursos"
  type        = list(string)
  default     = ["owner", "environment", "cost-center"]
}

variable "regioes_permitidas" {
  description = "Regiões permitidas na subscription"
  type        = list(string)
  default     = ["brazilsouth", "eastus2"]
}

variable "resource_groups_nao_prod" {
  description = "Resource groups de dev/teste que só podem usar os SKUs de VM abaixo"
  type        = list(string)
  default     = []
}

variable "skus_vm_nao_prod" {
  description = "SKUs de VM permitidos em não-prod"
  type        = list(string)
  default     = ["Standard_B2s", "Standard_B2ms", "Standard_D2s_v5", "Standard_D2as_v5"]
}

variable "tags" {
  description = "Tags dos recursos criados por este módulo"
  type        = map(string)
  default = {
    owner       = "time-plataforma"
    environment = "shared"
    cost-center = "finops"
  }
}
