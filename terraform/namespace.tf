# resource "kubernetes_namespace" "cybersapient_namespace" {
#   metadata {
#     annotations = {
#       name = "${var.environment}"
#     }

#     labels = {
#       mylabel = "label-value"
#     }

#     name = "${var.environment}"
#   }
# }