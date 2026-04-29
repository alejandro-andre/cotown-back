{% set R = Rooms[0] %}
# CONTRATO DE ARRENDAMIENTO
<br><br>
En Barcelona, a {{Today_day}} de {{Today_month|month}} de {{Today_year}}
<br><br>
## LAS PARTES

{%if R.Owner_id_type=='CIF'%}
De una parte, {%for s in R.Owner_signers%}{%-if loop.index>1%} y {%endif%}{{s.Owner_signer_name}}, mayor de edad, provisto de {{s.Owner_signer_id_type}} {{s.Owner_signer_id}}{%endfor%}, con domicilio profesional en {{R.Owner_address}}, {{R.Owner_zip}} {{R.Owner_city}}, actuando en nombre y representación de {{R.Owner_name}} con el mismo domicilio, {{R.Owner_id_type}} {{R.Owner_id}}{%if R.Owner_signers|length>1%}, en calidad de apoderados mancomunados{%endif%}. La Arrendadora tiene designada para la gestión de este contrato de arrendamiento y uso de habitación y durante todo el plazo de duración a la compañía Cotown Sharing Life, S.L. (la "**Gestora**"), con domicilio profesional en Beethoven 15, 7ª planta, 08021 Barcelona, CIF B67551754, representado por Dª Azucena Esteban Calderon, mayor de edad, provisto de DNI 38148452P, con el mismo domicilio, actuando en nombre de la mencionada sociedad.
{%else%}
De una parte, {{R.Owner_name}}, mayor de edad, con {{R.Owner_id_type}} núm. {{R.Owner_id}}, con domicilio profesional en {{R.Owner_address}}, {{R.Owner_zip}} {{R.Owner_city}} actuando en su nombre y representación.
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

I. Que el Arrendador es propietario de la siguiente finca en [{{R.Resource_flat_street}}], [{{R.Resource_building_city}}] (en adelante “la Vivienda”) que dispone de cédula de habitabilidad, el certificado de eficiencia energética y una superficie de m² construidos que se indica a continuación:

| | | | |
|:-|:-|:-|-:|
|**Piso**|**Cédula de habitabilidad**|**Certificado de eficiencia energética**|**m²**|
{%-for f in Flats_info-%}
|{{f.Resource_flat_address}}|{{f.Resource_flat_occupancy}}|{{f.Resource_flat_energy}}|{{f.Resource_flat_area}}|
{% endfor-%}
| | | | |

II. Que, el Arrendador tiene la consideración de gran tenedor con arreglo a la normativa vigente. 

III. Que, el Arrendatario es una organización/entidad interesada en arrendar la Vivienda de forma temporal para ser ocupada exclusivamente por parte de las personas que se identificarán en el cuerpo de este documento.

Las personas que ocuparán la Vivienda tienen su residencia permanente en los siguientes domicilios y ocuparán  el inmueble antes descrito para la temporada que luego se dirá, por motivos de estudios o trabajo.

Se adjunta al presente la documentación acreditativa de la estancia, a efectos de justificar la necesidad de temporalidad.

V. Que la gestión del presente contrato y, por lo tanto, la representación de la Propiedad durante todo el plazo que dure el presente será llevada a cabo por la compañía Cotown Sharing Life, S.L. (la gestora)

V. Y, estando ambas partes interesadas en el arrendamiento de conformidad con los términos que seguidamente se convienen, suscriben el presente **contrato de arrendamiento de temporada**, de conformidad con las siguientes:

## ESTIPULACIONES

## 1. OBJETO DEL CONTRATO DE ARRENDAMIENTO

1.1. El Arrendador cede en arrendamiento al Arrendatario la Vivienda  con el número de plazas que se indican a continuación, por el plazo y precio indicados en los siguientes pactos (en adelante el "**Contrato de arrendamiento**")

{% for r in Rooms %}
- [{{r.Resource_address}}]
{%-endfor %}

1.2. La vivienda se destinará de forma exclusiva a vivienda de temporada por parte de las personas cuyos nombres completos, datos de identificación, incluyendo los datos de su residencia permanente y habitual, así como habitaciones y plazas asignadas en la Vivienda constan en el anexo al presente documento, adjuntándose también los documentos que acreditan el motivo de dicha temporalidad

El Arrendatario hará cumplir a las personas que designe las obligaciones aquí contenidas, haciéndose responsable el Arrendatario en caso de incumplimiento, lo cual acepta. El Arrendatario no podrá modificar el destino de la Vivienda ni las personas que hagan uso de cada habitación según consta en el anexo al presente, todo ello sin la previa novación por escrito del Contrato de arrendamiento.

1.3. El uso de la Vivienda otorga el uso de los servicios comunes y los suministros de los que está dotada (agua, gas, electricidad e internet).

## 2. DURACIÓN

2.1. El arrendamiento de la Vivienda entra en vigor a la fecha de firma del presente contrato, de conformidad con la reserva aceptada, y se procede al bloqueo de la Vivienda para que esté a disposición del Arrendatario cuando inicie su uso durante todo el plazo que se indica a continuación. 

El arrendamiento se pacta por temporada y, por tanto, por tiempo determinado, común y de obligado cumplimiento, plazo este que empezará a contar desde el {{Booking_date_from_day}}/{{Booking_date_from_month}}/{{Booking_date_from_year}} y finalizará el {{Booking_date_to_day}}/{{Booking_date_to_month}}/{{Booking_date_to_year}}. 

2.2. Llegada la fecha final del arrendamiento, el Arrendatario dejará libre y a disposición del Arrendador la Vivienda, sin necesidad de preaviso alguno, haciendo entrega de cada habitación e inventario en perfecto estado, así como de todos los juegos de llaves. 

2.3. Coincidiendo con el día de entrega de la Vivienda, el Arrendatario entregará al Arrendador los juegos de llaves de la portería y la Vivienda. En caso de pérdida o extravío de las llaves, el Arrendatario deberá abonar el coste de 150 euros por cada llave o juego de llave completo, según sea el caso y para cada habitación. 

2.4. Una vez finalizado el plazo de arrendamiento pactado, este solo podrá prorrogarse por los motivos previstos en la ley, y con el acuerdo previo y por escrito de ambas partes.
  
## 3. RENTA Y CONCEPTOS DEL ARRENDAMIENTO

Por el arrendamiento de la vivienda, el Arrendatario abonará obligatoriamente al Arrendador y durante todo el Plazo la cantidad de (la "**Renta**"):

{% for rent in Prices %}
{%-if Owner_id == Service_id %}
- Mes {{rent.Rent_date_month}}/{{rent.Rent_date_year}}: [{{(rent.Rent+rent.Services+(rent.Rent_discount or 0)+(rent.Services_discount or 0))|decimal(1)}}] euros mensuales por plaza.
{%-else %}
- Mes {{rent.Rent_date_month}}/{{rent.Rent_date_year}}: [{{(rent.Rent+(rent.Rent_discount or 0))|decimal(1)}}] euros mensuales por plaza.
{%-endif %}
{%-endfor %}


El pago de la renta y conceptos asimilados se realizará por el Arrendatario al Arrendador mediante transferencia bancaria a la cuenta designada por el Arrendador, entre los cinco primeros días de cada mes, debiendo remitir un comprobante de esta.

La renta del presente contrato se ha establecido teniendo en cuenta lo siguiente:

a) Que el Arrendador tiene la condición de gran tenedor.

b) Que la Vivienda está situada en una zona de mercado residencial tensionado.

c) Que la Vivienda ha estado arrendada / no ha estado arrendada durante los últimos 5 años como vivienda habitual en virtud de un contrato sujeto a la Ley de Arrendamientos Urbanos.

d) Del mismo modo, el importe de la renta se ha establecido según lo previsto en el Artículo 17.6 y 7 de la Ley de Arrendamientos Urbanos y en virtud de lo dispuesto en la ley 18/2007 de Vivienda de Cataluña según la redacción dada por la ley 11/2025 de 29 de diciembre de medidas en materia de vivienda y urbanismo.

{% if Booking_type == 'recreativo' %}
{% if Booking_final_cleaning and Booking_final_cleaning > 0 %}

La gestora de la Propiedad cobrará al Arrendatario un importe de [{{Booking_final_cleaning|decimal(1)}}] euros (21% IVA incluido) por plaza en concepto de limpieza de salida a la finalización de la estancia.
{% endif %}

{% elif Booking_limit_type == 'indice' %}
De conformidad con lo anterior, la determinación de la renta de la Vivienda se ha determinado tomando en consideración el índice de Referencia Estatal (se acompaña como anexo).

Los conceptos indicados a continuación no están incluidos en la renta y se facturarán como conceptos aparte de forma mensual:

- Gastos por suministros de los que esté dotada la Vivienda y hasta el límite de [{{Booking_limit|decimal(1)}}] euros por persona y mes
- IBI y gastos de la comunidad de propietarios 

{% elif Booking_limit_type == 'lau' %}
De conformidad con lo expuesto, la determinación de la renta se ha efectuado tomando como referencia:

- la última renta del contrato de arrendamiento de vivienda habitual que permaneció vigente hasta [{{Resource_last_LAU_date}}], cuyo importe ascendía a [{{Resource_last_LAU_rent or 0|decimal(1)}}] euros mensuales.

- el Índice de Referencia Estatal que se adjunta como anexo al presente.

Por ello, de conformidad con lo dispuesto en los Apartados 6 y 7 del Art. 17 de la LAU la renta del arrendamiento corresponde a la menor entre la última renta del contrato anterior actualizada y la resultante del Índice de Referencia Estatal.

Aplicada la actualización de la renta conforme al Índice de Precios al Consumo correspondiente, así como el incremento del 10 % autorizado por la realización de obras de mejora en la Vivienda en los dos años anteriores, la renta resultante asciende a [{{Booking_rent|decimal(1)}}] euros mensuales.

El Arrendatario abonará también: 

- Gastos por suministros de los que esté dotada la Viviendao y hasta el límite de [{{Booking_limit|decimal(1)}}] euros por persona y mes

{% else %}
De conformidad con lo anterior, la determinación de la renta se ha llevado a cabo tomando en consideración la consulta realizada en la página web del Ministerio de Vivienda y Agenda Urbana a efectos de determinar la existencia de Índice de Referencia (se acompaña informe como anexo a la consulta del que resulta que no existe precio de referencia a dichos efectos, por tratarse de una vivienda de más de 150 m2).
{% if Booking_final_cleaning and Booking_final_cleaning > 0 %}

La gestora de la Propiedad cobrará al Arrendatario un importe de [{{Booking_final_cleaning|decimal(1)}}] euros (21% IVA incluido) por plaza en concepto de limpieza de salida a la finalización de la estancia.
{% endif %}
{% endif %}

## 4. CLÁUSULA DE EXENCIÓN DE IVA

4.1. Resultará aplicable la exención de pago del IVA prevista en el artículo 20. Uno. 23º. b) de la Ley 37/1992, de 28 de diciembre del Impuesto sobre el Valor Añadido, por cuanto la Vivienda completa constituirá la vivienda de las personas designadas por el Arrendatario, cuyos nombres y datos de identificación constan en el anexo, siendo el destino del inmueble el uso exclusivo como vivienda según ha quedado definido en el pacto primero anterior.

## 5. CONDICIONES DE CANCELACIÓN

- Cancelaciones realizadas hasta dos meses antes de la fecha de llegada sin gastos de cancelación.

- Cancelaciones realizadas entre un mes y medio y un mes antes de la fecha de llegada se penalizará con un importe del 50% de la totalidad de la reserva.

- Cancelaciones realizadas entre un mes antes de la fecha de llegada y hasta la fecha de llegada se penalizará con un importe del 85% de la totalidad de la reserva.

- A partir de la fecha de llegada y durante toda la estancia, cualquier cancelación total o parcial y reducción de estancia se penalizará con el importe del 100% de la totalidad de la reserva.

## 6. ARRENDAMIENTO Y CESIÓN DEL CONTRATO DE ARRENDAMIENTO

6.1. El Arrendatario no podrá en modo alguno subarrendar, ceder o traspasar los derechos de este Contrato de arrendamiento a terceros.

6.2. En el supuesto de que el Arrendatario incumpliera esta obligación, podrá el Arrendador resolver el presente Contrato de arrendamiento.

## 7. DERECHO DE ADQUISICIÓN PREFERENTE

7.1. El Arrendatario renuncia expresamente a cualesquiera derechos de adquisición preferente o de tanteo y/o retracto que sobre la Vivienda arrendada y/o sus derechos le pudieren corresponder.

## 8. ESTADO FÍSICO DE LA VIVIENDA COMPLETA Y REPARACIONES

8.1. El Arrendatario reconoce recibir la Vivienda en perfecto estado de conservación y mantenimiento, apta para el destino convenido y, por lo tanto, a su entera satisfacción.

8.2. Serán por tanto de cuenta del Arrendatario los desperfectos y deterioros que en el mismo se ocasionen.

8.3. La necesidad de reparaciones no otorgará al Arrendatario derecho alguno a la suspensión del Contrato de arrendamiento o a desistir del mismo, ni a indemnización alguna, así como tampoco a reducir o paralizar el pago de la renta.

8.4. Cualquier situación de crisis sanitaria, alarma, pandemia o similar no supondrá la reducción total o parcial de la renta, que deberá ser igualmente abonada salvo acuerdo expreso de las Partes.

## 9. OBRAS

9.1. Las partes convienen expresamente que queda prohibida la ejecución de cualquier tipo de obras por el Arrendatario.

9.2. Será causa de resolución del presente Contrato de arrendamiento la ejecución por el Arrendatario de obras no autorizadas por el Arrendador.

9.3. Cualquier obra que el Arrendatario realice en la Vivienda quedará en beneficio de este, sin derecho a reclamación o indemnización por parte del Arrendatario.

## 10. FIANZA Y GARANTÍA ADICIONAL

10.1. El Arrendatario entrega en este acto y en concepto de fianza legal la suma de [{{Booking_deposit|decimal(1)}}] euros, equivalente a la parte proporcional de un mes de renta en función de la duración del Contrato , mediante transferencia bancaria cuya copia se acompaña al presente, como garantía del cumplimiento por el Arrendatario de todas sus obligaciones arrendaticias, así como de la falta de cumplimiento de las personas designadas.

10.2. Asimismo, el Arrendatario entrega en este acto y en concepto de garantía adicional la suma de [{{Booking_deposit|decimal(1)}}] euros, equivalente a la parte proporcional de dos meses de renta en función de la duración del Contrato, mediante transferencia bancaria cuya copia se acompaña al presente, como garantía del cumplimiento por el Arrendatario de todas sus obligaciones arrendaticias, así como de la falta de cumplimiento de las personas designadas.

10.3. Ambas partes acuerdan la restitución íntegra de la fianza legal y de la garantía al Arrendatario en el momento de la finalización del Contrato de arrendamiento, previa verificación del correcto estado de la Vivienda al momento de la entrega.

## 11. GASTOS E IMPUESTOS

El Arrendador abonará los gastos, cargas o impuestos propios de la Vivienda repercutiendo en el Arrendatario aquellos que se han hecho constar expresamente en el pacto 3 anterior.

## 12. CAUSAS DE TERMINACIÓN DEL CONTRATO DE ARRENDAMIENTO

12.1. El presente Contrato de arrendamiento finalizará al cumplimiento del plazo estipulado, y se resolverá por incumplimiento de cualquiera de las obligaciones contractuales asumidas por el Arrendatario en el presente documento.

12.2. El Arrendatario renuncia expresamente a cualquier derecho a indemnización con motivo de la terminación o resolución anticipada del Contrato de arrendamiento.

## 13. OTRAS OBLIGACIONES DEL ARRENDATARIO

13.1. Además de las obligaciones contenidas en los párrafos precedentes de este Contrato de arrendamiento, el Arrendatario se obliga a lo siguiente:

a) A no instalar transmisiones, motores, máquinas, etc., que produzcan vibraciones o ruidos molestos para los demás ocupantes de la Vivienda o de las colindantes, o que pueda afectar la consistencia, solidez o conservación de la misma.

b) A no almacenar manipular en la Vivienda materias explosivas, inflamables, incómodas o insalubres, y observar en todo momento las disposiciones vigentes.

c) A permitir el acceso a la Vivienda al propietario, administrador y a los operarios o industriales mandados por cualesquiera de ambos, para la realización, inspección y comprobación de cualquier clase de obras o reparaciones que afecten a la Vivienda.

d) A cumplir en todo momento las normas estatutarias, reglamentarias y los acuerdos que la comunidad de propietarios tenga establecidos o establezcan, en orden a la utilización de los servicios, elementos comunes y buen régimen de convivencia.

e) Se prohíbe expresamente la tenencia de cualquier animal en la finca arrendada.

f) Se prohíbe expresamente la realización de actividades molestas, insalubres, nocivas, peligrosas o ilícitas.

## 14. PROTECCIÓN DE DATOS

Ambas partes tratarán los datos personales de los representantes, así como del resto de personas que intervengan en la relación jurídica con la finalidad de cumplir con los derechos y obligaciones contenidas en este Contrato de arrendamiento y en las disposiciones que establece la normativa vigente en materia de protección de datos (LOPDGDD), para poder prestar el servicio contratado. El tratamiento de dichos datos queda legitimado por la ejecución del presente Contrato de arrendamiento.

Los datos proporcionados se conservarán mientras se mantenga la relación contractual o durante el tiempo necesario para cumplir con las obligaciones legales y atender las posibles responsabilidades que pudieran derivar del cumplimiento de la finalidad para la que los datos fueron recabados. Los datos no se cederán a terceros salvo en los casos en que exista una obligación legal. Asimismo, no se realizan transferencias internacionales de datos.

Los interesados podrán ejercer sus derechos de acceso, rectificación, supresión de datos, así como solicitar la portabilidad de los datos, que se limite el tratamiento o a oponerse al mismo, mediante escrito a cada una de las partes a través de la dirección mencionada en el encabezamiento del Contrato de arrendamiento. Asimismo, los interesados tendrán derecho a presentar una reclamación ante la Agencia Española de Protección de Datos.

## 15. NOTIFICACIONES

15.1. A efectos de recepción de notificaciones, las Partes han designado los domicilios indicados al principio, y las direcciones de correo electrónico que se indican a continuación.

- El Arrendador: housing@cotown.com

- El Arrendatario en la persona de {%if Customer_type=='empresa'%}[{{Customer_signer_name}}]{%else%}[{{Customer_name}}]{%endif%}, con direcciones de correo electrónico: [{{Customer_email}}]

15.2. Las Partes podrán variar las direcciones que figuran en el apartado anterior, comunicándolo a la otra Parte por escrito, en la forma indicada en el apartado inmediatamente anterior.

## 16. DERECHO APLICABLE, IDIOMA Y JURISDICCIÓN COMPETENTE 

16.1. Derecho aplicable

Este Contrato de arrendamiento, que tiene la condición jurídica de “arrendamiento para uso distinto al de vivienda”, se regirá por el art. 66 bis de la Ley catalana 18/2007 y el título II de la Ley de Arrendamientos Urbanos en cuanto a la fianza, las garantías, la determinación y actualización de la renta, la elevación de la renta por mejoras y la asunción de gastos generales y servicios individuales. El resto de cláusulas se regirán por la voluntad de las partes, en su defecto, por lo dispuesto en el título III de la Ley de Arrendamientos Urbanos y, supletoriamente, por lo dispuesto en los artículos 1.546 y siguientes del Código Civil. Además, resulta de aplicación lo previsto en el artículo 20. Uno. 23º. b) de la Ley 37/1992, de 28 de diciembre del Impuesto sobre el Valor Añadido en cuanto a la exención de pago del I.VA.

16.2. Idioma

El presente Contrato de arrendamiento se redacta en idioma español. Los documentos que tengan que ser traducidos a un idioma distinto del español serán abonados por la parte que lo solicite.

16.3. Jurisdicción

Para resolver cualquier interpretación o disputa derivada del presente Contrato de arrendamiento, las partes se someterán a la jurisdicción de los juzgados y tribunales de la ciudad de Barcelona con renuncia a su propio fuero si fuese el caso.

Y, habiendo leído y comprendido la totalidad del presente Contrato de arrendamiento, lo firman en prueba de aceptación y conformidad, por duplicado ejemplar y a un solo efecto, en el lugar y la fecha indicados en el encabezado.

| | |
|:-|:-|
|**El Arrendador**|**El Arrendatario**|
{%-for s in Owner_signers-%}
| | |
|![firma]([{{Server}}]/signature/[{{s.Owner_signer}}])|<div class="signature">/FIRMACLIENTE/</div>|
|Fdo: [{{s.Owner_signer_name}}]|{%if loop.index==1%}Fdo: {%if Customer_type=='empresa'%}[{{Customer_signer_name}}]{%else%}{%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} [{{Customer_name}}]{%endif%}{%endif%}|
| |{%if loop.index==1%}Fecha:<span style="color:white;">/FECHACLIENTE/</span>{%endif%} |
| | |
{% endfor-%}