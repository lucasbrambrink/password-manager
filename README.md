# password-manager
Platform to store passwords securely

UI (Web/app) <-> Server API <-> Vault API

Write blog / about page
write intro / marketing page

* authenticate devices (gen device keys)
    * if unrecognized device, ask for OTP

* set up OTP pipeline
    * create email client to send codes to users

* fix user-gen token (not strong enough)
* avoid root token completely

* fix user archive key generation
    * use pbkdf2 (~100000 iterations)
DONE

* add a bunch of extra fields to Password object
    * username
    * notes, tags, etc
DONE

