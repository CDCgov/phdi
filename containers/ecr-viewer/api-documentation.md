# View eCR

Display an eCR

**URL** : `/view-data?id=:id&auth=:auth`

**URL Parameters** : 
- `id=[string]` where `id` is the ID of the eCR.
- `auth=[string]` where `auth` is the authentication token for the user

**Method** : `GET`

**Auth required** : YES

**Permissions required** : None


## Success Response

**Condition** : If the eCR exists and authentication is valid.

**Code** : `200 OK`

**Content** : eCR will be displayed to the user

## Error Responses

**Condition** : If the eCR does not exist with `id`

**Code** : `404 NOT FOUND`

**Content** : Error will be displayed to user

### Or

**Condition** : If the authentication is invalid

**Code** : `401 UNAUTHORIZED`

**Content** : Error will be displayed to user
