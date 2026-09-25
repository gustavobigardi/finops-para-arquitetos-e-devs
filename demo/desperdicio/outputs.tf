output "resource_group" {
  value = azurerm_resource_group.demo.name
}

output "criados" {
  value = compact([
    azurerm_managed_disk.orfao.name,
    azurerm_public_ip.sem_uso.name,
    azurerm_network_interface.orfa.name,
    var.criar_plano ? one(azurerm_service_plan.vazio[*].name) : "",
    var.criar_disco_premium ? one(azurerm_managed_disk.orfao_premium[*].name) : "",
  ])
}
