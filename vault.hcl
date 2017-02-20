backend "consul" {
  address = "127.0.0.1:8500"
  path = "vault"
}

listener "tcp" {
 address = "127.0.0.1:8200"
 tls_disable = 1
}

path "sys/*" {
  policy = "deny"
}

path "secret/*" {
  policy = "write"
}
