resource "aws_ecr_repository" "ynabri_repositories" {
  for_each             = toset(local.repository_list)
  name                 = each.value
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(local.common_tags, {
    Name = each.value
  })
}