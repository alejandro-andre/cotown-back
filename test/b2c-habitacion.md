# CONTRATO DE ...


En Barcelona, a {{Today_day}} de {{Today_month|month}} de {{Today_year}}


# REUNIDOS

De una parte, {%for s in Owner_signers%}{%-if loop.index>1%} y {%endif%}{{s.Owner_signer_name}}, mayor de edad, provisto de {{s.Owner_signer_id_type}} {{s.Owner_signer_id}}{%endfor%}, con domicilio profesional en {{Owner_address}}, {{Owner_zip}} {{Owner_city}}, actuando en nombre y representación de {{Owner_name}} con el mismo domicilio, {{Owner_id_type}} n.º {{Owner_id}}{%if Owner_signers|length>1%}, en calidad de apoderados mancomunados{%endif%}.

En adelante el "**Arrendador**" o la "**Propiedad**".

{%if Customer_type=='empresa'%}
Sr./Sra. {{Customer_signer_name}}, mayor de edad, con {{Customer_signer_id_type}} núm. {{Customer_signer_id}}, con domicilio profesional en {{Customer_address}} {{Customer_zip}} {{Customer_city}}, {{Customer_province}}, {{Customer_country}}, actuando en nombre y representacion de {{Customer_name}} con el mismo domicilio, {{Customer_id_type}} n.º {{Customer_id}}.
{%elif Customer_tutor_id==''%}
Sr./Sra. {{Customer_name}}, mayor de edad{%if Customer_nationality!=null%}, de nacionalidad {{Customer_nationality}}{%endif%}, con {{Customer_id_type}} núm. {{Customer_id}}, con domicilio habitual y permanente en {{Customer_address}} {{Customer_zip}} {{Customer_city}}, {{Customer_province}}, {{Customer_country}}, actuando en su nombre y representación.
{%else%}
Sr./Sra. {{Customer_name}}, menor de edad{%if Customer_nationality!=null%}, de nacionalidad {{Customer_nationality}}{%endif%}, con {{Customer_id_type}} núm. {{Customer_id}}, con domicilio habitual y permanente en {{Customer_address}} {{Customer_zip}} {{Customer_city}}, {{Customer_province}}, {{Customer_country}}, actuando en su nombre y representación en virtud de autorización paterna/materna/tutor legal o con la comparecencia paterna/materna/tutor legal.
{%endif%}

En adelante denominada la “**Arrendataria**”

# MANIFIESTAN (EJEMPLO)

I.- Que la sociedad {{Owner_name}} es la propietaria del inmueble ubicado en {{Resource_building_address}} {{Resource_flat_address}} de {{Resource_building_city}} y ejerce en él la actividad de arrendar partes indivisas de la finca por temporada a estudiantes y jóvenes profesionales durante su estancia académica o laboral. Que la vivienda se encuentra totalmente amueblada y equipado con los utensilios domésticos. 

II.- Que el objeto del presente arrendamiento es una parte indivisa de la vivienda, que se encuentra amueblada y equipada. 

III.- Que el arrendatario, desea arrendar una parte indivisa de la finca por motivos de {{Booking_reason}} en {{School}} y consecuentemente, AMBAS PARTES se reconocen suficiente capacidad legal para llevar a cabo este contrato, INTERVINIENDO en nombre y derecho mencionados respectivamente, siendo responsables de la veracidad de sus manifestaciones y que se regirá por las siguientes:

# ESTIPULACIONES (EJEMPLO)

## PRIMERA.- DESTINO. 

El objeto del presente contrato consiste en la cesión del uso de {{Resource_part|part}} indivisa de la finca, que le concede el derecho de uso exclusivo de la habitación reservada, con derecho además, al uso de los servicios comunes y suministros (agua, gas, electricidad e internet), y ello para ser ocupada como vivienda.

La parte arrendataria no podrá modificar el destino mencionado sin el previo consentimiento por escrito del arrendador. El incumplimiento de este precepto será motivo de resolución del contrato. 

## SEGUNDA.- ESTADO Y REGLAS DE USO. 

La parte arrendataria declara recibir las llaves del piso y reconoce su buen estado de conservación y se compromete a devolverlo en el mismo estado a la conclusión de la relación contractual. 

En caso de pérdida o extravío de las llaves durante el contrato el arrendatario podrá pedir otra llave en las oficinas de la propiedad y por ello se le cobrará el importe de 50 euros (IVA incluido)

Los elementos generales de la vivienda y habitaciones estarán siempre en condiciones de habitabilidad.  

A partir de las 22 horas queda totalmente prohibido hacer cualquier tipo de ruido que pueda molestar a los vecinos y se respetará tanto el descanso como el estudio de los otros estudiantes que habiten en el inmueble. Si se producen este tipo de incidentes, así como si se altera la buena convivencia en el uso del piso, o se realizan en el piso, desordenes, desperfectos o se consume y se posee sustancias estupefacientes o ilegales, ello será considerado como motivo de resolución del contrato pues la propiedad se reserva siempre el derecho de admisión. 

## TERCERA.- SERVICIOS QUE PRESTA LA ARRENDADORA: 

- Alojamiento en la vivienda especificada 

- Mantenimiento de la vivienda y de los elementos comunes del edificio para un buen funcionamiento.

- Todos los suministros de Agua, Gas, Electricidad e Internet (siendo exclusivamente responsable el arrendatario del legítimo uso de internet, asumiendo el arrendatario que de recibir la propiedad aviso de las autoridades sobre el mal uso del mismo, se interrumpiría inmediatamente aquel y se facilitaría a las autoridades los datos personales que se le soliciten de los autores de ese indebido uso).  

## CUARTA.- DURACIÓN. 

El arrendamiento se pacta por temporada y tiempo determinado empezando el día {{Booking_date_from}} y finalizando el día {{Booking_date_to}} por estar matriculado o trabajando en {{School}}.

La duración del subarrendamiento comporta que de conformidad a lo convenido en el art. 3.2 de la Ley de Arrendamientos Urbanos, la naturaleza jurídica de este contrato sea para uso distinto del de vivienda.

A las 10 horas de la mañana del último día se tendrá que dejar libre la vivienda y entregar las llaves del piso sin que sea necesario requerimiento previo.  

Si el arrendatario continúa ocupando la finca una vez pasado el vencimiento del contrato, éste tendrá que satisfacer en concepto de ocupación la cantidad de 40 euros por cada día que el arrendatario se exceda en la estancia, en concepto de indemnización de daños y perjuicios, facultando a la arrendadora para, en su caso, descontarlos del importe del depósito entregado inicialmente.  

## QUINTA.- RENTA. 

La parte arrendataria abonará al gestor del  arrendador 3K Coliving & Accommodation SLcotown sharing life, s.l. en concepto de renta, la cantidad de {{Booking_rent+Booking_services}} euros, dentro de los cinco primeros días de cada mes, mediante tarjeta bancaria o bien mediante domiciliación bancaria en caso de disponer de una cuenta bancaria española. 

En el recibo que atenderá el arrendatario se incluyen también los gastos de comunidad (limpieza de zonas comunes de la escalera, así como el Servicio de Portería si lo hubiera), internet y suministros (Luz, Agua, Gas) con un límite máximo, estos últimos, de {{Booking_limit}} euros mensuales, de tal suerte que lo que exceda de esa cantidad le será facturado al arrendatario aparte del recibo.

El incumplimiento de la obligación de pago de ese recibo en el periodo fijado será motivo de resolución del contrato, dando derecho al arrendador a solicitar el desahucio, siendo por cuenta del arrendatario los gastos que estas acciones originen. Los recibos emitidos se abonarán íntegramente sea cual sea el tiempo en que se utilicen los servicios de alojamiento.  

## SEXTA.- REPARACIONES 

Respecto a los desperfectos que se originen dentro de las dependencias del piso, su coste irá a cargo del causante. En caso de desconocer el responsable, este importe se repartirá entre todos los ocupantes del piso. Las facturas de reparaciones de dispositivos del piso arrendado (caldera, sistemas de calefacción, electrodomésticos en general) provocadas por un mal uso o por un deficiente mantenimiento por parte de los residentes, se repercutirán al causante directo del mismo o, en caso en que no se pueda individualizar, se repercutirá a todos los residentes del piso de forma proporcional.  

El arrendatario es responsable, no sólo de sus propios actos, sino también de los de aquellos a los que invite al piso, si bien esas personas no están autorizadas a pernoctar en la habitación cuyo uso exclusivo se atribuye al arrendatario ni en la vivienda, siendo ello causa de resolución y de una posible indemnización de daños y perjuicios.  

## SEPTIMA.- RESPONSABILIDADES.

La propiedad no se hace responsable de los objetos robados y/o extraviados en la  y vivienda y se prohíbe expresamente la tenencia de cualquier tipo de animal en la vivienda.  

## OCTAVA.- FIANZA GARANTÍA 

El arrendatario entrega a la empresa en el transcurso de este acto el importe de {{Booking_deposit}} euros en concepto de fianza garantía, suma que tendrá como finalidad cubrir los pagos de las obligaciones derivadas de este contrato que el arrendatario asume a favor del arrendador y en su caso responder de los desperfectos que el arrendatario pueda causar en el piso contratado, incluidas la perdida de las llaves o excesos de consumo no satisfechos durante la estancia

La fianza garantía no sustituirá en ningún caso al pago de la última mensualidad, pudiendo ésta ser incautada en su totalidad en caso de impago de la última renta.

Se hace constar expresamente, y así se acepta al suscribirse el presente contrato, que si se produce una baja voluntaria el arrendatario no tendrá derecho a la devolución del importe de la fianza garantía excepto en el caso de haber dado éste un preaviso por escrito a la propiedad con al menos dos meses de antelación a la fecha prevista de la baja, en ese caso sólo se descontarán de la fianza 230 euros en concepto de penalización.

La baja involuntaria del arrendatario en cualquier momento del curso estudiantil, incluida la expulsión, o la denegación de visado, entre otros motivos nunca dará derecho a la devolución del importe de la fianza garantía .

En el caso de que la fianza garantía no cubra el total de las mensualidades pendientes y el importe de los daños causados, la empresa tiene el derecho de exigir al arrendatario el pago de las mensualidades y de los daños que no han sido cubiertos con el importe de la fianzagarantía.  

## NOVENA.- CESIÓN Y SUBARRIENDO. 

El arrendatario se obliga a no subarrendar, ni ceder o traspasar la parte indivisa de la vivienda arrendada sin el consentimiento expreso y escrito del arrendador. El incumplimiento de esta cláusula será causa de resolución del contrato. 

## DÉCIMA.- SUBSTITUCIÓN DE INMUEBLE. 

En el caso de que el inmueble sobre el que versa este arrendamiento esté co-arrendado/co-ocupado por menos del 50% de su capacidad, y a los efectos de conservar el espíritu del presente contrato, que es el de compartir vivienda diversas personas, la arrendadora queda facultada para substituir el inmueble arrendado por otro inmueble que se encuentre en similares o superiores condiciones, entendiendo que el criterio de determinación de dicho concepto de igualdad o superioridad vendrá determinado por la superficie de la habitación cuyo uso exclusivo se adjudica a la arrendataria. En cualquier caso, el inmueble se hallará en el mismo barrio. Y para la aplicación de dicho cambio, la arrendadora vendrá obligada a comunicarlo a la arrendataria con diez días de antelación al traslado, corriendo la arrendadora con el coste del mismo y con la previa exhibición del inmueble al arrendatario. Esta facultad podrá ejercitarse por la arrendadora una sola vez durante la vigencia del contrato, salvo acuerdo con la parte arrendataria. En el supuesto de que, exhibida la vivienda de substitución, no resultare del agrado a la parte arrendataria, ésta podrá resolver el arrendamiento, sin penalización para ninguna de las partes, antes de la fecha prevista para el traslado. 

## DÉCIMO PRIMERA.- OBRAS. 

El arrendatario no podrá realizar ningún tipo de obra o modificación en el inmueble o edificio al que pertenece sin el consentimiento expreso de la parte arrendadora. 

A pesar de no tener la consideración de obra, se prohíbe expresamente al arrendatario la realización de agujeros o perforaciones en las paredes del inmueble, descontándose de la fianza garantía el importe que sea necesario para que las paredes recuperen su estado original en su caso en caso de incumplimiento. 

## DÉCIMO SEGUNDA.- INCUMPLIMIENTO DE OBLIGACIONES. 

El incumplimiento por cualquiera de las partes de las obligaciones resultantes del contrato dará derecho a la parte que hubiere cumplido las suyas a exigir el cumplimiento de la obligación y/o a promover la resolución del contrato de acuerdo con lo dispuesto en el artículo 1.124 del Código Civil. 

Además de lo ya dicho, el arrendador podrá resolver de pleno derecho el contrato e instar el desahucio de la  arrendadataria por las siguientes causas:

a) La falta de pago de la renta o, en su caso, de cualquiera de las cantidades cuyo pago haya asumido o corresponda al arrendatario, como los consumos; 

b) La falta de pago del importe de la fianzagarantía; 

c) La realización de daños causados en la finca o de obras no consentidas por el arrendador; 

d) cuando en el inmueble tengan lugar actividades molestas, insalubres, nocivas, peligrosas o ilícitas; 

e) la realización de obras no consentidas por el arrendador; 

f) además se considerará incumplimiento todo aquello que el arrendatario haga en contra de lo dispuesto por la Comunidad de Propietarios del edificio en donde se encuentra la vivienda arrendada parcialmente;

g) al uso de su parte indivisa de vivienda distinto al previsto expresamente en este contrato sin la previa autorización del arrendador

## DÉCIMO TERCERA.- CESIÓN DE DATOS

La parte arrendataria autoriza a la arrendadora para que pueda ceder los datos personales que constan en este contrato a terceras entidades o personas jurídicas para que oferten al arrendatario servicios realizados con la finca y que pueda recabar de las mismas la información relativa al cumplimiento o incumplimiento de lo que al arrendatario corresponda para el adecuado mantenimiento de la finca arrendada y que pueda afectar a los demás ocupantes del inmueble.

A los efectos de dar cumplimiento a lo prevenido en la LO 3/2018, de 5 de diciembre, de Protección de Datos de Carácter personal, le informamos que:

3K Coliving & Accommodation SLCotown Sharing Life, S.L., con el domicilio en c/Beethoven 15, 7ª planta (Barcelona) es la responsable del tratamiento de los datos personales, y que estos serán conservados durante el plazo necesario para cumplir con la finalidad para la cual fueron recabados. En la dirección de correo electrónico info@3kcolivingcotown.com  puede ejercer sus derechos de acceso, rectificación, supresión, oposición, portabilidad, limitación del tratamiento y en su caso retirar el consentimiento. Asimismo, tiene derecho a interponer una reclamación ante la correspondiente Autoridad de Control.

## DÉCIMO CUARTA.- SUMISIÓN. 

Los contratantes se someten expresamente a los Juzgados y Tribunales de la ciudad en la que se encuentra ubicado el inmueble, para todas aquellas cuestiones litigiosas que pudieran derivarse del mismo. 

## DÉCIMO QUINTA- LEY APLICABLE

El arrendatario no tendrá derecho a indemnización de clase alguna a la extinción del contrato.

La arrendataria renuncia expresamente al derecho de adquisición preferente, tanteo y retracto para el supuesto de la transmisión de la vivienda arrendada por cualquier título. 

Este contrato se rige por las disposiciones contenidas en el código civil, artículos 1546 y siguientes, para el arrendamiento de cosas, excluyéndose expresamente las previsiones contenidas en la LAU. 

Y con el carácter expresado en la intervención, firman el presente contrato por duplicado, en cuatro folios escritos por el anverso numeradas sus caras del uno al cuatro, en el lugar y fecha indicados. 

|  |  |
|:-|:-|
|**El Arrendador**|**El Arrendatario**|
{%-for s in Owner_signers-%}
|&nbsp; | |
|&nbsp; | |
|&nbsp; | |
|&nbsp; | |
|&nbsp; | |
|Fdo: D./D. {{s.Owner_signer_name}}|{%if loop.index==1%}Fdo: {{Customer_name}}{%endif%}|
{%-endfor-%}