# CONTRATO DE ARRENDAMIENTO DE TEMPORADA DE INMUEBLE
<br><br>
En Barcelona, a {{Today_day}} de {{Today_month|month}} de {{Today_year}}
<br><br>
## LAS PARTES

{%if Owner_id_type=='CIF'%}
De una parte, {%for s in Owner_signers%}{%-if loop.index>1%} y {%endif%}{{s.Owner_signer_name}}, mayor de edad, provisto de {{s.Owner_signer_id_type}} {{s.Owner_signer_id}}{%endfor%}, con domicilio profesional en {{Owner_address}}, {{Owner_zip}} {{Owner_city}}, actuando en nombre y representación de {{Owner_name}} con el mismo domicilio, {{Owner_id_type}} {{Owner_id}}{%if Owner_signers|length>1%}, en calidad de apoderados mancomunados{%endif%}. La Arrendadora tiene designada para la gestión de este contrato de arrendamiento y uso de habitación y durante todo el plazo de duración a la compañía Cotown Sharing Life, S.L. (la "**Gestora**"), con domicilio profesional en Beethoven 15, 7ª planta, 08021 Barcelona, CIF B67551754, representado por Dª Azucena Esteban Calderon, mayor de edad, provisto de DNI 38148452P, con el mismo domicilio, actuando en nombre de la mencionada sociedad.
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

La Arrendadora y la Arrendataria serán referidas conjuntamente en adelante como las "**Partes**".

Las Partes acuerdan conjuntamente suscribir el presente contrato que se regirá por las siguientes condiciones particulares (las "**Condiciones Particulares**") y las condiciones generales (las "**Condiciones Generales**"):

## MANIFIESTAN

I. Que el Arrendador es propietario del inmueble ubicado en {{Resource_street}}, {{Resource_address}} que se encuentra totalmente amueblado y equipado con los utensilios domésticos (en adelante “la Vivienda”)

La Vivienda dispone de cédula de habitabilidad {{Resource_occupancy}}, de certificado de eficiencia energética {{Resource_energy}}, NRA {{Resource_registry}} y tiene una superficie de {{Resource_area}} m² construidos.

II. Que, el Arrendador tiene la consideración de gran tenedor con arreglo a la normativa vigente.

III. Que el arrendatario está interesado en arrendar el inmueble antes descrito para la temporada que luego se dirá, por motivos de {{Booking_reason|lower}}{% if Booking_reason_id in (1, 3) and Booking_school %} en {{Booking_other_school or Booking_school}}{% endif %}{% if Booking_reason_id in (2, 4) and Booking_company %} en {{Booking_company}}{% endif %}.

Se adjunta al presente la documentación acreditativa de la estancia, a efectos de justificar la necesidad de temporalidad.

IV. Ambas partes se reconocen suficiente capacidad legal para llevar a cabo este contrato, interviniendo en nombre y derecho mencionados respectivamente, y convienen formalizar el presente **Contrato de arrendamiento de temporada**.
<div style="page-break-after: always;"></div>
## ESTIPULACIONES: 
 
## PRIMERA. OBJETO. 

El arrendador arrienda a {{Customer_signer_name or Customer_name}} la Vivienda, para ser destinada a constituir su residencia temporal por motivos de {{Booking_reason|lower}}{% if Booking_reason_id in (1, 3) and Booking_school %} en {{Booking_other_school or Booking_school}}{% endif %}{% if Booking_reason_id in (2, 4) and Booking_company %} en {{Booking_company}}{% endif %} y por el tiempo que después se dirá. La Vivienda que se arrienda en virtud del presente contrato no tendrá en ningún caso la condición de residencia permanente del arrendatario, por tener el Arrendatario su residencia permanente en la dirección reseñada en el encabezamiento del presente contrato, ni de cualesquiera terceros, salvo autorización expresa del arrendador. Asimismo, las partes convienen que la Vivienda no podrá ser destinada al uso como alojamiento turístico o análogo (incluyendo de manera no exhaustiva las siguientes modalidades de alojamiento turístico: apartamentos turísticos y viviendas de uso turístico). 
 
La parte arrendataria no podrá modificar el destino mencionado sin el previo consentimiento por escrito del arrendador. El incumplimiento de este precepto será motivo de resolución del contrato.

## SEGUNDA. ESTADO Y REGLAS DE USO. 

La parte arrendataria declara recibir las llaves de la Vivienda y reconoce su buen estado de conservación y se compromete a devolverla en el mismo estado a la conclusión de la relación contractual. 
 
En caso de pérdida o extravío de las llaves durante el contrato, la parte arrendataria podrá pedir otra llave en las oficinas de la propiedad y por ello se le cobrará el importe de 120 euros. 
 
Todos los elementos generales de la Vivienda estarán siempre en condiciones de habitabilidad.  
 
A partir de las 22 horas queda totalmente prohibido hacer cualquier tipo de ruido que pueda molestar a los vecinos y se respetará tanto el descanso como el estudio de terceros. Si se producen este tipo de incidentes, así como si se altera la buena convivencia en el inmueble o edificio, o se realizan desordenes, desperfectos o se consume y se posee sustancias estupefacientes o ilegales, ello será considerado como motivo de resolución del contrato, pues la propiedad se reserva siempre el derecho de admisión. 

## TERCERA. SERVICIOS QUE PRESTA LA ARRENDADORA: 
 
- Alojamiento en el inmueble. 
- Mantenimiento del piso para un buen funcionamiento y de los elementos comunes del edificio. 
- Todos los suministros de Agua, Gas, Electricidad e Internet (siendo exclusivamente responsable el arrendatario del legítimo uso de internet, en caso de recibir aviso de las autoridades sobre el mal uso del mismo, la Arrendadora quedará facultada para interrumpir el servicio y facilitar a las autoridades correspondientes los datos personales que se le soliciten acerca de los responsables).

## CUARTA. SERVICIO DE LIMPIEZA ORDINARIA.

En aquellos contratos cuya duración sea superior a dos (2) meses, el arrendador incluirá como parte del presente contrato un servicio de limpieza del inmueble consistente en dos (2) horas de limpieza una vez al mes, durante toda la vigencia del arrendamiento.

Dicho servicio será prestado por personal designado por el arrendador o por una empresa externa contratada a tal efecto, en fecha y horario que se acordarán previamente con el arrendatario, procurando no interferir de manera injustificada en el uso y disfrute de la vivienda.

El servicio de limpieza tendrá carácter ordinario, limitándose a tareas generales de mantenimiento y limpieza del inmueble, y no incluirá limpiezas de carácter extraordinario, tales como limpiezas derivadas de un uso negligente, daños, obras, ni limpieza profunda al inicio o final del contrato, salvo pacto expreso en contrario.

El arrendatario se compromete a facilitar el acceso a la vivienda en las fechas acordadas para la correcta prestación del servicio.

## QUINTA. DURACIÓN. 

El arrendamiento se pacta por temporada y tiempo determinado empezando este el día {{Booking_date_from_day}}/{{Booking_date_from_month}}/{{Booking_date_from_year}} a fin de proceder a la reserva y bloqueo del inmueble, y finalizando el día {{Booking_date_to_day}}/{{Booking_date_to_month}}/{{Booking_date_to_year}}.

Coincidiendo con la firma de este contrato, la Arrendataria hará efectivo el pago del importe de la fianza legal y la garantía adicional.

A las 10:00 horas de la mañana del último día del Plazo del Contrato del Inmueble, la Arrendataria dejará libre y a disposición de la Arrendadora la Vivienda, sin necesidad de preaviso alguno, haciendo entrega de la Vivienda con el inventario, muebles y enseres en perfecto estado, así como de todos los juegos de llaves que le hubieran sido entregados a la Arrendataria.

Si el arrendatario continúa ocupando la Vivienda una vez transcurrida la fecha de vencimiento del Contrato, éste tendrá que satisfacer en concepto de ocupación la cantidad de 400 euros por cada día que el usuario se exceda en la estancia. Además, y por ocupar la Vivienda sin autorización del arrendador, deberá satisfacer en concepto de indemnización de daños y perjuicios la cantidad de 300 euros/día por cada uno que el usuario se exceda en su estancia de lo convenido, que podrán ser descontados del importe de la Garantía entregada inicialmente y hasta donde alcance y en caso de que se supere el importe de la Garantía, la Arrendataria deberá proceder con el abono de la diferencia hasta las penalizaciones efectivamente incurridas con carácter semanal.

## SEXTA. RENTA. 

Por el arrendamiento y uso del inmueble por la Arrendataria conforme al presente Contrato, la Arrendataria abonará obligatoriamente a la Arrendadora y durante todo el Plazo la cantidad de (la "**Renta**").

{% for rent in Prices %}
{%-if Owner_id == Service_id %}
- Mes {{rent.Rent_date_month}}/{{rent.Rent_date_year}}: {{(rent.Rent+rent.Services+(rent.Rent_discount or 0)+(rent.Services_discount or 0))|decimal(1)}} euros mensuales.
{%-else %}
- Mes {{rent.Rent_date_month}}/{{rent.Rent_date_year}}: {{(rent.Rent+(rent.Rent_discount or 0))|decimal(1)}} euros mensuales.
{%-endif %}
{%-endfor %}

La renta del presente contrato se ha establecido teniendo en cuenta lo siguiente:

a) Que el Arrendador tiene la condición de gran tenedor.

b) Que la Vivienda está situada en una zona de mercado residencial tensionado.

c) Que la Vivienda ha estado arrendada / no ha estado arrendada durante los últimos 5 años como vivienda habitual en virtud de un contrato sujeto a la Ley de Arrendamientos Urbanos.

d) Del mismo modo, el importe de la renta se ha establecido según lo previsto en el Artículo 17.6 y 7 de la Ley de Arrendamientos Urbanos y en virtud de lo dispuesto en la ley 18/2007 de Vivienda de Cataluña según la redacción dada por la ley 11/2025 de 29 de diciembre de medidas en materia de vivienda y urbanismo.

{% if Booking_type == 'recreativo' %}
Además, la parte arrendataria abonará {{Booking_final_cleaning|decimal(1)}} euros de limpieza de salida mediante domiciliación bancaria o tarjeta bancaria dentro de los cinco primeros días naturales contados a partir de la fecha de emisión de la factura.

{% elif Booking_limit_type == 'indice' %}
De conformidad con lo anterior, la determinación de la renta de la Vivienda se ha determinado tomando en consideración el índice de Referencia Estatal (se acompaña como anexo).

Los conceptos indicados a continuación no están incluidos en la renta y se facturarán como conceptos aparte de forma mensual:

- Gastos por suministros de los que esté dotada la Vivienda y hasta el límite de {{Booking_limit|decimal(1)}} euros por persona y mes
- IBI y Gastos de la comunidad de propietarios
- Tasa de recogida de basuras
- Conexión al servicio de internet

{% elif Booking_limit_type == 'lau' %}
De conformidad con lo expuesto, la determinación de la renta se ha efectuado tomando como referencia:

- la última renta del contrato de arrendamiento de vivienda habitual que permaneció vigente hasta {{Resource_last_LAU_date_day}}/{{Resource_last_LAU_date_month}}/{{Resource_last_LAU_date_year}}, cuyo importe ascendía a {{Resource_last_LAU_rent or 0|decimal(1)}} euros mensuales.

- el Índice de Referencia Estatal que se adjunta como anexo al presente.

Por ello, de conformidad con lo dispuesto en los Apartados 6 y 7 del Art. 17 de la LAU la renta del arrendamiento corresponde a la menor entre la última renta del contrato anterior actualizada y la resultante del Índice de Referencia Estatal.

Aplicada la actualización de la renta conforme al Índice de Precios al Consumo correspondiente, así como el incremento del 10% autorizado por la realización de obras de mejora en la Vivienda en los dos años anteriores, la renta resultante asciende a {{Booking_rent|decimal(1)}} euros mensuales.

El Arrendatario abonará también:

- Gastos por suministros de los que esté dotada la Vivienda y hasta el límite de {{Booking_limit|decimal(1)}} por persona y mes

{% if Booking_expenses %}
- IBI y gastos de comunidad {{Booking_expenses|decimal(1)}} euros mensuales.{% endif %}

{% else %}
De conformidad con lo anterior, la determinación de la renta se ha llevado a cabo tomando en consideración la consulta realizada en la página web del Ministerio de Vivienda y Agenda Urbana a efectos de determinar la existencia de Índice de Referencia (se acompaña informe como anexo a la consulta del que resulta que no existe precio de referencia a dichos efectos, por tratarse de una vivienda de más de 150 m2).

Este importe incluye:

- Los trabajos de mantenimiento en las zonas comunes del piso y edificio por parte de la Arrendadora, que se llevarán a cabo como mínimo una vez cada quince días.

- Los consumos de los suministros de agua, gas y electricidad del piso donde está ubicada la habitación, que tienen un límite máximo mensual del conjunto del piso incluido en el importe de la renta, resultante de sumar la cantidad de {{Booking_limit|decimal(1)}} euros mensuales por cada habitación que tenga cada piso. Dicho importe en euros se calculará mensualmente mediante la suma de las tres facturas de suministros (Agua, gas y electricidad). 

Excedido dicho importe mensual máximo de consumo por piso expresado en euros, el exceso se cobrará a partes iguales a todos los ocupantes de las habitaciones del mismo piso, y se le pasará el cargo al cobro dentro de la factura mensual de Renta pero como concepto aparte. 

- El servicio de internet.

No está incluido en la renta:

- Limpieza de salida: La Arrendataria abonará la cantidad de {{Booking_final_cleaning|decimal(1)}} euros dentro de los cinco primeros días naturales contados a partir de la fecha de emisión de la factura.

{% endif %}
El incumplimiento de la obligación de pago de ese recibo en el periodo fijado será motivo de resolución del contrato, dando derecho al arrendador a solicitar el desahucio, siendo por cuenta del arrendatario los gastos que estas acciones originen. Los recibos emitidos se abonarán íntegramente sea cual sea el tiempo en que se utilicen los servicios de alojamiento.

El retraso en el pago por parte de la Arrendataria de la Renta, total o parcial, y por un plazo superior a cinco (5) días naturales contados a partir de la fecha de emisión de la factura (la cual se generará el día 1 de cada mes o el día en que inicie el contrato de alquiler), indicada en la Condición General 4, así como, en su caso, de los conceptos aparte, dará derecho a la Arrendadora a cobrar intereses de demora y, en cualquier caso, a exigir a la Arrendataria el abono de un recargo pactado de 10 euros por factura y por cada día de retraso, una vez requerida formalmente de pago por cualquier medio. La Arrendadora podrá a suspender y resolver el Contrato de Habitación y solicitar la inmediata entrega de la Habitación y el pago de las cantidades pendientes, más los intereses y la penalización.

Se aplicará un recargo de 5 € en concepto de penalización a cada factura emitida de cualquier servicio asociado o derivado del contrato de alquiler por parte de la Arrendataria que no haya sido abonada dentro del mes correspondiente. La Arrendadora podrá a suspender y resolver el Contrato de Habitación y solicitar la inmediata entrega de la Habitación y el pago de las cantidades pendientes, más los intereses y la penalización.

## SÉPTIMA. REPARACIONES.

Una vez entregadas las llaves, la Arrendataria dispondrá de un plazo de quince (15) días naturales para examinar el estado de la Vivienda, el inventario, los muebles y el equipo. En caso de encontrar alguna disconformidad lo hará saber a la Arrendadora mediante el formulario que se contiene en la página web de la Gestora. En caso contrario y transcurridos los indicados quince (15) días naturales, se entenderá que el inventario (con los muebles, equipo y estado general) está en buen estado y orden.

La Arrendataria deberá devolver la Vivienda en las mismas condiciones a la finalización del Contrato, comprometiéndose a su limpieza y conservación. En caso contrario, el coste de restauración al estado original será asumido por la Arrendataria. 

Las facturas de reparaciones de instalaciones de la Vivienda (caldera, sistemas de calefacción, electrodomésticos en general) provocadas por un mal uso o por un deficiente mantenimiento por parte de los residentes, se repercutirán al arrendatario. 
 
El arrendatario es responsable, no sólo de sus propios actos, sino también de los de aquellos a los que invite a la Vivienda.

En el supuesto que se produzca un desperfecto en la Vivienda, cuyo origen y causante no puedan ser identificados de forma individual, todos los ocupantes de la Vivienda asumirán su coste a prorrateo, esto es a partes iguales, con un importe mínimo por arrendatario de cinco euros (5€).

## OCTAVA. RESPONSABILIDADES.

La Arrendataria reconoce que la Arrendadora no proporcionará cobertura de seguro para los bienes de la Arrendataria, ni será responsable de la pérdida de sus bienes, ya sea por robo, incendio u otros, ni a las personas que ocupen el Inmueble durante la vigencia del Contrato o daños que estas pudieran causar a terceros o las cosas.

La Arrendataria podrá contratar y mantener vigente durante todo el plazo contractual una póliza de seguro que cubra el contenido y la responsabilidad civil de terceros.

## NOVENA.  FIANZA Y GARANTÍA ADICIONAL.

El arrendatario entrega a la arrendadora en el transcurso de este acto el importe de {{Booking_deposit|decimal(1)}} euros en concepto de fianza legal equivalente a la parte proporcional de un mes de renta en función de la duración del contrato, para garantizar el cumplimiento por la Arrendataria de todas las obligaciones y responsabilidades que asume. 

Asimismo, el Arrendatario entrega en este acto y en concepto de garantía adicional la suma de {{Booking_deposit|decimal(1)}} euros, equivalente a la parte proporcional de dos meses de renta en función de la duración del Contrato, mediante transferencia bancaria cuya copia se acompaña al presente, como garantía del cumplimiento por el Arrendatario de todas sus obligaciones arrendaticias, así como de la falta de cumplimiento de las personas designadas

Las Partes acuerdan la devolución de la fianza y la garantía adicional a la Arrendataria y sin intereses, en un plazo máximo de treinta (30) días contados desde la finalización del Contrato, previa verificación del correcto estado de las habitaciones y zonas comunes del piso, así como de la no existencia de deudas o cantidades a reclamar a la Arrendataria. La Arrendataria autoriza irrevocablemente y desde ahora a la Arrendadora a la ejecución de la fianza y la garantía adicional para hacer frente a cualquier obligación o pago pendiente de la Arrendataria, debiendo rembolsar el resto, de haberlo, a la Arrendataria.

Para el caso de que una vez devuelta la Vivienda,  la propiedad detecte la existencia de defectos o daños en la misma comunicados o no por el inquilino y que precisen su valoración, reparación y/o reposición, el inquilino autoriza expresamente a la propiedad a retener la  fianza y la garantía adicional hasta que se lleven a cabo dichas actuaciones, y proceder a liquidar importes minorados en el coste de las actuaciones en el plazo máximo de 15 días laborables una vez vencido el plazo de apartado anterior. Paralelamente, si el apartamento queda en muy mal estado de limpieza y el servicio de limpieza tarda más horas de las estipuladas, la diferencia se retendrá de las cantidades entregadas en dichos conceptos. 

Se hace constar expresamente, y así se acepta al suscribirse el presente contrato, que si se produce una baja voluntaria, el arrendatario no tendrá derecho a la devolución del importe de la garantía excepto en el caso de haber dado éste un preaviso por escrito a la propiedad con al menos un mes de antelación a la fecha prevista de la baja, en ese caso sólo se descontarán de la fianza 230 euros en concepto de penalización más la diferencia de tarifa si se le hubiera aplicado por la duración de la estancia. 

La baja involuntaria del arrendatario en cualquier momento de la estancia, incluida la expulsión, o la denegación de visado, entre otros motivos nunca dará derecho a la devolución del importe de la garantía. 

Si una vez finalizado el contrato la arrendataria no rellena y facilita a la gestora o la propiedad, en el plazo máximo de 6 meses contados desde la fecha de finalización contractual, los datos requeridos para la devolución de su garantía, se entenderá que renuncia a ella y quedará en poder de la arrendadora sin derecho a reclamación.

## DÉCIMA. CESIÓN Y SUBARRIENDO.

I. El arrendatario se obliga a no subarrendar, ni ceder o traspasar el inmueble arrendado sin el consentimiento expreso y escrito del arrendador. El incumplimiento de esta cláusula será causa de resolución del contrato. 

{% if Residents %}

II. Que, la Arrendataria manifiesta que junto con ella vivirán de forma temporal en el piso alquilado, y como máximo hasta el plazo de finalización del contrato pactado por la Partes, las personas cuyos datos completos de identificaciónse detallan a continuación:

{%for r in Residents%}
- {%if r.Customer_gender=='H'%}D.{%elif r.Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{r.Customer_name}} con {{r.Customer_id_type}} {{r.Customer_id}}
{%endfor%}

A lo que no se opone la Arrendadora, siempre que:

- ello no se pueda entender en forma alguna como un subarriendo o cesión del contrato.
- que no exceda el número de personas aquí indicadas.
- debiendo la Arrendataria hacer cumplir a dichas personas con las condiciones y normas de uso de las instalaciones.
- respondiendo la Arrendataria por todas y cada una de esas personas en caso de problemas, conflictos, roturas, deterioros o daños propios o a terceros.
- asumiendo la Arrendataria la obligación de entrega de la vivienda o piso a la finalización del contrato, libre de ocupantes y en las condiciones pactadas. 

El incumplimiento de las condiciones indicadas en el punto II anterior supondrá la resolución del contrato con efectos a la fecha de su comunicación, debiendo asumir la Arrendataria con el incumplimiento, así como cualquier gasto y honorarios que se puedan generar hasta la recuperación del piso libre de ocupantes.
{%endif%}
## UNDÉCIMA. OBRAS.

El arrendatario no podrá realizar ningún tipo de obra o modificación en el inmueble o edificio al que pertenece sin el consentimiento expreso de la parte arrendadora. 
 
A pesar de no tener la consideración de obra, se prohíbe expresamente al arrendatario la realización de agujeros o perforaciones en las paredes del inmueble, descontándose de la fianza el importe que sea necesario para que las paredes recuperen su estado original en su caso en caso de incumplimiento. 

## DÉCIMO SEGUNDA. INCUMPLIMIENTO DE OBLIGACIONES.

El incumplimiento por cualquiera de las partes de las obligaciones resultantes del contrato dará derecho a la parte que hubiere cumplido las suyas a exigir el cumplimiento de la obligación y/o a promover la resolución del contrato de acuerdo con lo dispuesto en el artículo 1.124 del Código Civil. 
 
Además de lo ya dicho, el arrendador podrá resolver de pleno derecho el contrato por las siguientes causas: a) La falta de pago de la renta o, en su caso, de cualquiera de las cantidades cuyo pago haya asumido o corresponda al arrendatario, como los consumos b) La falta de pago del importe de la fianza c) La realización de daños causados dolosamente en la finca o de obras no consentidas por el arrendador. d) Cuando en el inmueble tengan lugar actividades molestas, insalubres, nocivas, peligrosas o ilícitas. e) Además se considerará incumplimiento todo aquello que el arrendatario haga en contra de lo dispuesto por la Comunidad de Propietarios del edificio en donde se encuentra la vivienda arrendada, así como contraviniendo todo lo que haya convenido para la limpieza y conservación del inmueble arrendado, incluso con terceras personas o entidades. f) el destino de la vivienda a un uso distinto del expresamente previsto en este contrato sin la previa autorización expresa del arrendador.  
 
Asimismo, en caso de resolución del contrato por la causa prevista en el punto f) anterior, el arrendador podrá exigir al arrendatario indemnización por la suma equivalente al total de las sanciones y la cuantía de cualesquiera otros perjuicios que le fueran causados por el destino de la habitación arrendada o de la vivienda en la que se encuentra a un uso distinto del expresamente previsto en este contrato, incluyendo, en su caso, las consecuencias jurídicas o económicas que pudieran resultar de la incoación de procedimientos sancionadores por incumplimiento de la normativa turística o sobre actividades. 

## DÉCIMO TERCERA. CESIÓN DE DATOS.

La parte arrendataria autoriza a la arrendadora para que pueda ceder los datos personales que constan en este contrato a terceras entidades o personas jurídicas para que oferten al arrendatario servicios realizados con la finca y que pueda recabar de las mismas la información relativa al cumplimiento o incumplimiento de lo que al arrendatario corresponda para el adecuado mantenimiento de la finca arrendada y que pueda afectar a los demás ocupantes del inmueble. 

A los efectos de dar cumplimiento a lo prevenido en la LO 3/2018, de 5 de diciembre, de Protección de Datos de Carácter personal, le informamos que:

Cotown Sharing Life, S.L., con el domicilio en c/Beethoven 15, 7ª planta (Barcelona) es la responsable del tratamiento de los datos personales, y que estos serán conservados durante el plazo necesario para cumplir con la finalidad para la cual fueron recabados. En la dirección de correo electrónico hola@cotown.com puede ejercer sus derechos de acceso, rectificación, supresión, oposición, portabilidad, limitación del tratamiento y en su caso retirar el consentimiento. Asimismo, tiene derecho a interponer una reclamación ante la correspondiente Autoridad de Control.

## DÉCIMO CUARTA. SUMISIÓN.

Los contratantes se someten expresamente a los Juzgados y Tribunales de la ciudad en la que se encuentra ubicado el inmueble, para todas aquellas cuestiones litigiosas que pudieran derivarse del mismo. 

## DÉCIMO QUINTA- LEY APLICABLE.

El arrendatario no tendrá derecho a indemnización de clase alguna a la extinción del contrato.

La arrendataria renuncia expresamente al derecho de adquisición preferente, tanteo y retracto para el supuesto de la transmisión de la vivienda arrendada por cualquier título. 

Este Contrato de arrendamiento, que tiene la condición jurídica de “arrendamiento para uso distinto al de vivienda”, se regirá por el art. 66 bis de la Ley catalana 18/2007 y el título II de la Ley de Arrendamientos Urbanos en cuanto a la fianza, las garantías, la determinación y actualización de la renta, la elevación de la renta por mejoras y la asunción de gastos generales y servicios individuales. El resto de cláusulas se regirá por la voluntad de las partes, en su defecto, por lo dispuesto en el título III de la Ley de Arrendamientos Urbanos y, supletoriamente, por lo dispuesto en los artículos 1.546 y siguientes del Código Civil. 

Y con el carácter expresado en la intervención, firman el presente contrato, en el lugar y fecha indicados. 

| | |
|:-|:-|
|**El Arrendador**|**El Arrendatario**|
{%-for s in Owner_signers-%}
| | |
|![firma]({{Server}}/signature/{{s.Owner_signer}})|<div class="signature">/FIRMACLIENTE/</div>|
|Fdo: {{s.Owner_signer_name}}|{%if loop.index==1%}Fdo: {%if Customer_type=='empresa'%}{{Customer_signer_name}}{%else%}{%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_name}}{%endif%}{%endif%}|
| |{%if loop.index==1%}Fecha:<span style="color:white;">/FECHACLIENTE/</span>{%endif%} |
| | |
{% endfor-%}