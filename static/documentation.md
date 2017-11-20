[TOC]

## Description:
_Directory permet d'organiser un ensemble de repertoires de fichiers. Créer / supprimer des documents markdown avec une restriction de droits et gestion de groupe._

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
## Règles applicables à tout services
### #Pa01
 * L’API des services est en https avec un certificat valide.
 * [root] doit être en https.

### #Pa02
 * L’API des services est versionnée.

### #Pa03
 * Le header contient une clef **version** qui renseigne la version en cours de l’API.
 ex: **version**:1.0.0

---
# Services
---

## ASKTOKEN

_Récupère un [**#Db02**:Token](#db02-token) pour consommer les services de l’API. Les droits du token sont limités à ***[**#ED01:**](#ed01-right)unauth***._
<br>

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/asktoken
{: .header } **HEADER** | \{**token-request**: [**#Fb01**:TokenRequest](**#Fb01**:TokenRequest)}
{: .get } **GET**
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error), **token**: [**#Db02**:Token](#db02-token)}  

### #SaP01
* Le service est en GET **[root]/rest/[v]/asktoken**.
* Le header contient le [**#Fb01**:TokenRequest](**#Fb01**:TokenRequest).

### #SaD01
* Retourne un {**error**: [**#Da00**:Error](#da00-error), **token**: [**#Db02**:Token](#db02-token)}.
* **En cas de succès**, retourne un {[**#Da00**:Error](#da00-error)[**code**:success], [**#Db02**:Token](#db02-token)[**right**:unauth]}.
* **En cas d’échec**, si la clef d’API est incorrecte, retourne un {[**#Da00**:Error](#da00-error)[**code**:invalid_apikey], [**#Db02**:Token](#db02-token)} où le token est vide.

<br>
###### Exemple:
~~~~.Bash
curl http://127.00.0.1:8000/rest/0.0.2/asktoken --header "Content-Type: application/json" -H "token-request: I7mHCIWiwTyyct50ENCkIHjGDcLfSQ3CT4HVkAYDtT63Pe9YC2MX3ViyfrxK9AgJcm2A_A==" }
~~~~

~~~~.html
// output
{
	"token": {
		"dateLimit": "2017-10-19_16:36:09",
		"right": "0",
		"hash": "gNNeGwYSz-4Upa_mHOVkAvfF9KLZhcJX66weQcupioYOY2hJX7Q84Vwd-ae0_QaQT79kzKPcToaBDdhfWoN2Gw=="
	},
	"error": {
		"code": "1",
		"description": "request success"
	}
}
~~~~

---
## CREATEACCOUNT

Créé un compte. Retourne un [**#Da00**:Error](#da00-Error)[**code**:success] si la création de compte a réussi.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/createaccount
{: .header } **HEADER** | \{**token** : [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= unauth]}
{: .post } **POST** | {**loginrequest** : [#**Dc01**:LoginRequest](#dc01-loginrequest)}
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-Error)}  

### #SbP01
* Le service est en POST **[root]/rest/[v]/createaccount**.
* Le header contient le [**#Fb02**:TokenFormat](#fb02-tokenformat) avec des droit supérieur ou égaux à unauth.
* Le [#**Dc01**:LoginRequest](#dc01-loginrequest) doit être fourni en POST.

### #SbD01
* **En cas de succès**, Retourne un [**#Da00**:Error](#da00-Error)[**code**: [**#Ea01:**](#ea01-status)success].
* **En cas d’échec**, retourne un [**#Da00**:Error](#da00-Error) relatif à l’erreur.

### #SbR01
* **Chaque compte est unique**. Créer un doublon est impossible.
* Retourne un **code**: [**#Ea01:**](#ea01-status)user_already_exist si le compte existe déjà.

### #SbR02
* Le compte doit être conforme à [**#Ra01:**RegexEmail](#ra01-regexemail) ou renvoie un
[**#Da00**:Error](#da00-Error)[**code**: invalid_user_email]
* Le mot de passe doit être conforme à [**#Ra02:**RegexPassword](#ra01-regexpassword) ou renvoie un [**#Da00**:Error](#da00-error)[**code**: invalid_user_password].

~~~~.Bash
curl --header "Content-Type: application/json" -H "token": "htZXjL4dbTXrsUI3WVz3BV4mOh8enaRBnqYuTt0RP9he_klbwGmIZMLgT77YLZT_id-CusOsgGX_Q8ygoo_RLQ==" http://127.00.0.1:8000/rest/0.0.2/createaccount -d '{"loginrequest": {"cryptpassword": "I7mHCIWiwTyyct50ENCkIHjGDcLfSQ3CT4HVkAYDtT63fDFjlrKheap5kaT4tX9yhVl1oDH5n6HqrKXRVXrY57-M1OEdLH_--WqdzWw=", "email": "xxxx.@xx.com"}}'
~~~~


~~~~.html
// output
{
	u 'error': {
		u 'code': u '1',
		u 'description': u 'request success'
	}
}
// le compte a été créé
~~~~

---
## DELETEACCOUNT

Supprime le compte lié au token.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/deleteAccount
{: .header } **HEADER** | \{**token:** [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= logged]}
{: .get } **GET** |
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error)}

### #ScP01
* Le service est de structure **[root]/rest/[v]/deleteAccount**.
* Le header contient le [**#Fb02**:TokenFormat](#fb02-tokenformat) avec des droit supérieur ou égaux à unauth.

### #ScD01
* Retourne une data-structure de type [[**#Da00**:Error](#da00-error)].
* **En cas de succès**, retourne un [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)success].
* **En cas d’échec**, retourne un [**#Da00**:Error](#da00-error) relatif à l’erreur.

---
## LOGIN

Identification à l’API Directories. Renvoie un [**#Da01:**User](#dd01-user) et un token lié au compte, de droit supérieur ou égaux à [**#ED01:**](#ed01-right)logged. En cas de compte/password invalide, renvoie un [**#Da01:**User](#dd01-user) vide.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/login
{: .header } **HEADER** | \{**token** : [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= unauth]}
{: .post } **POST** | {**loginrequest** : [#**Dc01**:LoginRequest](#dc01-loginrequest)}
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error), **user**: [**#Dd01**:User](#dd01-user), **token:**[**#Db02**:Token](#db02-token)}  

### #SdP01
* Le service est en GET **[root]/rest/[v]/login**.
* Le [#**Dc01**:LoginRequest](#dc01-loginrequest) doit être fourni en POST.
* Le header contient le [**#Fb02**:TokenFormat](#fb02-tokenformat) avec des droits supérieurs ou égaux à unauth.

### #SdD01
* En cas de succès, retourne un [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)success], un [**#Dd01**:User](#dd01-user) et un nouveau [**#Db02**:Token](#db02-token) avec des droits supérieur ou égauxe à [**#ED01:**](#ed01-right)logged.
* En cas d’échec, retourne un [**#Da00**:Error](#da00-error) relatif à l’erreur.

### #SdR01
* Retourne un [**#Da00**:Error](#da00-error)[**code**: user_already_logged] si l’utilisateur est déjà connecté.
* Retourne un [**#Da00**:Error](#da00-error)[**code**: user_not_found] si l’utilisateur n’existe pas.
* Retourne un [**#Da00**:Error](#da00-error)[**code**: user_pass_email_mismatch] si le password ne correspond pas au compte.

---
## LOGOUT

Se déconnecte du compte lié au token. Nécessite un token dans le header dont les droits sont supérieurs ou égaux à [**#ED01:**](#ed01-right)logged. Retourne un nouveau token avec des droits restreints à [**#ED01:**](#ed01-right)unauth. L’ancien token devient invalide.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/logout
{: .header } **HEADER** | \{**token**: [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= logged]}
{: .get } **GET** |
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error), **token:** [**#Db02**:Token](#db02-token)}

### #SeP01
* Le service est en GET **[root]/rest/[v]/logout**.
* Le header contient le [**#Fb02**:TokenFormat](#fb02-tokenformat) avec des droit supérieur ou égaux à logged.

### #SeD01
* En cas de succès, retourne un [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)success] et un token avec des droit réduits [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= unauth].
* En cas d’échec, retourne un [**#Da00**:Error](#da00-error) relatif à l’erreur.

### #SeR01
* Une fois déconnecté, le token du compte devient invalide.

---

## CREATEFILE

Créé un fichier. Retourne le fichier complet. Nécessite un token dont les droits sont supérieurs ou égaux à [**#ED01:**](#ed01-right)logged.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/createfile
{: .header } **HEADER** | \{**token**: [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= logged]}
{: .post } **POST** | {**filetype:** [**#Ia01:**FileType](#ia01-filetype)}
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error), **filePayload:** [**#Ia04**:FilePayload](#ia04-filepayload)}

### #SfP01
* Le service est en POST **[root]/rest/[v]/createFile**.
* En POST, le [**#Ia01:**FileType](#ia01-filetype) avec le type de fichier souhaité.
* Le header contient le [**#Fb02**:TokenFormat](#fb02-tokenformat) avec des droits supérieurs ou égaux à logged.

### #SfD01
* **En cas de succées**, retourne un [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)success] et un [**#Ia04**:FilePayload](#ia04-filepayload) avec le type de fichier demandé.
* **En cas d’échec**, retourne un [**#Da00**:Error](#da00-error) relatif à l’erreur et un [**#Ia04**:FilePayload](#ia04-filepayload) vide.

### #SfR01
* Si le type de fichier est invalide, renvoie un [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)file_unknow_type].

---

## MODIFYFILE

Modifie un fichier. Nécessite un token dont les droits sont supérieurs ou égaux à [**#ED01:**](#ed01-right)logged.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/modifyFile
{: .header } **HEADER** | \{**token**: [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= logged]}
{: .post } **POST** | {**filePayload:** [**#Ia04**:FilePayload](#ia04-filepayload)}
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error), **filePayload:** [**#Ia04**:FilePayload](#ia04-filepayload)}

### #SgP01
* Le service est en POST **[root]/rest/[v]/modifyFile**.
* En POST, le [**#Ia04**:FilePayload](#ia04-filepayload) du fichier que l’on souhaite modifier.
* Le header contient le [**#Fb02**:TokenFormat](#fb02-tokenformat) avec des droits supérieurs ou égaux à logged.

### #SgD01
* **En cas de succées**, retourne un [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)success].
* **En cas d’échec**, retourne un [**#Da00**:Error](#da00-error) relatif à l’erreur.

### #SgR01
* Renvoie un  [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)not_permitted] si les droits du fichier ne  permettent pas sa modification.

---

## DELETEFILE
Supprime un fichier. Nécessite un token dont les droits sont supérieurs ou égaux à [**#ED01:**](#ed01-right)logged.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/deletefile
{: .header } **HEADER** | \{**token**: [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= logged]}
{: .post } **POST** | {**fileid:** [**#Ia02:**FileID](#ia02-fileid)}
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error)}

### #ShP01
* Le service est en POST **[root]/rest/[v]/deleteFile**.
* En POST, Le [**#Ia02:**FileID](#ia02-fileid) du fichier que l’on souhaite supprimer.  
* Le header contient le [**#Fb02**:TokenFormat](#fb02-tokenformat) avec des droit supérieurs ou égaux à logged.

### #ShD01
* **En cas de succées**, retourne un [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)success].
* **En cas d’échec**, retourne un [**#Da00**:Error](#da00-error) relatif à l’erreur.

### #SRD01
* Renvoie un [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)not_permitted] si les droits du fichier ne  permettent pas sa modification.

---

## FILESHEADER

Récupère une liste de [**#Ia03:**FileHeader](#ia03-fileheader) relative aux [**#Ia02:**FileID](#ia02-fileid) du POST.
Nécessite un token dont les droits sont supérieurs ou égaux à [**#ED01:**](#ed01-right)unauth.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/filesheader
{: .header } **HEADER** | \{**token**: [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= unauth]}
{: .post } **POST** | {**filesid:** [[**#Ia02:**FileID](#ia02-fileid)]}
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error),  **filesheader:** [[**#Ia03:**FileHeader](#ia03-fileheader)]}

### #SiP01
* Le service est en POST **[root]/rest/[v]/filesheader**.
* En POST, La liste de [[**#Ia02:**FileID](#ia02-fileid)] des fichiers à récupérer.  
* Le header contient le [**#Fb02**:TokenFormat](#fb02-tokenformat) avec des droits supérieurs ou égaux à logged.

### #SiD01
* **En cas de succées**, retourne un [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)success] et la liste des [[**#Ia03:**FileHeader](#ia03-fileheader)] récupérés.
* **En cas d’échec**, retourne un [**#Da00**:Error](#da00-error) relatif à l’erreur.

---

## FILESPAYLOAD

Récupére une liste de #Ia03:FilePayload relative aux [**#Ia02:**FileID](#ia02-fileid) du POST.
Nécessite un token dont les droits sont supérieurs ou égaux à [**#ED01:**](#ed01-right)unauth. Si l’utilisateur n’a pas les droits pour accéder aux fichiers, retourne une erreur et un payload vide.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/filespayload
{: .header } **HEADER** | \{**token**: [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= logged]}
{: .post } **POST** | {**filesid:** [[**#Ia02:**FileID](#ia02-fileid)]}
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error),  **filespayload:** [[**#Ia04**:FilePayload](#ia04-filepayload)]}

### #SjP01
* Le service est en POST **[root]/rest/[v]/filespayload**.
* En POST, La liste de [[**#Ia02:**FileID](#ia02-fileid)] des fichiers à récupérer.  
* Le header contient le [**#Fb02**:TokenFormat](#fb02-tokenformat) avec des droits supérieurs ou égaux à unauth.

### #SjD01
* **En cas de succées**, retourne un [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)success] et la liste des [[**#Ia04**:FilePayload](#ia04-filepayload)] récupérés.
* **En cas d’échec**, retourne un [**#Da00**:Error](#da00-error) relatif à l’erreur.

---

## GRAPH

Renvoie la hierachie d'une collection de documents.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/graph
{: .header } **HEADER** | \{**token**: [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right:** >= logged]}
{: .post } **POST** | {**filesid:** [[**#Ia02:**FileID](#ia02-fileid)]}
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error),  **filespayload:** [[**#Ia04**:FilePayload](#ia04-filepayload)]}

### #SkP01
* Le service est en POST **[root]/rest/[v]/graph**.
* En POST, Le [[**#Ia02:**FileID](#ia02-fileid)] du fichier.  
* Le header contient le [**#Fb02**:TokenFormat](#fb02-tokenformat) avec des droits supérieurs ou égaux à unauth.

### #SkD01
* **En cas de succées**, retourne le graph des fichiers enfants en liste hierarchique. [**#Da00**:Error](#da00-error)[**code**: [**#Ea01:**](#ea01-status)success] et la liste des [[**#Ia04**:FilePayload](#ia04-filepayload)] récupérés.
* **En cas d’échec**, retourne un [**#Da00**:Error](#da00-error) relatif à l’erreur et un graph vide.

---

## HISTORY

Renvoie l'historique de documents par utilisateur.

commande| data
------- | -------------
{: .uri } **URI** | [root]/rest/[v]/history
{: .header } **HEADER** | \{**token**: [**#Fb02**:TokenFormat](#fb02-tokenformat)[**right**: >= logged]}
{: .post } **POST** | {**option**: [[**#Df01:**Option](#df01-option)]}
{: .return } **RETURN**  | \{**error**: [**#Da00**:Error](#da00-error),  **filesheader**: [[**#Ia03:**FileHeader](#ia03-fileheader), **iterator**: [**#dg01**:Iterator](#dg01-iterator)]}

---
# Datastructures
---

## #Da00: Error
&#8203; |key| description | type
---|-- | ---|---------
{.row_30_px} **1** | code | Retourne le status de la requète.  | [**#Ea01:**](#ea01-status)Status
**2** | description | Description de l’erreur | String


## #Db02: Token
&#8203; |key| description | type
---|-- | ---|---------
{.row_30_px} **1**  | hash | Une clef unique qui permet d’identifier le client des services.  | String
**2** | dateLimit | Date d'expiration du token. | [**#Fa01:**](#fa01-date)Date
**3** | right | La permission sur les services. | [**#ED01:**](#ed01-right)Right


## #Dc01: LoginRequest
&#8203; |key| description | type
---|-- | ---|---------
{.row_30_px} **1** | email | Une clef unique qui permet d’identifier le client des services.  | String
**2** | cryptpassword | Password au format [**#Fd01:** EncryPassword](#fd01-encrypassword). | [**#Fd01:**EncryPassword](#fd01-encrypassword)

## #Dd01: User
&#8203; |key| description | type
---|-- | ---|---------
{.row_30_px} **1** | uid | L’identifiant unique qui permet d’identifier l’utilisateur.  | String
**2** | email | Email de l’utilisateur. | String
**3** | name | Nom de l’utilisateur. | String
**4** | groups | Les id de groupes auquel l’utilisateur appartient. | [[**#la02**: FileID](#ia02-fileid)]

## #De01: Rule
&#8203; |key| description | type
---|-- | ---|---------
{.row_30_px} **1** | owner | L’id de la personne concernée par la règle.  | [**#Dd01**:User](#dd01-user)[id]
**2** | permission | La permission sur le document. | [**#Ec01**:FilePermission](#ec01-filepermission)

## #Df01: Option
&#8203; |key| description | type
---|-- | ---|---------
{.row_30_px} **1** | group_name | Le nom du group demandé  | Bool
**2** | file_payload | Retourne le payload si demandé   | Bool

## #Dg01: Iterator
&#8203; |key| description | type
---|-- | ---|---------
{.row_30_px} **1** | elmts_by_page | Le nombre d'éléments renvoyés par page | Int
**2** | iteration | L'itération en cours  | Int
**3** | max_iteration | Le nombre total de pages  | Int

## #Ia01: FileType
&#8203; |key| description | type
---|-- | ---|---------
{.row_30_px} **1** | type | Le type de document.  | [**#Eb01:**FileType](#eb01-filetype)
**2** | name | Le nom du document. | String
**3** | parentId | L’id du parent si il existe. | [**#Ia01:**FileType](#ia01-filetype)[id]

## #Ia02: FileID
&#8203; |key| description | type
---|-- | ---|---------
{: .blank_row .row_30_px} | {: .blank_row}| {: .blank_row} ***hérite de [#Ia01: FileType](#ia01-filetype)*** |{: .blank_row}|{: .blank_row}
**4** | uid | Identifiant unique du document.  | String

## #Ia03: FileHeader
&#8203; |key| description | type
---|-- | ---|---------
{: .blank_row .row_30_px} | {: .blank_row}| {: .blank_row} ***hérite de [#Ia02: FileId](#ia02-fileid)*** |{: .blank_row}|{: .blank_row}
**5** | owner | La personne qui a crée le document.  | [**#Dd01**:User](#dd01-user)[id]
**6** | title | Titre du document. | String
**7** | date | Date de création du document. | [**#Fa01:**](#fa01-date)Date
**8** | rules | Liste des règles de droits par utilisateur. | [[**#De01:**Rule](#de01-rule)]
**9** | childsId | Liste de fichiers que le fileHeader contient. Peut être nul.| [[**#Ia01:**FileType](#ia01-filetype)[id]]

## #Ia04: FilePayload
&#8203; |key| description | type
---|-- | ---|---------
{: .blank_row .row_30_px} | {: .blank_row}| {: .blank_row} ***hérite de [#Ia03: FileHeader](#ia03-fileheader)*** |{: .blank_row}|{: .blank_row}
**10** | payload | Le contenu du document.  | String

---
# Enum
---

### #Ea01: Status

&#8203; |name
---|--
{.row_30_px} **0** | unknow
**1** | success
**2** | invalid_apikey
**3** | invalid_token
{: .blank_row}  |  {: .blank_row} **format regex**
**10** | invalid_user_email
**11** | invalid_user_password
**12** | invalid_token
{: .blank_row} |  {: .blank_row} **Post Status**
**20** | not_permitted
**21** | token_header_missing
**22** | token_request_header_missing
**23** | invalid_json
{: .blank_row} |  {: .blank_row} **Loggin Status**
**30** | user_already_exist
**31** | user_not_found
**32** | user_already_logged
**33** | user_pass_email_mismatch
{: .blank_row} |  {: .blank_row} **File Status**
**50** | file_unknow_type

## #Eb01: FileType
&#8203; |name
---|--
{.row_30_px} **0** | unknow
**1** | group
**2** | folder
**3** | markdown
**4** | other

## #Ec01: FilePermission
&#8203; |name
---|--
{.row_30_px} **0**  | forbidden
**1** | read
**2** | modify

## #ED01: Right
&#8203; |name
---|--
{.row_30_px} **0** | none
**1** | unauth
**2** | logged
**3** | superUser

---
# Format
---

## #Fa01 Date
&#8203; |format
---|--
format | MM-DD-YYYY_Thh:mmTZD
exemple | 2017-10-07_11:44:11

## #Fb01: TokenRequest
&#8203; |format
---|--
format | AES(secretAPIKey\|[**#Fa01:**](#fa01-date)CurrentDate)
exemple | AES(fdskhdfsizzfbhzc\|2017-10-07_11:44:11)

## #Fc01: TokenFormat
&#8203; |format
---|--
format | AES(generatedAccessKey\|[**#ED01:**](#ed01-right)Right\|[**#Fa01:**](#fa01-date)DateLimite)
exemple | fdskhdfsizzsgsqfbhzc\|1\|2017-10-09_11:44:11

## #Fd01: EncryPassword
&#8203; |format
---|--
format | AES(secretAPIKey|password)
exemple | AES(fdskhdfsizzsgsqfbhzc|mot-de-passe)

## #Ra01: RegexEmail
&#8203; |format
---|--
format | xxx@xx.x
exemple | moncompte@mail.com

## #Ra01: RegexPassword
&#8203; |format
---|--
format | 8 caractères min, 1 majuscule, 1 signe spécial, 1 chiffre
exemple | mot2Pass&
