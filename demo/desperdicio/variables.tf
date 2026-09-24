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
