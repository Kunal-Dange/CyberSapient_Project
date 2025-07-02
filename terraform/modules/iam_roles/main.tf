resource "aws_iam_role" "roles" {
  for_each = var.iam_roles
  name     = each.value.name
  assume_role_policy = jsonencode(each.value.assume_role_policy)
  description        = each.value.description
  max_session_duration = each.value.max_session_duration
  tags               = each.value.tags
}

resource "aws_iam_role_policy" "policy" {
  for_each = var.iam_role_policies
  name     = each.value.name
  role     = aws_iam_role.roles[each.value.role_name].name
  policy   = jsonencode(each.value.policy)
}

resource "aws_iam_policy_attachment" "policy_attachment" {
  for_each = var.managed_policies
  name     = each.value.name
  roles    = [aws_iam_role.roles[each.value.role_name].name]
  policy_arn = each.value.policy_arn
}