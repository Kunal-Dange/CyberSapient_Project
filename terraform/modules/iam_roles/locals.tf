locals {
    roles =jsondecode(var.roles_json)

    inline_policies = flatten([
        for role in local.roles : try([
            for policy in role.inline_policies :[
                policy
            ]
        ], []
        )
        ]
    )

    map_inline_policies = try({
        for policy in local.inline_policies : 
            "${policy.role_name}_${policy.name}" =>  policy
        }
    )

    managed_policies = flatten([
        for role in local.roles : try([
            for policy in role.managed_policies :[
                policy
            ]
            ],[])
        ]
    )

    map_managed_policies =try({
        for policy in local.managed_policies : 
            "${policy.role_name}_${policy.name}" =>  policy
        },{}
    )
}