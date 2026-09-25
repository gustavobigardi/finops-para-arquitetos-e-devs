variable "subscription_id" {
  description = "Subscription da demo (não use produção)"
  type        = string
}

variable "location" {
  description = "Região dos recursos da demo"
  type        = string
  default     = "eastus2"
}

variable "owner" {
  description = "Valor da tag owner"
  type        = string
  default     = "gustavo"
}

variable "criar_plano" {
  description = "Cria o App Service Plan vazio. Desligue se a subscription não tiver cota de plano pago"
  type        = bool
  default     = true
}

variable "plano_sku" {
  description = "SKU do App Service Plan vazio (B1, S1, P0v3...)"
  type        = string
  default     = "B1"
}

variable "plano_location" {
  description = "Região do plano, quando a cota só existe em outra região. Vazio usa var.location"
  type        = string
  default     = null
}

variable "criar_disco_premium" {
  description = "Cria um segundo disco órfão Premium, alternativa ao plano quando falta cota"
  type        = bool
  default     = false
}
