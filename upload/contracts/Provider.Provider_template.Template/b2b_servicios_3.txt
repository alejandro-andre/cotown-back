# CONTRATO DE SERVICIOS



En Barcelona, a {{Today_day}} de {{Today_month|month}} de {{Today_year}}


## REUNIDOS

De una parte,

{%if Rooms[0].Owner_id_type=='CIF'%}
De una parte, {%for s in Rooms[0].Owner_signers%}{%-if loop.index>1%} y {%endif%}{{s.Owner_signer_name}}, mayor de edad, provisto de {{s.Owner_signer_id_type}} {{s.Owner_signer_id}}{%endfor%}, con domicilio profesional en {{Rooms[0].Owner_address}}, {{Rooms[0].Owner_zip}} {{Rooms[0].Owner_city}}, actuando en nombre y representación de {{Rooms[0].Owner_name}} con el mismo domicilio, {{Rooms[0].Owner_id_type}} {{Owner_id}}{%if Owner_signers|length>1%}, en calidad de apoderados mancomunados{%endif%}.
{%else%}
De una parte, {{Rooms[0].Owner_name}}, mayor de edad, con {{Rooms[0].Owner_id_type}} núm. {{Rooms[0].Owner_id}}, con domicilio profesional en {{Rooms[0].Owner_address}}, {{Rooms[0].Owner_zip}} {{Rooms[0].Owner_city}} actuando en su nombre y representación.
{%endif%}

En adelante "ATLAS".

Y de otra parte,

{%if Customer_type=='empresa'%}
De otra parte, {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_signer_name}}, mayor de edad, con {{Customer_signer_id_type}} {{Customer_signer_id}}, con domicilio profesional en {{Customer_address}} {{Customer_zip}} {{Customer_city}}, {{Customer_province}}, {{Customer_country}}, actuando en nombre y representacion de {{Customer_name}} con el mismo domicilio, {{Customer_id_type}} {{Customer_id}}.
{%elif Customer_birth_date|age >= 18%}
De otra parte, {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_name}}, mayor de edad{%if Customer_nationality!=null%}, de nacionalidad {{Customer_nationality}}{%endif%}, con {{Customer_id_type}} núm. {{Customer_id}}, con domicilio habitual y permanente en {{Customer_address}} {{Customer_zip}} {{Customer_city}}, {{Customer_province}}, {{Customer_country}}, actuando en su nombre y representación.
{%else%}
De otra parte, {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_name}}, menor de edad{%if Customer_nationality!=null%}, de nacionalidad {{Customer_nationality}}{%endif%}, con {{Customer_id_type}} núm. {{Customer_id}}, con domicilio habitual y permanente en {{Customer_address}} {{Customer_zip}} {{Customer_city}}, {{Customer_province}}, {{Customer_country}}, actuando en su nombre y representación en virtud de autorización paterna/materna/tutor legal o con la comparecencia paterna/materna/tutor legal.
{%endif%}

En adelante el "**Arrendatario**"

Ambas partes se reconocen la capacidad legal necesaria para este acto, y de común acuerdo.


## EXPONEN

I. Que la propiedad de la finca sita en #### la ha arrendado a #### por plazo que vence el #### para destinarla a vivienda de algunos de sus estudiantes, interesando a la arrendataria que ATLAS se ocupe de la gestión del arrendamiento a dichos estudiantes, facilitando el acceso de éstos a la finca, prestando determinados servicios y atendiendo las posibles incidencias que puedan originarse en relación al arrendamiento y/o los servicios que puedan haberse contratado.

II.- #### está interesada en contratar el servicio prestado por ATLAS que a continuación se indicará y sometiéndose a los siguientes


## PACTOS

### Primero.- Objeto del contrato.

ATLAS prestará a los estudiantes de #### que residan en la vivienda indicada en el antecedente I los siguientes servicios: 

- Las zonas comunes serán limpiadas una vez cada quince (15) días.

- Personal de contacto con disposición 24h/día, en el teléfono: 680412059, y capacidad para intervenir a los efectos de atender los servicios convenidos e incidencias relacionadas con la finca que acaezcan.

- ATLAS se compromete a atender las anomalías de mantenimiento dentro de las 24 horas de haber sido requeridas a menos que sea una urgencia que deba atenderse inmediatamente.

- Limpieza final exhaustiva con desinfección de habitaciones

- ATLAS proveerá de un pack de sábanas y toallas por cada estudiante, y se entregará a la llegada.

Estos servicios podrán ser prestados directamente por ATLAS o por cualquier otra persona jurídica o natural que aquélla designe.

### Segundo.- Precio del servicio.

El precio de los servicios convenidos en el presente y prestados por ATLAS es de #### € mensuales, más la preceptiva cuota de IVA, a cargo de #### a pagar dentro de los cinco primeros días de cada mes, en la siguiente cuenta bancaria titularidad de ATLAS ES67 2038 9261 9360 0037 0962 

Se cobrará a #### , #### € más la preceptiva cuota de IVA en concepto de limpieza final.
         
### Tercero.- Duración.

La duración del presente acuerdo constituye el período de tiempo comprendido entre el #### y el ####.

### Cuarto.- Sumisión judicial.

Para cualquier diferencia en la interpretación y ejecución del presente contrato, las partes se someten a los Juzgados y Tribunales de la ciudad de Barcelona, con renuncia a su fuero propio, si existiere.

Y en prueba de conformidad con el contenido de todas y cada una de las presentes cláusulas, las partes concurrentes firman el presente contrato, por duplicado y a todos los efectos, en la ciudad y fecha arriba indicadas.



| | |
|:-|:-|
|**ATLAS**|**El Arrendatario**|
{%-for s in Owner_signers-%}
| | |
|![firma]({{Server}}/signature/{{s.Owner_signer}})| |
|Fdo: {{s.Owner_signer_name}}|{%if loop.index==1%}Fdo: {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_name}}{%endif%}|
{%-endfor-%}