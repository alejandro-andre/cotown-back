# CONTRATO DE ARRENDAMIENTO DE TEMPORADA DE INMUEBLE.



En Barcelona, a {{Today_day}} de {{Today_month|month}} de {{Today_year}}



## LAS PARTES

{%if Owner_id_type=='CIF'%}
De una parte, {%for s in Owner_signers%}{%-if loop.index>1%} y {%endif%}{{s.Owner_signer_name}}, mayor de edad, provisto de {{s.Owner_signer_id_type}} {{s.Owner_signer_id}}{%endfor%}, con domicilio profesional en {{Owner_address}}, {{Owner_zip}} {{Owner_city}}, actuando en nombre y representación de {{Owner_name}} con el mismo domicilio, {{Owner_id_type}} {{Owner_id}}{%if Owner_signers|length>1%}, en calidad de apoderados mancomunados{%endif%}.
{%else%}
De una parte, {{Owner_name}}, mayor de edad, con {{Owner_id_type}} núm. {{Owner_id}}, con domicilio profesional en {{Owner_address}}, {{Owner_zip}} {{Owner_city}} actuando en su nombre y representación.
{%endif%}

En adelante "**Arrendadora**".

{%if Customer_type=='empresa'%}
De otra parte, {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_signer_name}}, mayor de edad, con {{Customer_signer_id_type}} {{Customer_signer_id}}, con domicilio profesional en {{Customer_address}} {{Customer_zip}} {{Customer_city}}, {{Customer_province}}, {{Customer_country}}, actuando en nombre y representacion de {{Customer_name}} con el mismo domicilio, {{Customer_id_type}} {{Customer_id}}.
{%elif Customer_birth_date|age >= 18%}
De otra parte, {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_name}}, mayor de edad{%if Customer_nationality!=null%}, de nacionalidad {{Customer_nationality}}{%endif%}, con {{Customer_id_type}} núm. {{Customer_id}}, con domicilio habitual y permanente en {{Customer_address}} {{Customer_zip}} {{Customer_city}}, {{Customer_province}}, {{Customer_country}}, actuando en su nombre y representación.
{%else%}
De otra parte, {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_name}}, menor de edad{%if Customer_nationality!=null%}, de nacionalidad {{Customer_nationality}}{%endif%}, con {{Customer_id_type}} núm. {{Customer_id}}, con domicilio habitual y permanente en {{Customer_address}} {{Customer_zip}} {{Customer_city}}, {{Customer_province}}, {{Customer_country}}, actuando en su nombre y representación en virtud de autorización paterna/materna/tutor legal o con la comparecencia paterna/materna/tutor legal.
{%endif%}

En adelante denominada la "**Arrendataria**"



## MANIFIESTAN:  
 
I.- Que el arrendador es propietario del inmueble ubicado en {{Resource_building_address}} {{Resource_flat_address}}, que se encuentra totalmente amueblado y equipado con los utensilios domésticos. 

II.- Que el arrendatario está interesado en arrendar el inmueble antes descrito para la temporada que luego se dirá, por motivos de {{Customer_reason}} en {{Customer_school}}.
 
III.- AMBAS PARTES se reconocen suficiente capacidad legal para llevar a cabo este contrato, INTERVINIENDO en nombre y derecho mencionados respectivamente, y convienen formalizar el presente CONTRATO DE ARRENDAMIENTO DE TEMPORADA, con arreglo a los siguientes



## ESTIPULACIONES: 
 
## PRIMERA.- OBJETO. 

El arrendador arrienda a {{Customer_name}} el inmueble descrito en el expositivo primero de este contrato, para ser destinado a constituir su residencia temporal por motivo de estudios y por el tiempo que después se dirá. El inmueble que se arrienda en virtud del presente contrato no tendrá en ningún caso la condición de residencia permanente del arrendatario ni de cualesquiera terceros, salvo autorización expresa del arrendador. Asimismo, las partes convienen que el inmueble no podrá ser destinado al uso como alojamiento turístico o análogo (incluyendo de manera no exhaustiva las siguientes modalidades de alojamiento turístico: apartamentos turísticos y viviendas de uso turístico). 
 
La parte arrendataria no podrá modificar el destino mencionado sin el previo consentimiento por escrito del arrendador. El incumplimiento de este precepto será motivo de resolución del contrato. 
 
## SEGUNDA.- ESTADO Y REGLAS DE USO. 

La parte arrendataria declara recibir las llaves del inmueble y reconoce su buen estado de conservación y se compromete a devolverlo en el mismo estado a la conclusión de la relación contractual. 
 
En caso de pérdida o extravío de las llaves durante el contrato, la parte arrendataria podrá pedir otra llave en las oficinas de la propiedad y por ello se le cobrará el importe de 50 euros. 
 
Todos los elementos generales de la vivienda estarán siempre en condiciones de habitabilidad.  
 
A partir de las 22 horas queda totalmente prohibido hacer cualquier tipo de ruido que pueda molestar a los vecinos y se respetará tanto el descanso como el estudio de terceros. Si se producen este tipo de incidentes, así como si se altera la buena convivencia en el inmueble o edificio, o se realizan desordenes, desperfectos o se consume y se posee sustancias estupefacientes o ilegales, ello será considerado como motivo de resolución del contrato, pues la propiedad se reserva siempre el derecho de admisión. 
 
## TERCERA.- SERVICIOS QUE PRESTA LA ARRENDADORA: 
 
- Alojamiento en el inmueble. 

- Mantenimiento del piso para un buen funcionamiento y de los elementos comunes del edificio. 

- Todos los suministros de Agua, Gas, Electricidad e Internet (siendo exclusivamente responsable el arrendatario del legítimo uso de internet, asumiendo el arrendatario que de recibir la propiedad aviso de las autoridades sobre el mal uso del mismo, se interrumpiría inmediatamente aquel y se facilitaría a las autoridades los datos personales que se le soliciten de los autores de ese indebido uso).  
 
## CUARTA.- DURACIÓN. 

El arrendamiento se pacta por temporada y tiempo determinado empezando este el día {{Booking_date_from_day}}/{{Booking_date_from_month}}/{{Booking_date_from_year}} y finalizando el día {{Booking_date_to_day}}/{{Booking_date_to_month}}/{{Booking_date_to_year}}.

A las 10 horas de la mañana del último día se tendrá que dejar libre el inmueble y entregar las llaves del mismo sin que sea necesario requerimiento previo.
 
Si el arrendatario continúa ocupando el inmueble una vez pasado el vencimiento del contrato, éste tendrá que satisfacer en concepto de ocupación la cantidad de 30 euros por cada día que el usuario se exceda en la estancia. Además, y por ocupar el inmueble sin autorización del arrendador, deberá satisfacer en concepto de indemnización de daños y perjuicios la cantidad de 40 euros/día por cada uno que el usuario se exceda en su estancia de lo convenido, que serán descontados del importe del depósito entregado inicialmente.  
 
## QUINTA.- RENTA. 

La parte arrendataria abonará al gestor del arrendador Cotown Sharing Life, SL, en concepto de renta, la cantidad de {{Booking_rent|decimal}} euros, dentro de los cinco primeros días de cada mes, mediante domiciliación bancaria o tarjeta bancaria. Además, la parte arrendataria abonará {{Booking_final_cleaning|decimal}} euros de limpieza de salida, dentro de los cinco primeros días del último mes de su estancia, mediante domiciliación bancaria o tarjeta bancaria.

En el recibo que atenderá el arrendatario se incluyen también los gastos de comunidad (limpieza de zonas comunes de la escalera) y los suministros (Luz, Agua, Gas, e Internet) con un límite máximo, estos últimos, de {{Booking_limit|decimal}} euros mensuales, de tal suerte que lo que exceda de esa cantidad le será facturado al arrendatario aparte del recibo. 
 
El incumplimiento de la obligación de pago de ese recibo en el periodo fijado será motivo de resolución del contrato, dando derecho al arrendador a solicitar el desahucio, siendo por cuenta del arrendatario los gastos que estas acciones originen. Los recibos emitidos se abonarán íntegramente sea cual sea el tiempo en que se utilicen los servicios de alojamiento. 
 
## SEXTA.- REPARACIONES.

Respecto a los desperfectos que se originen en el inmueble, su coste irá a cargo del arrendatario. Las facturas de reparaciones de dispositivos del inmueble (caldera, sistemas de calefacción, electrodomésticos en general) provocadas por un mal uso o por un deficiente mantenimiento por parte de los residentes, se repercutirán al arrendatario. 
 
El arrendatario es responsable, no sólo de sus propios actos, sino también de los de aquellos a los que invite al piso, si bien esas personas no están autorizadas a pernoctar en la vivienda, siendo ello causa de resolución y de una posible indemnización de daños y perjuicios. 
 
## SEPTIMA.- RESPONSABILIDADES.

La propiedad no se hace responsable de los objetos robados y/o extraviados en el inmueble y se prohíbe expresamente la tenencia de cualquier tipo de animal doméstico en la vivienda. 
 
## OCTAVA.- GARANTÍA.

El arrendatario entrega a la arrendadora en el transcurso de este acto el importe de {{Booking_deposit}} euros (un mes) en concepto de garantía, suma que tendrá como finalidad cubrir los pagos de las obligaciones derivadas de este contrato que el arrendatario asume a favor del arrendador y en su caso responder de los desperfectos que el arrendatario pueda causar en el piso donde contratado, incluidas la perdida de las llaves o excesos de consumos no satisfechos durante la estancia.
 
Se hace constar expresamente, y así se acepta al suscribirse el presente contrato, que si se produce una baja voluntaria el arrendatario no tendrá derecho a la devolución del importe de la garantía excepto en el caso de haber dado éste un preaviso por escrito a la propiedad con al menos dos meses de antelación a la fecha prevista de la baja, en ese caso sólo se descontarán de la fianza 230 euros en concepto de penalización más la diferencia de tarifa si se le hubiera aplicado por la duración de la estancia. 
 
La baja involuntaria del arrendatario en cualquier momento de la estancia, incluida la expulsión, o la denegación de visado, entre otros motivos nunca dará derecho a la devolución del importe de la garantía. 
 
En el caso de que la garantía no cubra el total de las mensualidades pendientes y el importe de los daños causados, el arrendador tiene el derecho de exigir al arrendatario el pago de las mensualidades y de los daños que no han sido cubiertos con el importe de la garantía. 
 
## NOVENA.- CESIÓN Y SUBARRIENDO.

El arrendatario se obliga a no subarrendar, ni ceder o traspasar el inmueble arrendado sin el consentimiento expreso y escrito del arrendador. El incumplimiento de esta cláusula será causa de resolución del contrato. 
 
## DÉCIMA.- OBRAS.

El arrendatario no podrá realizar ningún tipo de obra o modificación en el inmueble o edificio al que pertenece sin el consentimiento expreso de la parte arrendadora. 
 
A pesar de no tener la consideración de obra, se prohíbe expresamente al arrendatario la realización de agujeros o perforaciones en las paredes del inmueble, descontándose de la fianza el importe que sea necesario para que las paredes recuperen su estado original en su caso en caso de incumplimiento. 
 
## DÉCIMO PRIMERA.- INCUMPLIMIENTO DE OBLIGACIONES.

El incumplimiento por cualquiera de las partes de las obligaciones resultantes del contrato dará derecho a la parte que hubiere cumplido las suyas a exigir el cumplimiento de la obligación y/o a promover la resolución del contrato de acuerdo con lo dispuesto en el artículo 1.124 del Código Civil. 
 
Además de lo ya dicho, el arrendador podrá resolver de pleno derecho el contrato por las siguientes causas: a) La falta de pago de la renta o, en su caso, de cualquiera de las cantidades cuyo pago haya asumido o corresponda al arrendatario, como los consumos b) La falta de pago del importe de la fianza c) La realización de daños causados dolosamente en la finca o de obras no consentidas por el arrendador. d) Cuando en el inmueble tengan lugar actividades molestas, insalubres, nocivas, peligrosas o ilícitas. e) Además se considerará incumplimiento todo aquello que el arrendatario haga en contra de lo dispuesto por la Comunidad de Propietarios del edificio en donde se encuentra la vivienda arrendada, así como contraviniendo todo lo que haya convenido para la limpieza y conservación del inmueble arrendado, incluso con terceras personas o entidades. f) el destino de la vivienda a un uso distinto del expresamente previsto en este contrato sin la previa autorización expresa del arrendador.  
 
Asimismo, en caso de resolución del contrato por la causa prevista en el punto f) anterior, el arrendador podrá exigir al arrendatario indemnización por la suma equivalente al total de las sanciones y la cuantía de cualesquiera otros perjuicios que le fueran causados por el destino de la habitación arrendada o de la vivienda en la que se encuentra a un uso distinto del expresamente previsto en este contrato, incluyendo, en su caso, las consecuencias jurídicas o económicas que pudieran resultar de la incoación de procedimientos sancionadores por incumplimiento de la normativa turística o sobre actividades. 
 
## DÉCIMO SEGUNDA.- CESIÓN DE DATOS.

La parte arrendataria autoriza a la arrendadora para que pueda ceder los datos personales que constan en este contrato a terceras entidades o personas jurídicas para que oferten al arrendatario servicios realizados con la finca y que pueda recabar de las mismas la información relativa al cumplimiento o incumplimiento de lo que al arrendatario corresponda para el adecuado mantenimiento de la finca arrendada y que pueda afectar a los demás ocupantes del inmueble. 

A los efectos de dar cumplimiento a lo prevenido en la LO 3/2018, de 5 de diciembre, de Protección de Datos de Carácter personal, le informamos que:

Cotown Sharing Life, S.L., con el domicilio en c/Beethoven 15, 7ª planta (Barcelona) es la responsable del tratamiento de los datos personales, y que estos serán conservados durante el plazo necesario para cumplir con la finalidad para la cual fueron recabados. En la dirección de correo electrónico hola@cotown.com puede ejercer sus derechos de acceso, rectificación, supresión, oposición, portabilidad, limitación del tratamiento y en su caso retirar el consentimiento. Asimismo, tiene derecho a interponer una reclamación ante la correspondiente Autoridad de Control.

## DÉCIMO TERCERA.- SUMISIÓN.

Los contratantes se someten expresamente a los Juzgados y Tribunales de la ciudad en la que se encuentra ubicado el inmueble, para todas aquellas cuestiones litigiosas que pudieran derivarse del mismo. 
 
## DÉCIMO QUINTA- LEY APLICABLE.

El arrendatario no tendrá derecho a indemnización de clase alguna a la extinción del contrato.

La arrendataria renuncia expresamente al derecho de adquisición preferente, tanteo y retracto para el supuesto de la transmisión de la vivienda arrendada por cualquier título. 

Este contrato se rige por las disposiciones contenidas en el código civil, artículos 1546 y siguientes, para el arrendamiento de cosas, excluyéndose expresamente las previsiones contenidas en la LAU. 

Y con el carácter expresado en la intervención, firman el presente contrato por duplicado, en cuatro folios escritos por el anverso numeradas sus caras del uno al cuatro, en el lugar y fecha indicados. 
 
| | |
|:-|:-|
|**El Arrendador**|**El Arrendatario**|
{%-for s in Owner_signers-%}
| | |
|![firma]({{Server}}/signature/{{s.Owner_signer}})| |
|Fdo: {{s.Owner_signer_name}}|{%if loop.index==1%}Fdo: {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_name}}{%endif%}|
{%-endfor-%}