
https://www.notion.so/wealizedigital/Flujo-de-emisi-n-de-LEAR-29b56b87afa3801f88b6c1b3f8fdb482
https://www.notion.so/wealizedigital/Propuesta-cambio-Api-Integraci-n-17d56b87afa381489880e1d29a67a2b6





usar API KEY para llamar a Identify

Pedir API KEy en los endpoiys que me llama Identify

identify llamara a este componente

llamadas a identify


portal llama a third , generar VC representante
  valida accestoken



  credential_identifiers "/issuance/identifiers"
      viene profile con un valor fijo => variable de entorno 
      vc_type comprobar que es uno de los dos que permitimos (represente y empleado)
      subject_id No comprobar
    devolver
       


 /issuance/claims  

 vienen estos campos 

    "profile": string,
	"vc_type": string,
	"subject_id": string,
    "vc_identifier?": => vacio

    llamar a la fuente de la verdad. https://tmf.evidenceledger.eu/oapiv4/index.html?urls.primaryName=Party+Management+v4#/organization/retrieveOrganization
    urn:ngsi-ld:organization:VATES-B60645900
    Cif de la empresa vendrá con el acces token
    No tiene seguridad
        

    devolver claims


 /issuance/notifications

     


llamada  ### /protected/oid/preauth-code

    Pasar estos campos
    "profile": string,
    "vc_types": [string], 
    "subject_id": string,


Obtener QR Credential Offer /oid/credential-offer
    "response_mode":   (depende del portal, principio QR)     enum[qr, content, deep-link, redirect], // si queremos un QR, el contenido del QR, el contenido en si, etc.
	"profile": string,
	"vc_type?": [string],
	-"scope?":  no pasar
	"preauth_code?": string, // Debe validar el código registrado


Cuando este la credencia podría llamar
    Recuperar credencial /protected/credentials/{id}

    Guardar datos y credenciales



Resumen:

En los endpoints del third party hay 2 campos nuevos que hemos metido para compatibilidad futura, que son app y instance. Si quiers puedes ignorarlos o comprobar que coinciden con 2 variables de entorno o configuraciones que declares. app valdrá probablemente "oid", y instance si será un valor concreto que te tendría que confirmar. 

NO en /auth/requests
    la respuesta 200 cambia, se añade un campo authorized
    desaparece la respuesta 204
    no recuerdo si tu devolvías un 200 o un 204. En cualquier caso, ahora tienes que devolver un 200 poniendo authorized=true

cualquier error que quieras devolver (si los hay) puedes añadir un body con error y error_description

en /issuance/claims

    creo que antes se te pasaba vc_type, y ahora es vc_identifier. Simplemente un cambio de nombre
    en la respuesta antes había claims y pasa a llamarse subject_claims. Aparece additional_claims y context_claims (antes solo context) No los necesitas

todos los endpoints de conector pasan a tener versionado y un elemento nuevo en el  path llamado {endpoint}. Si el valor "instance" del primer punto lo guardaste, lo puedes usar para ponerlo aquí, son valores equivalentes pero con nombres distintos por el contexto. 

Revisa por si ves algún otro cambio que no recuerdo, y si tienes  alguna duda hablamos


/credentials/[organization_identify]


La organización viene en el token
puede que en un campo con nombre "organization_identify"

[organization_identify] es opcional, si no está se devuelven todos y tiene permisos para todas, o solo para aquellas, comporbar en el token

en token y param es la misma organizacion => devolver

en token y param es diferente organizacion => se debe de comprobar que tiene permisos para esa organización, pero pendiente de poder comprobar, la información vendría en el mismo token, pero no se sabe que formato, o incluso roles como admin
