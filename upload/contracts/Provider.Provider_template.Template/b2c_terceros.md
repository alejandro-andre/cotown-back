# CONTRATO DE ARRENDAMIENTO Y USO DE HABITACIÓN.



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

La Arrendadora y la Arrendataria serán referidas conjuntamente en adelante como las "**Partes**".

Las Partes acuerdan conjuntamente suscribir el presente contrato que se regirá por las siguientes condiciones particulares (las "**Condiciones Particulares**") y las condiciones generales (las "**Condiciones Generales**"):


## MANIFIESTAN

I. Que, la Arrendadora es una entidad cuyo objeto es el arrendamiento de habitaciones para su uso por terceros en los edificios de su propiedad. 

II. La Arrendataria está interesada en arrendar y usar de forma temporal una de las habitaciones propiedad de la Arrendadora, en uno de los edificios de la Arrendadora.

III. En su virtud, las partes acuerdan celebrar este contrato de arrendamiento y uso de habitación, de acuerdo con las siguientes condiciones particulares y generales.


## ESTIPULACIONES

## A. CONDICIONES PARTICULARES

## 1. Objeto.

1.1 Las Condiciones particulares descritas a continuación junto con las condiciones generales tienen por objeto regular las relaciones entre la Arrendadora y la Arrendataria en todo lo relativo al contrato de arrendamiento y uso de habitación por temporada, (en adelante el "**Contrato de Habitación**"), en el piso {{Resource_flat_address}} del edificio de la calle {{Resource_building_address}} {{Resource_flat_street}} de la ciudad de {{Resource_building_city}}, para el tipo de habitación acordado en el documento de reserva (la "**Habitación**") y por el plazo que luego se dirá. 

## 1.2. Vinculación con las Condiciones Generales 

Las Condiciones Particulares están vinculadas necesaria y obligatoriamente con las condiciones generales que se contienen a continuación de las condiciones particulares (las "**Condiciones Generales**") y que completan a las presentes condiciones particulares en todo lo no previsto en las mismas, siendo éstas de obligado cumplimiento, las cuales se dan aquí por reproducidas y por tanto aceptadas mediante la firma del presente documento, formando desde ese momento las condiciones Particulares y la Generales de forma conjunta e indisoluble las condiciones del presente Contrato de Habitación.

## 1.3 Vinculación con las Normas de Uso

Las Condiciones Particulares del presente Contrato de Habitación están vinculadas necesariamente con las normas de uso que constan en la página web de la Arrendadora y de la Gestora (las "**Normas de Uso**"), y completan a las Condiciones Particulares y las Condiciones Generales del Contrato de Habitación, siendo de obligado cumplimiento para la Arrendataria en todo momento durante la duración del presente Contrato de Habitación.

## 1.4 Designación de la gestora

La Arrendadora tiene designada para la gestión de este contrato de arrendamiento y uso de habitación y durante todo el plazo de duración a la compañía Cotown Sharing Life, S.L. (la "**Gestora**"). 

La Arrendadora tiene delegada en la web de la gestora {{Segment_url}} el área privada a la que se podrá dirigir la Arrendataria para algunas de las gestiones de su Contrato de Habitación durante todo el plazo de duración.

## 2. Descripción del arrendamiento

La Arrendataria contrata el arrendamiento y uso de la Habitación indicada en la Condición Particular 1 anterior, (según documento de reserva), que se da aquí por íntegramente reproducido, para su uso como alojamiento temporal por motivos de estudio/trabajo, con el mobiliario y equipamiento que constan en la página web de la Arrendadora y de la Gestora, y con la posibilidad de uso de las zonas comunes que se indica en las Condiciones Generales.

## 3. Plazo

El Contrato de Habitación entra en vigor a la fecha de efectivo pago del importe de la garantía y tendrá un plazo de duración que va desde el día {{Booking_date_from_day}}/{{Booking_date_from_month}}/{{Booking_date_from_year}} al día {{Booking_date_to_day}}/{{Booking_date_to_month}}/{{Booking_date_to_year}} (el "**Plazo**"). Una vez cumplido este Plazo, el Contrato de Habitación quedará resuelto automáticamente sin necesidad de previo requerimiento o aviso. 

Sin perjuicio del Plazo, la Arrendataria tendrá derecho a resolver el Contrato de Habitación en cualquier momento siempre que dé un preaviso mínimo a la Arrendadora de cuarenta y cinco (45) días naturales a la fecha en la que desee finalizar el Contrato de Habitación, sin incurrir en ningún coste adicional o penalización por dicho motivo, salvo con la obligación de devolución de todos los descuentos aplicados en su caso, por el Plazo de tiempo inicialmente contratado y no cumplido.

La entrada y puesta a disposición de la Habitación tendrá lugar el primer día del Plazo y se llevará a cabo en la forma pactada por las Partes en el formulario de entrada y registro que se remitirá a la Arrendataria por mail o que estará a su disposición en el área privada de la web de la Gestora. 

## 4. Precio

Por el arrendamiento y uso de la Habitación por la Arrendataria conforme al presente Contrato de Habitación, la Arrendataria abonará obligatoriamente a partir del inicio del Plazo, la cantidad de (la "**Renta**"):

{%for rent in Prices%}
{%-if Owner_id == Service_id-%}
- Mes {{rent.Rent_date_month}}/{{rent.Rent_date_year}}:   {{(rent.Rent+rent.Services)|decimal}} euros mensuales
{%else%}
- Mes {{rent.Rent_date_month}}/{{rent.Rent_date_year}}:   {{rent.Rent|decimal}} euros mensuales
{%endif%}
{%-endfor%}

mediante los cargos recurrentes que efectuará la Arrendadora en la cuenta corriente o tarjeta de crédito designada por la Arrendataria durante todo el Plazo del Contrato de Habitación.

## 4.1. Conceptos incluidos en el Contrato de Habitación.

- Los consumos de los suministros de agua, gas y electricidad del piso donde está ubicada la habitación, tienen un límite máximo mensual del conjunto del piso incluido en el importe de la renta, resultante de sumar la cantidad de 60 euros mensuales por cada habitación que tenga cada piso. Dicho importe en euros se calcula para cada mes y mediante la suma de las tres facturas de suministros (Agua, gas y electricidad). Excedido dicho importe mensual máximo de consumo por piso expresado en euros, el exceso se cobrará a partes iguales a todos los ocupantes de las habitaciones del mismo piso, y se le pasará el cargo al cobro dentro de la factura mensual de Renta pero como concepto aparte. 

- El servicio de internet.

## 5. Facturación y pago. 

La facturación por el importe de la Renta y cualesquiera otros conceptos aparte de aquella se realizará con carácter mensual, expresando separadamente el periodo o periodos al que corresponda y detallando cada concepto facturado.

El importe total a pagar se pasará al cobro entre los días 1 a 5 de cada mes. 

En cualquiera de los casos, la Arrendataria reconoce y confirma el mandato para el cobro de las facturas correspondientes a través de la cuenta corriente o tarjeta de crédito por ella designada según lo indicado en esta cláusula.

En este contexto, mediante la suscripción del presente Contrato de Habitación, la Arrendataria acepta de forma expresa recibir la factura expresada con el aviso de cobro en su área interna, sin perjuicio de su derecho a recibir la factura en papel.

## 6. Prestación de Garantía

Coincidiendo con la firma del Contrato de Habitación, la Arrendataria ha efectuado el pago a favor de la Arrendadora de una garantía en la suma de {{Booking_deposit|decimal}} euros (la "**Garantía**"), para garantizar el cumplimiento por la Arrendataria de todas las obligaciones que asume en el Contrato de Habitación, Condiciones Particulares, Condiciones Generales, Normas de Uso y responsabilidades económicas asumidas por la Arrendataria. 

Las Partes acuerdan la devolución de la Garantía a la Arrendataria y sin intereses, en un plazo máximo de treinta (30) días contados desde la finalización del Contrato de Habitación, previa verificación del correcto estado de la Habitación y las zonas comunes del piso, así como de la no existencia de deudas o cantidades a reclamar a la Arrendataria.

La liquidación de daños y deuda que tuviera pendiente la Arrendataria y que sea presentada por la Arrendadora o persona que ésta designe a la Arrendataria será suficiente para acreditar el saldo resultante adeudado por la Arrendataria (saldo deudor) en la fecha de resolución o vencimiento del Contrato de Habitación, a cuyo pago vendrá obligada la Arrendataria. La Arrendataria autoriza irrevocablemente y desde ahora a la Arrendadora a la ejecución de la Garantía para hacer frente a cualquier obligación o pago pendiente de la Arrendataria, debiendo rembolsar el resto, de haberlo, a la Arrendataria.

## 7. Notificaciones

A efectos de recepción de notificaciones, las Partes han designado las personas y los domicilios indicados al principio, así como las direcciones de correo electrónico que se indican a continuación.

Correo electrónico de la gestora de la Arrendadora: hola@cotown.es

Correo electrónico de la Arrendataria: {{Customer_email}}

Las Partes podrán variar las direcciones que figuran en el apartado anterior, comunicándolo a la otra Parte por escrito y con mensaje de recepción.


## B. CONDICIONES GENERALES


## 1. Objeto del Contrato de Habitación

El objeto del Contrato de Habitación es el uso de la habitación, equivalente a una parte alícuota del piso (la "Habitación") y que concede el derecho de uso exclusivo de la habitación solicitada, sita en el edificio propiedad de la Arrendadora, gestionado por la Gestora, exclusivamente por la Arrendataria, con el mobiliario y equipamiento que se describe en la página web de la Arrendadora, y para su uso solo como alojamiento temporal por motivos de estudio o trabajo sin que sea destinada a residencia permanente de la Arrendataria con derecho además al uso compartido de las zonas y servicios comunes, así como los suministros (agua, gas, electricidad e internet), que no serán con carácter exclusivo.

Siendo el domicilio habitual y permanente de la Arrendataria el que consta en las Condiciones Particulares, el arrendamiento de la Habitación es tan solo para el Plazo indicado en las Condiciones Particulares.

La Habitación no podrá ser destinada a un uso como alojamiento turístico o análogo (apartamentos turísticos y viviendas de uso turístico, etc.).

La Arrendataria no podrá modificar el destino de la mencionada Habitación. Su incumplimiento será motivo de resolución del Contrato de Habitación.

## 2. Entrega de llaves

La entrega de las llaves de la Habitación tendrá lugar el día y forma señalada en las Condiciones Particulares.
Una vez entregadas las llaves, la Arrendataria dispondrá de un plazo de quince (15) días naturales para examinar el estado de la Habitación, el inventario, los muebles y el equipo. En caso de encontrar alguna disconformidad lo hará saber a la Arrendadora mediante el formulario que se contiene en la página web de la Gestora. En caso contrario y transcurridos los indicados quince (15) días naturales, se entenderá que el inventario (con los muebles, equipo y estado general) está en buen estado y orden.

En caso de pérdida o extravío de una o la totalidad del llavero con las llaves durante el Plazo del Contrato de Habitación, la Arrendataria podrá pedir otra llave o llavero a la Arrendadora, y por ello se le cobrará el importe de 100 euros por cada reposición.

La Habitación se entrega en perfecto estado de cuidado y mantenimiento. La Arrendataria deberá devolverla en las mismas condiciones a la finalización del Contrato de Habitación, comprometiéndose a su limpieza y conservación. En caso contrario, el coste de restauración al estado original será asumido por la Arrendataria. 

La Arrendataria ha sido informada y acepta las Normas de Uso del que forma parte la Habitación que se contienen en la página web de la Gestora y es conocedora de que a partir de las 22:00 horas queda totalmente prohibido hacer cualquier tipo de ruido que pueda molestar a los vecinos o demás ocupantes del piso y edificio. Si se producen este tipo de incidentes, así como si se altera la buena convivencia en el uso de la habitación o piso, o se realizan desordenes, fiestas, desperfectos o se consume y se posee sustancias estupefacientes o ilegales, ello será considerado motivo de resolución del Contrato de Habitación pues la propiedad se reserva siempre el derecho de admisión.

## 3. Duración

El arrendamiento se pacta por temporada y por tanto por tiempo determinado, empezando y finalizando los días indicados en las Condiciones Particulares del Contrato de Habitación.

A las 10:00 horas de la mañana del último día del Plazo del Contrato de Habitación, la Arrendataria dejará libre y a disposición de la Arrendadora la Habitación, sin necesidad de preaviso alguno, haciendo entrega de la Habitación con el inventario, muebles y enseres en perfecto estado, así como de todos los juegos de llaves que le hubieran sido entregados a la Arrendataria. 

En el caso de que exista algún desperfecto atribuible a la Arrendataria, esta lo pondrá en conocimiento de la Arrendadora a fin de abonar el coste de reparación o sustitución según sea el caso. En caso de que no hubiera sido puesto de manifiesto por la Arrendataria, pero tras la entrega la Arrendadora lo percibiera, se lo comunicará a la Arrendataria, así como el coste correspondiente a dicha reparación para que proceda con el abono correspondiente.

La Arrendataria podrá manifestar a la salida y entrega de la Habitación cualquier comentario relativo al estado de esta y de su inventario, o de las zonas comunes del piso, mediante el formulario que se contiene en la página web de la Gestora. En caso de no manifestar nada al respecto, la reparación o sustitución de desperfectos o roturas será abonada por la Arrendataria con cargo a la Garantía y hasta donde alcance. 

La Arrendataria acepta expresamente que la presentación por la Arrendadora de la cuenta de liquidación por la reparación o sustitución será suficiente para acreditar la obligación de pago de esta por la Arrendataria. 

Si la Arrendataria continúa ocupando la Habitación una vez cumplido el vencimiento del Contrato de Habitación, ésta tendrá que satisfacer en concepto de cláusula penal la cantidad de 200 euros por cada día que la parte Arrendataria se exceda en la estancia del Plazo pactado por las Partes. Además, y por ocupar la Habitación sin autorización de la Arrendadora, la Arrendataria deberá satisfacer en concepto de indemnización de daños y perjuicios la cantidad de 150 euros al día, hasta que desaloje efectivamente la Habitación. Tanto el importe en concepto de cláusula penal como por daños y perjuicios podrán ser descontados por la Arrendadora del importe de la garantía y hasta donde alcance y en caso de que se supere el importe de la Garantía, la Arrendataria deberá proceder con el abono de la diferencia hasta las penalizaciones efectivamente incurridas con carácter semanal.

## 4. Renta

La Renta acordada entre las Partes es la cantidad indicada en las Condiciones Particulares y que abonará la Arrendataria por meses anticipados, mediante cargo que realizará la Arrendadora, entre los cinco (5) primeros días de cada mes, en la cuenta bancaria de la Arrendataria abierta en un banco español o sistema de pago alternativo acordado.

Mediante la firma del presente y salvo que las Partes acuerden otra forma de pago, la Arrendataria autoriza a que la Arrendadora realice cargos recurrentes para el pago de la Renta acordada en la cuenta bancaria o tarjeta de crédito que se indicará, y durante el Plazo del Contrato de Habitación. En su caso se acompañará orden de domiciliación de adeudo directo SEPA.

La Arrendataria se compromete y obliga a subir a su área interna el documento SEPA con el número de cuenta IBAN de la Arrendataria donde realizar los cargos en cuenta de los recibos mensuales de la Renta, debiendo informar a su entidad financiera y a la Arrendadora. 

Los consumos de suministros de agua, gas y electricidad se incluyen en la renta mensual con el límite mensual indicado en las Condiciones Particulares. Excedido dicho importe, la Arrendadora pasará al cobro un recibo con el exceso de consumo lo cual acepta expresamente la Arrendataria.

Las refacturaciones se realizarán según lo siguiente:

1. Entre el día 1 y el 5 de diciembre.
2. Entre el día 1 y 5 de marzo.
3. Entre el día 1 y 5 de junio.
4. A la entrega de la habitación.

El servicio de internet está incluido en la Renta. 

Todo coste, gasto o interés bancario que se derive de un impago de la Renta y demás cantidades, en caso de que se produzca, deberá abonarlo la Arrendataria.

El pago de la Renta no podrá ser suspendido por ninguna causa o motivo salvo a la finalización del Contrato de Habitación por las causas aquí acordadas.

Cualquier situación de crisis, alarma, pandemia o similar no supondrá la reducción total o parcial de la renta que deberá ser igualmente abonada.

## 5. La Arrendataria está obligada a: 

a) informar a la Arrendadora de cualquier incidente avería o daño que detecte dentro de la Habitación, piso, o edificio, así como en elementos del mobiliario e inventario;

b) no tener animales en la Habitación ni entrar animales al edificio; 

c) cumplir en todo momento las Normas de Uso y cumplir todas las leyes aplicables en todo momento; 

d) permitir el acceso a la Habitación a la Arrendadora o persona enviada para inspeccionar y comprobar el estado general de la Habitación, inventario e instalaciones en general, para la realización de cualquier tipo de trabajo o reparación. Las entradas en la Habitación serán anunciadas con un (1) día natural de antelación, en cuyo caso se acordará una hora adecuada para ambas Partes. En caso de falta de acuerdo la visita será entre las 08:00 y las 11:00 horas, debiendo permitir el acceso a la Habitación la Arrendataria, salvo casos de urgencia o necesidad, en cuyo caso no será exigible preaviso alguno, pero si un previa aviso por cualquier medio. 

e) a hacerse cargo de la reparación que le sea atribuible por daños en las cosas. 

f) no utilizar la Habitación con ningún fin comercial o ningún tipo de actividad que pueda resultar ilícita, molesta o dañina, tanto para la Habitación como para la seguridad de la población o los vecinos.

g) mantener en buen estado la Habitación, sus componentes, mobiliario, los baños, el sumidero de evacuación de agua de las instalaciones en el baño, procurando en todo momento que se mantenga limpio y en buen estado.

h) la Arrendataria no podrá realizar agujeros en las paredes, techos o suelo de la Habitación o piso por ningún motivo.

i) la Arrendataria es la única responsable de hacer un uso correcto y legítimo del servicio de internet.

j) la Arrendataria se hace responsable de las personas invitadas a la Habitación durante las horas especialmente habilitadas para ello y de los objetos y pertenencias que se encuentren en la misma.

k) la Arrendataria se compromete a que la Habitación no sea ocupada por terceras personas a parte de la Arrendataria.

l) la Arrendataria no debe mantener ni tener en la Habitación ningún material de carácter peligroso, inflamable o explosivo que pueda aumentar de manera injustificada el peligro de incendio dentro o alrededor del edificio o que pueda considerarse peligroso.

m) Las personas invitadas al piso o Habitación no están autorizadas a pernoctar en la Habitación o piso, cuyo uso exclusivo se atribuye a la Arrendataria. 

## 6. La Arrendadora está obligada a:

a) Mantener a la Arrendataria en la Habitación acordada salvo el derecho de cambio aquí previsto.

b) El mantenimiento del piso y espacios comunes del piso así como de los elementos comunes del edificio para un buen funcionamiento y uso.

c) Facilitar los suministros de agua, gas, electricidad e Internet en la forma indicada. 

d) Rembolsar la Garantía a la Arrendataria, tal y como se estipula en las Condiciones Generales.

e) Reparar y/o sustituir cualquier servicio e instalación que deje de funcionar y cuyo funcionamiento o mantenimiento recaiga en su ámbito de responsabilidad.

## 7. Suspensión temporal o total por impago.

El retraso en el pago en la Renta u otras cantidades, total o parcial, por parte de la Arrendataria de las cantidades adeudadas y por un plazo superior a un (1) mes desde la fecha de pago indicada en la Condición General 4, así como en su caso, de los conceptos aparte, dará derecho a la Arrendadora, previo aviso a la Arrendataria, a suspender y resolver el Contrato de Habitación y solicitar la inmediata entrega de la Habitación y el pago de las cantidades pendientes.

La Arrendadora notificará la suspensión y/o resolución arriba referidos mediante una comunicación a la Arrendataria que se practicará con al menos tres (3) días de antelación a la fecha en que vaya a tener lugar la suspensión o resolución. En la misma comunicación la Arrendadora incluirá la fecha en que, de no efectuarse el pago, se procederá a la suspensión o resolución, que no podrá llevarse a cabo en día inhábil.

En caso de no llevar a cabo el pago una vez requerida la Arrendataria, dará lugar a la consiguiente resolución definitiva del Contrato de Habitación y la obligación de devolución de la Habitación por la Arrendataria.

## 8. Cambio de Habitación o edificio

A los efectos de conservar el espíritu del presente Contrato de Habitación, que es el de arrendamiento y uso de una Habitación dentro de un piso compartido por parte de diversas personas y para el caso de que el piso donde se encuentre la Habitación objeto del presente Contrato de Habitación esté ocupado por menos del 50% de su capacidad, la Arrendadora queda facultada para sustituir la Habitación arrendada por otra en el mismo edificio u otro edificio en el que se encuentre una Habitación en similares o superiores condiciones, entendiendo que el criterio de determinación de dicho concepto de igualdad o superioridad vendrá determinado por la superficie de la Habitación cuyo uso exclusivo se adjudicará a la Arrendataria. En el caso de sustitución del inmueble, el nuevo se hallará en el mismo barrio. Y para la aplicación de dicho cambio, la Arrendadora vendrá obligada a comunicarlo a la Arrendataria con diez (10) días naturales de antelación al traslado, corriendo la Arrendadora con el coste del mismo y con la previa exhibición del inmueble y Habitación a la Arrendataria. Esta facultad podrá ejercitarse por la Arrendadora una sola vez durante la vigencia del Contrato de Habitación, salvo acuerdo con la parte Arrendataria. En el supuesto de que, exhibida la habitación de substitución, no resultare del agrado de la Arrendataria, ésta podrá resolver el arrendamiento, sin penalización para ninguna de las Partes, antes de la fecha prevista para el traslado.

## 9. Obras

La Arrendataria no podrá realizar ningún tipo de obras en el piso o habitación sin el previo consentimiento por escrito de la Arrendadora.

Se prohíbe expresamente alterar la pintura o instalar cualquier objeto que modifique las condiciones y diseño de la habitación.

Se prohíben los agujeros en cualquier pared, techo o suelo.

## 10. Mantenimiento y reparaciones

La Arrendataria declara que conoce las características y el estado de las instalaciones de la Habitación, así como del mobiliario y el inventario, que acepta expresamente, comprometiéndose a mantenerlos en perfectas condiciones y a hacer un uso conforme al objeto, incluyendo las puertas, cerraduras, ventanas, zonas comunes, todo tipo de instalaciones, y deberá devolvérselos a la Arrendadora en las mismas condiciones cuando finalice el presente Contrato de Habitación.

La Arrendataria deberá hacerse cargo de todo gasto que se derive de cualquier daño en la Habitación, su mobiliario, inventario, techos, suelo, cristales e instalaciones debido a su mal uso, bien por su valor de reparación o de reposición a nuevo. 
Respecto a los desperfectos que se originen en las zonas comunes del piso, su coste de reparación o reposición a nuevo irá a cargo del causante. En caso de desconocer el responsable, este importe se repartirá entre todos los ocupantes del piso. Las facturas de reparaciones de dispositivos del piso arrendado (caldera, sistemas de calefacción, electrodomésticos en general) provocadas por un mal uso o por un deficiente mantenimiento por parte de los ocupantes, se repercutirán al causante directo del mismo o, en caso en que no se pueda individualizar, se repercutirá a todos los ocupantes del piso de forma proporcional. 

La Arrendataria es responsable, no sólo de sus propios actos, sino también de los de aquellos a los que invite al piso o Habitación. 

## 11. Garantía

La Arrendataria abonará a la Arrendadora, en el momento y cuantía indicada en las Condiciones Particulares, la Garantía para atender y hasta donde alcance, las obligaciones económicas derivadas del Contrato de Habitación. 

Las Partes aceptan expresamente que, en caso de resolución anticipada del Contrato de Habitación por el Arrendatario antes del Plazo acordado y sin cumplir el preaviso, no dará derecho a la Arrendataria a la devolución del importe de la Garantía, que quedará en poder de la parte Arrendadora en concepto de daños y perjuicios.

La Garantía le será rembolsada a la Arrendataria en el plazo de treinta (30) días a contar de la devolución de las llaves y por tanto entrega de la Habitación a la Arrendadora con su mobiliario e inventario, en la forma indicada en el presente Contrato de Habitación y siempre que no se adeude cantidad por concepto alguno. En caso contrario, le será descontado de la Garantía. 
La Garantía no sustituirá en ningún caso al pago de la última mensualidad, pudiendo ésta ser incautada en su totalidad en caso de impago de cualquier importe de Renta.

Si una vez finalizado el Contrato de Habitación la Arrendataria no rellena y facilita a la gestora o la propiedad, en el plazo máximo de veinte (20) días naturales contados desde la fecha de finalización contractual, los datos requeridos para la devolución de su garantía, se entenderá que renuncia a ella y quedará en poder de la Arrendadora sin derecho a reclamación.

La liquidación de daños y deuda que tuviera pendiente la Arrendataria presentada por la Gestora de la propiedad a la Arrendataria será suficiente para acreditar el saldo resultante adeudado por la Arrendataria (saldo deudor) en la fecha de resolución o vencimiento del Contrato de Habitación, a cuyo pago vendrá obligada la Arrendataria.

## 12. Prohibiciones y renuncias

Queda expresamente prohibida la cesión, traspaso o subarriendo total o parcial de la Habitación, así como destinarla a usos distintos del pactado.

La Arrendataria sabe, le consta y acepta que por su propia seguridad el edificio está dotado de cámaras de vigilancia en circuito cerrado. 

La Arrendataria exonera a la Arrendadora de cualquier pérdida, demanda, reclamación, cargo, daño o lesión resultante de la falta de seguridad en el edificio.

La Arrendataria reconoce que la Arrendadora no proporcionará cobertura de seguro para los bienes de la Arrendataria, ni será responsable de la pérdida de sus bienes, ya sea por robo, incendio u otros, ni a las personas que ocupen la Habitación o piso durante la vigencia del Contrato o daños que estas pudieran causar a terceros o las cosas.

La Arrendataria podrá contratar y mantener vigente durante todo el plazo contractual una póliza de seguro que cubra el contenido y la responsabilidad civil de terceros.

La omisión o mora en el ejercicio total o parcial de cualquier derecho por la Arrendadora no constituirá una renuncia que le impida u obstaculice a ejercer los derechos que se derivan del presente Contrato de Habitación. 

La Arrendataria reconoce y acepta expresamente que no le corresponde derecho alguno de tanteo, retracto y/o adquisición preferente en caso de venta del piso donde está la Habitación o del edificio en su totalidad o por partes, renunciando por tanto a cualquier derecho que se pudiera instituir en el futuro.

La Arrendataria renuncia expresamente desde ahora a la reducción o supresión de la renta ante cualquier situación de crisis, alarma, pandemia o similar.

La Arrendataria renuncia expresamente a reclamar cualquier cantidad que, en su caso, le pudiera corresponder de conformidad con la normativa vigente en materia de contención de rentas y demás normativa complementaria aplicable.

## 13. Incumplimiento

El incumplimiento por cualquiera de las Partes de las obligaciones contenidas en el presente Contrato o normativa vigente dará derecho a la parte que hubiere cumplido las suyas a exigir el cumplimiento de la obligación y/o a promover la resolución del contrato de acuerdo con lo dispuesto en el artículo 1.124 del Código Civil Español. La resolución del Contrato de Habitación se producirá si en el plazo de tres (3) días naturales contados desde la notificación enviada a la parte incumplidora, ésta no subsanase el incumplimiento.

Será causa automática de resolución contractual y por lo tanto se deberá hacer entrega de la Habitación por parte de la Arrendataria, en los supuestos en los que ésta incumpla grave y/o reiteradamente las Normas de Uso, o incurriere en responsabilidad penal por delito o falta, ya sea por actos cometidos en el piso, habitación o fuera de ella y de los que sea responsable o colaboradora.

Una vez resuelto el Contrato de Habitación, el retraso en la entrega de la Habitación según la forma aquí acordada supondrá la obligación para la parte Arrendataria de abonar las cantidades y por los conceptos indicados en las Condiciones Generales y Condiciones Particulares.

En caso de rescisión de este Contrato de Habitación por incumplimiento de la Arrendataria o en caso de desistimiento anticipado del Contrato de Habitación por parte de la Arrendataria, salvo preaviso con una antelación mínima de cuarenta y cinco (45) días, no se le devolverá la Garantía. La Arrendataria seguirá obligada a pagar la Renta hasta el final del Plazo contractualmente acordado. Igualmente, y en caso de resolución anticipada (con o sin preaviso), la Arrendataria deberá devolver a la Arrendadora todos los descuentos aplicados por el Plazo inicialmente contratado.

## 14. Devolución de la Habitación.

Coincidiendo con la finalización del Plazo, por cualquier motivo, y en la misma fecha del día de salida, la Arrendataria deberá hacer entrega a la Arrendadora de la posesión de la Habitación, con las llaves, su mobiliario e inventario, todo en perfecto estado, salvo su desgaste natural. 

La Arrendataria deberá llevarse como máximo el día de salida sus propios muebles, enseres y objetos personales. Todo mobiliario, accesorio, enser y objetos personales que permanezcan en la Habitación cuando se devuelva la posesión de ésta se considerará abandonado y por lo tanto pasará a ser propiedad de la Arrendadora sin ningún tipo de compensación a la Arrendataria. 

La Arrendataria deberá devolver de forma inmediata la Habitación cuando así se lo requiera la Arrendadora por las causas previstas en este Contrato.

## 15. Impuestos

Las Partes abonarán los impuestos de los que, en su caso, sean sujetos pasivos conforme a la legislación vigente.

## 16. Nulidad e ineficacia de las cláusulas

En caso de que alguna cláusula o parte de las Condiciones Generales se declare nula o inválida, ésta solo afectará a la cláusula o la parte de esta que haya sido declarada nula o inválida. El resto de las cláusulas permanecerán vigentes y la estipulación o la parte de la estipulación nula o inválida se excluirá.

## 17. Notificaciones

A efectos de recepción de notificaciones, las Partes han designado los domicilios y las direcciones de correo electrónico indicados en las Condiciones Particulares.

## 18. Derecho aplicable 

El Contrato de Habitación se regirá en primer lugar por la voluntad de las Partes reflejadas en las Condiciones Particulares, Condiciones Generales y Normas de Uso y, en su defecto, por lo dispuesto en los artículos 1.542 a 1582 y artículos 523 a 529 del Código Civil Español.

## 19. Idioma

El presente Contrato de Habitación y sus condiciones se redactan en idioma español, que prevalecerá en sobre cualquier otro. Los documentos que tengan que ser traducidos a un idioma distinto del español serán abonados por la parte que lo solicite.

## 20. Jurisdicción

Para resolver cualquier disputa derivada del Contrato de Habitación, las Partes se someterán a la jurisdicción de los juzgados y tribunales de Barcelona (España).

## 21. Vinculación con las Condiciones Particulares

Las Condiciones Generales están vinculadas necesariamente con las Condiciones Particulares y juntamente conforman el Contrato de Habitación. Tanto las condiciones Particulares como las Condiciones Generales constan en la página web de la Gestora y la Propietaria, se completan mutuamente, siendo ambas de obligado cumplimiento.

## 22. Protección de datos

Ambas Partes tratarán los datos personales de los representantes, así como del resto de personas que intervengan en la relación jurídica con la finalidad de cumplir con los derechos y obligaciones contenidas en este contrato y en las disposiciones que establece la normativa vigente en materia de protección de datos (LOPDGDD), para poder prestar el servicio contratado. El tratamiento de dichos datos queda legitimado por la ejecución del presente Contrato de Habitación. 

Los datos proporcionados se conservarán mientras se mantenga la relación comercial o durante el tiempo necesario para cumplir con las obligaciones legales y atender las posibles responsabilidades que pudieran derivar del cumplimiento de la finalidad para la que los datos fueron recabados. Los datos no se cederán a terceros salvo en los casos en que exista una obligación legal. Asimismo, no se realizan transferencias internacionales de datos.

Los interesados podrán ejercer sus derechos de acceso, rectificación, supresión de datos, así como solicitar la portabilidad de los datos, que se limite el tratamiento o a oponerse al mismo, mediante escrito a cada una de las partes a través de la dirección mencionada en el encabezamiento del contrato. Asimismo, los interesados tendrán derecho a presentar una reclamación ante la Agencia Española de Protección de Datos.

## 23. Aceptación

La aceptación sin reservas de las presentes Condiciones Particulares, Condiciones Generales y Normas de Uso deviene obligatoria para la suscripción del presente Contrato de Habitación por parte de la Arrendataria. 

La Arrendataria manifiesta haber leído y entendido las Condiciones Particulares, Condiciones Generales y Normas de Uso que han sido puestas a su disposición, en todo momento, con carácter previo a la contratación y aceptarlas todas ellas sin objeción alguna.

| | |
|:-|:-|
|**El Arrendador**|**El Arrendatario**|
{%-for s in Owner_signers-%}
|&nbsp; | |
|&nbsp; | |
|&nbsp; | |
|&nbsp; | |
|&nbsp; | |
|Fdo: {{s.Owner_signer_name}}|{%if loop.index==1%}Fdo: {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_name}}{%endif%}|
{%-endfor-%}





<div style="page-break-after: always;"></div>

# NORMAS DE USO


1. Las visitas de amigos o familiares se recibirán en el piso con el consentimiento de los demás arrendatarios. Será responsabilidad de los arrendatarios informar a sus compañeros de piso de las visitas que quieran recibir. Los invitados no se pueden quedar a pasar la noche en el piso o Habitación bajo ningún concepto.

2. No se podrá utilizar otra habitación diferente de la contratada.

3. Cada arrendatario responde no solo por sus propios actos, sino también por los actos de aquellos a quien invite o introduzca en el piso.

4. Los arrendatarios respetarán las normas de convivencia de vecinos como uno más, y deberán cumplir con la normativa sobre ruidos. Por respeto al descanso de los demás residentes, a partir de las 22:00 horas deberá cesar cualquier tipo de ruido que pueda impedir su descanso o el de los demás vecinos, evitando, en especial, el uso de la lavadora y secadora u otros aparatos que produzcan ruido excesivo de acuerdo con la normativa municipal en vigor.

5. No están permitidas las fiestas en el piso, Habitación ni en las zonas comunes del edificio.

6. No está permitido introducir a personas ajenas al piso en el horario entre las 22:00 y las 08:00.

7. Se respetará como norma del Contrato de Habitación el tiempo de estudio y trabajo así como el de la noche. Se consideran normas del Contrato de Habitación los criterios de convivencia razonable que los arrendatarios decidan por mayoría, como la distribución de las tareas domésticas, tales como bajar la basura, limpiar la cocina, fregar los útiles de cocina, etc. La basura deberá bajarse diariamente a los contenedores habilitados más cercanos así como los puntos de reciclaje.

8. No se pueden utilizar ni consumir alimentos ni útiles de otros arrendatarios sin su permiso.

9. En el horario nocturno que va de las 11:00 horas a las 07:00 horas se apagarán todas las luces de las zonas comunes del piso.

10. Los arrendatarios respetarán la decoración de la vivienda y, salvo autorización expresa de la Arrendadora o la Gestora, no introducirán otros muebles u objetos en la misma. No está permitido clavar ni pegar objetos en las paredes (clavos, alcayatas, tacos, adhesivos, blue tac, etc.).

11. Se mantendrán despejadas y ordenadas las zonas comunes de la vivienda, especialmente para el mantenimiento adecuado. 

12. Queda prohibido el depósito de vehículos de transporte personal en el piso y las zonas del edificio que no hayan sido expresamente designadas para ello. 

13. Se deben mantener las condiciones mínimas de orden y se deberá facilitar el acceso al personal de limpieza en el día y horario estipulado.

14. La Arrendadora no responde por los robos y deterioros de los bienes y enseres depositados por los arrendatarios o sus invitados en la Habitación, piso o las zonas comunes del edificio.

15. Está prohibido fumar en el interior del edificio, el piso o la Habitación.

16. No está permitido encender velas o incienso en el piso o las habitaciones.

17. No se pueden introducir ni tener plantas ni animales en la Habitación, piso o zonas comunes del edificio.

18. No está permitida la tenencia de armas, explosivos, ni el consumo de cualquier tipo de drogas, estupefacientes, ni el consumo abusivo de bebidas alcohólicas. Tampoco está permitida la ostentación de material ofensivo que atente contra la dignidad, igualdad y sensibilidad común de las personas a fin de combatir el racismo, la discriminación racial, la xenofobia y otras formas de intolerancia, así como los incidentes y delitos de odio. 

19. La falta de respeto u comentarios ofensivos hacia el personal de mantenimiento y demás equipo de la Gestora tendrá la consideración de falta grave y por si sola puede suponer la expulsión de la persona que la haya cometido.

20. Cualquier comportamiento violento o agresivo en cualquier caso, tendrá la consideración de falta muy grave y por si sola puede suponer la expulsión de la persona que la haya cometido.

21. La Arrendataria será la única responsable del uso que haga del servicio de internet, comprometiéndose a realizar un uso adecuado del mismo. En caso contrario la Arrendadora quedará facultada para interrumpir el servicio y facilitar a las autoridades correspondientes los datos personales que se le soliciten acerca de los responsables.

22. No se pueden arrojar al retrete, lavamanos o ducha productos que atascan las tuberías y contaminan el agua, como son las toallitas higiénicas, algodón, tiritas, hilo dental, compresas, cabello, colillas, preservativos, etc., Sólo se puede arrojar por el retrete papel higiénico fabricado especialmente para ese uso. El coste de los desatascos necesarios por no respetar esta norma será por cuenta de los arrendatarios responsables al considerarse el atasco consecuencia del mal uso. Lo mismo aplica a los atascos originados en la cocina por arrojar comida en los desagües de los fregaderos o por arrojar medicamentos, los aceites vegetales, lejía, amoniaco, pinturas y disolventes, pesticidas e insecticidas, jabones y detergentes y tratamientos anti-cal que contaminan el agua

23. La reposición de los consumibles del piso o habitación (por ejemplo, papel higiénico, bolsas de basura, jabón, etc.) serán por cuenta y cargo de la Arrendataria.

24. Los trabajos de desatasco de lavabos, duchas, limpieza de filtros en electrodomésticos, etc. serán a cargo y cuenta de la Arrendataria cuando sean debidos a un mal uso o negligencia. Si no se puede individualizar se cobrarán de forma proporcional a todos los arrendatarios.

25. No se permite la utilización de estufas, hornillos u otros electrodomésticos dentro de las Habitaciones, recayendo sobre la Arrendataria cualquier responsabilidad que pudiera derivarse del uso de estos.

26. No se permite la instalación de aparatos de climatización adicionales de los que ya está dotado el piso o habitación y salvo autorización previa de la Arrendadora o su Gestora. 

27. La pérdida de llaves y su restitución tiene un coste de 100 euros (IVA incluido) por llave. Dicho coste podrá incrementarse en casos de pérdidas reiteradas.

28. El desplazamiento de personal de la Gestora al piso o Habitación por motivos injustificados o de negligencia de la Arrendataria supondrá el pago de 50 euros (IVA incluido) por parte de dicha Arrendataria.

| | |
|:-|:-|
|**El Arrendador**|**El Arrendatario**|
{%-for s in Owner_signers-%}
| | |
|![firma]({{Server}}/signature/{{s.Owner_signer}})| |
|Fdo: {{s.Owner_signer_name}}|{%if loop.index==1%}Fdo: {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_name}}{%endif%}|
{%-endfor-%}

