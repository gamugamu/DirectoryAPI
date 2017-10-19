[TOC]

## Description:
_Directories simule la structure d’un répertoire de fichiers. Permet de créer / supprimer des documents markdown avec une restriction de droits et gestion de groupe._

---

## Code ref API:
**D** (dataType)
**H** (header)
**S** (services)
**I** (interface)
**P** (protocole)
**G** (GET)
**F** (Format)

---
# Protocoles #
---
## Règles Tout Services
### #Pa01
 * L’API des services est en https avec un certificat valide.
 * [root] doit être en https.

### #Pa02
 * L’API des services est versionné.

### #Pa03
 * Le header contient la version en cours de l’API avec pour key Version.

---
# Services
---

## ASKTOKEN

_Permet de recevoir un ***#Db02:Token*** qui permet de consommer les services de base de l’API. Les droits du token sont limité à ***#Ed01:unauth***._
<br>

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/asktoken
{: .header } **HEADER** | \{**token-request**: **#Fb01**:TokenRequest}
{: .get } **GET**
{: .return } **RETURN**  | \{**error**: **#Da00**:error, **token**: **#Db02**:token}  

### #SaP01
* Le service est de structure **[root]/rest/[v]/asktoken**.
* Le header contient le **#Fb01**:TokenRequest.

### #SaD01
* Retourne une data-structure de type {**error**: **#Da00**:Error, **token**: **#Db02**:Token}.
* **En cas de succès**, retourne **#Da00**:Error[code:**success**] et un **#Db02**:Token[right:**unauth**].
* **En cas d’échec**, si la clef d’API est incorrecte, retourne un **#Da00**:Error[code:**invalid_apikey**] et un **#Db02**:Token vide.

<br>
###### Exemple:
~~~~.html
curl --header "Content-Type: application/json" -H "token: 5895db72e1c944a4b186dd6101b80cf0|0|2017-10-07_20:09:24" http://127.00.0.1:8000 '{"loginrequest" : {"email" : "bebeUFW@gmail.com", "cryptedpassword" : "I7mHCIWiwTyyct50ENCkIHjGDcLfSQ3CT4HVkAYDtT63fDFjlrKheap5kaQ="}}'

// output
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.</p>
curl: (3) [globbing] nested brace in column 19
~~~~
---
## CREATEACCOUNT

Permet de créer un compte. Retourne un #Da00:Error[code:success] si la création de compte a réussi.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/createaccount
{: .header } **HEADER** | \{**token** : ``#Fb02``[right : >= unauth]}
{: .post } **POST** | {**loginrequest** : ``#Dc01``:LoginRequest}
{: .return } **RETURN**  | \{**error**: ``#Da00``:error}  

### #SbP01
* Le service est de structure **[root]/rest/[v]/createaccount**.
* Le header contient le #Fb02:Token avec des droit supérieur ou égal à unauth.
* En POST, Le #Dc01:LoginRequest doit être fourni.

### #SbD01
* En cas de succès, Retourne un #Da00:Error[code : #Ea01:success].
* En cas d’échec, retourne un #Da00:Error relatif à l’erreur.

### #SbR01
* Chaque compte est unique. Créer un doublon est impossible.
* Retourne code : #Ea01:user_already_exist si le compte existe déjà.

### #SbR02
* Le compte doit être conforme à #Ra01:RegexEmail ou renvoie un
``#Da00``:Error[code : invalid_user_email]
* Le mot de passe doit être conforme à #Ra02: RegexPassword ou renvoie un #Da00:Error[code :invalid_user_password].
