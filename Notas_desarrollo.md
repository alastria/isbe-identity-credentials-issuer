
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