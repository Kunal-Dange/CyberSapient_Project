module "roles" {
  source = "./modules/iam_roles"

  roles_json = (file("${path.module}/roles.json"))
  
}
