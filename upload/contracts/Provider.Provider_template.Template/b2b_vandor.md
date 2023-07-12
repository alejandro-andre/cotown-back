# CONTRATO DE ARRENDAMIENTO



En Barcelona, a {{Today_day}} de {{Today_month|month}} de {{Today_year}}


## LAS PARTES

{%if Rooms[0].Owner_id_type=='CIF'%}
De una parte, {%for s in Rooms[0].Owner_signers%}{%-if loop.index>1%} y {%endif%}{{s.Owner_signer_name}}, mayor de edad, provisto de {{s.Owner_signer_id_type}} {{s.Owner_signer_id}}{%endfor%}, con domicilio profesional en {{Rooms[0].Owner_address}}, {{Rooms[0].Owner_zip}} {{Rooms[0].Owner_city}}, actuando en nombre y representación de {{Rooms[0].Owner_name}} con el mismo domicilio, {{Rooms[0].Owner_id_type}} {{Owner_id}}{%if Owner_signers|length>1%}, en calidad de apoderados mancomunados{%endif%}.
{%else%}
De una parte, {{Rooms[0].Owner_name}}, mayor de edad, con {{Rooms[0].Owner_id_type}} núm. {{Rooms[0].Owner_id}}, con domicilio profesional en {{Rooms[0].Owner_address}}, {{Rooms[0].Owner_zip}} {{Rooms[0].Owner_city}} actuando en su nombre y representación.
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

En adelante, LA "ARRENDADORA" y LA "ARRENDATARIA" serán referidas conjuntamente como las "Partes" y cualquiera de ellas, separadamente, como una "Parte".

Todas las partes intervienen y actúan en su propio nombre y representación.

Los comparecientes tienen, según se reconocen recíprocamente, la capacidad jurídica bastante y necesaria, tanto personal como representativa, para el otorgamiento del presente contrato de arrendamiento y, 


## EXPONEN

I. Que, la Arrendadora es propietaria de la siguiente finca: 

- Calle:  {{Rooms[0].Resource_flat_address}}
- Ciudad: {{Rooms[0].Resource_building_city}}
- Piso/s: {{Flats}}

(en adelante conjuntamente los "pisos" e individualmente el "piso")

II. Que, la Arrendataria es una organización/entidad interesada en arrendar el piso o los pisos de forma temporal y para ser ocupados exclusivamente por parte de las personas que se identificarán en el cuerpo de este documento.
 
III. Que la gestión del presente contrato y, por lo tanto, la representación de la Propiedad durante todo el plazo que dure el presente será llevada a cabo por la compañía Cotown Sharing Life, S.L. (la gestora).

IV. Y, estando ambas partes interesadas en el arrendamiento de conformidad con los términos que seguidamente se convienen, suscriben el presente contrato de arrendamiento, de conformidad con las siguientes,


## ESTIPULACIONES

## 1.- OBJETO DEL CONTRATO DE ARRENDAMIENTO

1.1.- La Arrendadora cede en arrendamiento a la Arrendataria el piso o los pisos que se indican a continuación, por el plazo y precio indicados en los siguientes pactos (en adelante el "Contrato de arrendamiento"). 

{%for r in Rooms-%}
- {{r.Resource_flat_street}}- {{r.Resource_address}}
{%endfor%}

1.2.- Los pisos se entregarán libres de arrendatarios y ocupantes, con la extensión, usos, circunstancias y estado físico que la Arrendataria declara conocer y aceptar expresamente. 

1.3.- Cada piso se destinará de forma exclusiva como arrendamiento de temporada por parte de las personas cuyos nombres, datos de identificación y habitaciones asignadas en cada piso constarán como anexo I al presente documento. 

La Arrendataria hará cumplir a los ocupantes que designe. las obligaciones aquí contenidas y la normas de uso, haciéndose responsable la Arrendataria en caso de incumplimiento, lo cual acepta. La Arrendataria no podrá modificar el destino de los pisos ni las personas que hagan uso de cada habitación según consta en los anexos al presente, todo ello sin la previa novación por escrito del Contrato de arrendamiento.

1.4.- El uso de las habitaciones otorga el uso de los servicios comunes y los suministros de los que están dotadas (agua, gas, electricidad e internet). 

1.5.- Todas las habitaciones disponen de un armario, una silla, una cama o dos para su uso por una sola persona, iluminación y disponen de calefacción, electricidad, internet y servicio de agua corriente.

Los pisos tienen el inventario que se adjuntará a la entrega de cada piso como anexo al presente.

## 2.- DURACIÓN

2.1.- El arrendamiento del piso o pisos se pacta por temporada y por tanto por el tiempo determinado, común y de obligado cumplimiento, plazo este que empezará a contar desde el {{Booking_date_from_day}}/{{Booking_date_from_month}}/{{Booking_date_from_year}} y finalizará el {{Booking_date_to_day}}/{{Booking_date_to_month}}/{{Booking_date_to_year}}. 

2.2.- Llegada la fecha final del arrendamiento, la Arrendataria dejará libre y a disposición de la Arrendadora el piso o los pisos, sin necesidad de preaviso alguno, haciendo entrega de cada piso  e inventario en perfecto estado, así como de todos los juegos de llaves, todo lo cual quedará recogido en el acta de entrega. 

2.3.- Coincidiendo con el día de entrega de cada piso, la Arrendataria entregará a la Arrendadora los juegos de llaves de portería y piso. En caso de pérdida o extravío de las llaves, la Arrendataria deberá abonar el coste de reposición de 100 euros por cada llave o juego de llaves completo, según sea el caso, y para cada habitación de cada piso.
  
## 3.- PRECIO Y CONCEPTOS DEL ARRENDAMIENTO

3.1.- En atención a la reserva de todos los pisos, la Arrendataria se obliga al íntegro pago del total precio del arrendamiento durante todo el plazo indicado en el pacto 2, el cual las partes establecen de conformidad con lo siguiente:

El precio de alquiler mensual se determina en base al precio por plaza/cama que se pone a disposición para la Arrendataria. El número de plazas/camas una vez entregadas a la Arrendataria no podrá ser objeto de modificación o reducción hasta la finalización del contrato salvo acuerdo expreso y escrito de ambas partes.

El precio acordado y negociado por las partes por el presente contrato de arrendamiento se establece en base una tarifa de {{Booking_rent|decimal}} euros al mes (sin impuestos) por cada cama/plaza disponible en cada piso objeto de alquiler según quedará recogido en el anexo indicado en el anterior punto 1.1.

El pago de la renta a la que venga obligada al pago la Arrendataria en cada momento así como de cuantas obligaciones económicas deriven de este Contrato será satisfecha por la Arrendataria por mensualidades anticipadas y dentro de los cinco (5) primeros días de cada mes. La Arrendataria autoriza a que, para el cobro de las mensualidades, la Arrendadora realice, entre los días 1 a 5 de cada mes, un cargo en la cuenta bancaria de la Arrendataria número {{Customer_bank_account}}.

La Arrendadora tendrá que expedir y librar a la Arrendataria la factura correspondiente de cada pago, que se realizará a través del sistema bancario.

La Arrendataria autoriza en este acto a la Arrendadora, para que desde esta fecha y con carácter indefinido, en tanto este vigente el presente contrato de alquiler, a que gire en el número de cuenta bancaria antes especificado, todos los recibos correspondientes a las facturas que se originen como consecuencia de la relación contractual entre ambas sociedades, según lo exigido por la Ley 16/2009, de Servicios de Pago.

La obligación del pago de la renta subsistirá, aunque haya finalizado el Contrato, hasta que se devuelvan todos los pisos y las instalaciones a la Arrendadora, sin que esto suponga prórroga de ningún tipo, sino cobro de la renta como indemnización por ocupación no consentida. 

3.3.- El impago de la renta o de cualquier cantidad por la que la Arrendataria venga obligada a su pago devengará el interés legal del dinero incrementado en tres puntos.

3.4.- En cuanto al pago del consumo de los suministros, las partes pueden optar entre el 3.4.1 o el 3.4.2:

3.4.1 Los servicios de electricidad, agua, gas y demás suministros individuales serán de cuenta y cargo exclusivo de la Arrendataria, debiendo estar domiciliados en su cuenta en la fecha de entrega de la posesión de los pisos. Para ello, la Arrendadora autoriza expresamente en este acto a la Arrendataria desde ahora y para entonces a cambiar la titularidad de los contratos y a domiciliar los recibos. A la finalización del contrato, la domiciliación y/o titularidad de dichos suministros será cambiada nuevamente a la parte Arrendadora sin que estos sean dados de baja. 

En caso de que, una vez finalizado el arrendamiento, la parte Arrendataria diera de baja alguno de los suministros de agua, electricidad o gas sin autorización de la Arrendadora, se penalizará a la Arrendataria con el pago de la cantidad efectivamente reclamada por la compañía suministradora para su alta y por cada suministro dado de baja. Entregado el piso efectivamente a la Arrendadora, esta deberá gestionar el cambio de los suministros en el plazo máximo de treinta días.

3.4.2 Los consumos de los suministros de agua, gas y electricidad de cada piso, tienen un límite máximo de consumo mensual incluido en el importe de la renta, resultante de sumar la cantidad de 60 euros mensuales por cada habitación que tenga cada piso. Dicho importe en euros se calcula para cada mes y mediante la suma de las tres facturas de suministros (Agua, gas y electricidad). Excedido dicho importe mensual máximo de consumo por piso expresado en euros, el exceso se cobrará a la Arrendataria y se le pasará el cargo al cobro dentro de la factura mensual de Renta pero como concepto aparte. 

Será a cargo de la Arrendadora el pago de las tasas por recogida de basuras, cuota anual del IBI y wi-fi. 

Será de cuenta de la Arrendataria cualquier otra que se pueda instaurar por el Ayuntamiento en un futuro, aunque se giren a nombre de la Arrendadora.

3.5.- El precio del alquiler incluye los gastos de limpieza de los espacios comunes dentro de los pisos, así como el mantenimiento de todos los pisos que será llevado a cabo por la Arrendataria de forma regular a fin de mantener un correcto estado de limpieza, orden y buen funcionamiento de los pisos y su mobiliario. La propiedad solo llevará a cabo la limpieza de las zonas comunes del edificio.

## 4.- CLÁUSULA FISCAL 

4.1.- Resultará aplicable la exención de pago del I.V.A. prevista en el artículo 20. Uno. 23º. b) de la Ley 37/1992, de 28 de diciembre del Impuesto sobre el Valor Añadido, por cuanto el piso  constituirá la vivienda temporal de las personas designadas por la Arrendataria, cuyos nombres y datos de identificación constan en el anexo, siendo el destino del inmueble el uso exclusivo como vivienda según ha quedado definido en el pacto primero anterior.

## 5.- GARANTÍA

5.1.- Garantía. La Arrendadora girará a la firma del presente contrato de alquiler y a la cuenta corriente de la Arrendataria indicada en el pacto cuarto anterior, el importe de la garantía consistente en la cantidad de {{Booking_deposit|decimal}} euros (la "Garantía") a lo cual le autoriza la Arrendataria.

Se hace constar expresamente, y así se acepta al suscribirse el presente contrato, que si se produce una baja voluntaria la Arrendataria no tendrá derecho a la devolución del importe de la Garantía.

La garantía se mantendrá en vigor durante todo el contrato y se podrá aplicar al pago de cualquier cantidad adeudada por la Arrendataria o las responsabilidades económicas asumidas por la Arrendataria por el presente contrato y por cualquiera de los pisos sin distinción entre estos.

## 6.- RENUNCIAS.

6.1.- Con expresa renuncia a lo dispuesto en la normativa vigente, las partes acuerdan que la Arrendataria no podrá en modo alguno subarrendar, ceder o traspasar los derechos de este Contrato de arrendamiento a terceros. 

La Arrendataria solo podrá hacer el uso que se indica en el pacto primero de este documento. 
 
En el supuesto de que la Arrendataria incumpliera esta obligación, podrá la Arrendadora resolver el presente Contrato de arrendamiento debiendo la Arrendataria dejar libre y a disposición de la Arrendadora todos los pisos en el plazo máximo de quince días naturales.

6.2.- Con expresa renuncia a lo dispuesto en la normativa vigente, la Arrendataria renuncia expresamente a cualesquiera derechos de adquisición preferente o de tanteo y/o retracto que sobre cualquier piso arrendado y/o derechos que le pudieren corresponder.

6.3.- Con expresa renuncia a los derechos que confiere la normativa vigente, la Arrendataria renuncia expresamente a cualquier derecho a indemnización con motivo de la terminación o resolución anticipada del Contrato de arrendamiento que en su caso le pudieran corresponder.

## 7.- ESTADO FÍSICO DE LOS PISOS Y REPARACIONES

7.1.- La Arrendataria reconoce que ha visitado el edificio, así como el piso o pisos, los cuales han sido recientemente renovados y actualizados, por lo que se entregan en perfecto estado siendo aptos para el destino convenido y estando por tanto a la entera satisfacción de la Arrendataria. 

7.2.- Serán por tanto de cuenta de la Arrendataria los desperfectos y deterioros que se ocasionen en cada piso. 

7.3.- La necesidad de alguna reparación no otorgará a la Arrendataria derecho alguno a la suspensión del Contrato de arrendamiento o a desistir del mismo, ni a indemnización alguna, así como tampoco a reducir o paralizar el pago de la renta.

7.4.- Cualquier situación de crisis sanitaria, alarma, pandemia o similar no supondrá la reducción total o parcial de la renta que deberá ser igualmente abonada, salvo acuerdo expreso de las Partes.

## 8.- OBRAS 

8.1.- Las partes convienen expresamente que queda prohibida la ejecución de cualquier tipo de obras por la Arrendataria salvo autorización expresa y por escrito de la Arrendadora. 

8.2.- Será causa de resolución del presente Contrato de arrendamiento la ejecución por la Arrendataria de obras no autorizadas por la Arrendadora.

## 9.- MANIFESTACIONES Y GARANTÍAS DE LA ARRENDATARIA

9.1.- La Arrendataria se compromete y obliga al abono de cualesquiera cantidades a las que venga obligada a su pago según se contiene en este contrato, así como de la falta de cumplimiento de sus obligaciones por parte de las personas por ella designadas y alojadas.

9.2.- La Arrendataria responderá respecto a los daños o desperfectos que se originen en el edificio o terceros, independientemente del causante de estos, eximiendo de cualquier responsabilidad a la Arrendadora.

9.3.- La liquidación de daños y deuda que tuviera pendiente la Arrendataria y que hubiera sido presentada por la gestora de la Propiedad o la Propiedad a la Arrendataria será suficiente para acreditar el saldo resultante adeudado por la Arrendataria (saldo deudor) en la fecha de resolución del contrato, a cuyo pago vendrá obligada la Arrendataria, pudiendo aplicar la fianza y la garantía indicada en el punto 5.1.

## 10.- GASTOS E IMPUESTOS

La Arrendataria abonará los gastos, cargas o impuestos propios de la total finca en la que se encuentran incluidos los pisos s, repercutiendo en la Arrendataria aquellos que se han hecho constar expresamente en el pacto 3 anterior.

## 11.- CAUSAS DE TERMINACIÓN DEL CONTRATO DE ARRENDAMIENTO

11.1.- El presente Contrato de arrendamiento finalizará al cumplimiento del plazo estipulado en el pacto 2, sin ulterior prórroga ni aplicación de la tácita reconducción.

11.2.- El presente Contrato se resolverá por incumplimiento de cualquiera de las obligaciones contractuales asumidas por la Arrendataria en el presente documento. 

11.3.- Ambas partes acuerdan que en el supuesto de que el arrendamiento se extinguiera por incumplimiento de la Arrendataria o por su desistimiento unilateral antes de la finalización del plazo contractual convenido, la Arrendataria quedará obligada al pago del total importe de la renta pendiente de pago hasta la finalización del plazo contractualmente acordado. 

11.4.- Llegada la fecha de finalización del contrato a su vencimiento, este se entenderá extinguido automáticamente, sin necesidad de preaviso o intimación de una parte a la otra, y sin que sea de aplicación la tácita reconducción recogida en el Artículo 1.566 del Código Civil.

11.5.-En el caso de finalización del contrato por cualquier causa (expiración, extinción, renuncia, rescisión, resolución, etc.), si la Arrendataria no procediese a desocupar todos o alguno de los pisos con la entrega de sus llaves, la Arrendadora podrá exigir por cada día de demora en la entrega de cada piso, y en concepto de cláusula penal no sustitutiva de daños y perjuicios, especialmente aceptada por la Arrendataria, una cantidad equivalente al triple de la renta diaria vigente, con independencia de la obligación legal, en su caso, de satisfacer la renta por el concepto de ocupación no consentida hasta el momento en que la Arrendataria entregue a la Arrendadora cada piso, por cualquiera de los medios legalmente establecidos.

El desalojo de cada uno de los pisos por vía judicial supondrá la obligación de la Arrendataria de pago de los honorarios de abogados y procuradores, tasas y gastos judiciales por el desalojo.

## 12.- OTRAS OBLIGACIONES DEL ARRENDATARIO

Además de las obligaciones contenidas en los párrafos precedentes de este Contrato de arrendamiento, la Arrendataria se obliga a lo siguiente:

a) A no instalar transmisiones, motores, máquinas, etc., que produzcan vibraciones o ruidos molestos para los demás ocupantes del inmueble o de los colindantes, o que pueda afectar la consistencia, solidez o conservación del inmueble
b) A no almacenar manipular en el piso  materias explosivas, inflamables, incómodas, insalubres o estupefacientes, y observar en todo momento las disposiciones vigentes.
c) A permitir el acceso en cada piso, al propietario, gestor y a los operarios o industriales mandados por cualesquiera de ambos, para la realización, inspección y comprobación de cualquier clase de obras o reparaciones que afectan inmueble. La Arrendadora deberá avisar con antelación y la Arrendataria deberá permitir su entrada sin poder oponer motivo alguno. 
d) A cumplir en todo momento las normas de uso internos que están en la web de la propiedad y de la gestora y los acuerdos que la comunidad de propietarios tenga establecidos o establezcan, en orden a la utilización de los servicios, elementos comunes y buen régimen de convivencia.
e) A cumplir y hacer cumplir a los ocupantes de los pisos en cada momento, con la normativa del Ayuntamiento de Barcelona en especial respecto al ruido, horario nocturno y normas de respeto y policía, eximiendo de cualquier responsabilidad a la Propiedad o la Gestora.  
f) Se prohíbe expresamente la tenencia de cualquier animal en la finca arrendada.
g) Se prohíbe expresamente la realización de actividades molestas, insalubres, nocivas, peligrosas o ilícitas.
h) Se prohíbe el uso de internet para actividades ilegítimas o delictivas. 

## 13. ACCESO A LOS PISOS.

La Arrendataria permitirá la entrada en los pisos a la Arrendadora o a cualquier persona designada a tal fin por ésta, a los efectos de verificar el cumplimiento de las obligaciones derivadas del presente Contrato, su estado u otra justa causa.

La Arrendataria permitirá la entrada en los pisos de la Arrendadora acompañada de arquitectos, técnicos y demás profesionales que intervengan en cualquier proceso de reparación.

De igual manera, la Arrendataria permitirá la entrada en los pisos de la Arrendadora acompañada de potenciales clientes interesados en la compra de los pisos, de todo el edificio o partes de éste.

La Arrendataria permitirá a la Arrendadora la colocación de rótulos en la fachada de éste, para el alquiler o venta de los pisos o edificio siempre que se ajusten a la normativa vigente. 

Dichas visitas serán señaladas previamente, y evitarán causar perjuicio en la actividad de la Arrendataria, salvo en casos de urgencia o necesidad, que se podrán llevar a cabo de forma inmediata.

## 14. SEGUROS

La Arrendataria se compromete a tener asegurado lo que es objeto de arrendamiento, junto con sus instalaciones, mobiliario, etc. durante toda la vigencia del presente Contrato, por los riesgos que puedan derivarse de su actividad que incluirá la responsabilidad civil frente a terceros y frente a la Arrendadora, por importe suficiente para cubrir cualquier responsabilidad bien directa como indirecta derivada de las personas que ocupen los pisos o aquellas que sean se encuentre eventual o transitoriamente en los mismos. Las pólizas contratas por la Arrendataria deberán incluir los riesgos por incendios o así como una póliza de responsabilidad civil completa.

La Arrendataria entregará copia de dichas pólizas de seguro a la Arrendadora, así como copia de los recibos de pago de las mismas.

El incumplimiento de la obligación del pago de estas primas, o la insuficiencia en el capital asegurado por las pólizas será causa de resolución del arrendamiento.

## 15.- PROTECCIÓN DE DATOS 

Ambas partes tratarán los datos personales de los representantes, así como del resto de personas que intervengan en la relación jurídica con la finalidad de cumplir con los derechos y obligaciones contenidas en este Contrato de arrendamiento y en las disposiciones que establece la normativa vigente en materia de protección de datos (LOPDGDD), para poder prestar el servicio contratado. El tratamiento de dichos datos queda legitimado por la ejecución del presente Contrato de arrendamiento.
 
Los datos proporcionados se conservarán mientras se mantenga la relación comercial o durante el tiempo necesario para cumplir con las obligaciones legales y atender las posibles responsabilidades que pudieran derivar del cumplimiento de la finalidad para la que los datos fueron recabados. Los datos no se cederán a terceros salvo en los casos en que exista una obligación legal. Asimismo, no se realizan transferencias internacionales de datos.
 
Los interesados podrán ejercer sus derechos de acceso, rectificación, supresión de datos, así como solicitar la portabilidad de los datos, que se limite el tratamiento o a oponerse al mismo, mediante escrito a cada una de las partes a través de la dirección mencionada en el encabezamiento del Contrato de arrendamiento. Asimismo, los interesados tendrán derecho a presentar una reclamación ante la Agencia Española de Protección de Datos. 

## 16.- NOTIFICACIONES

16.1.- A efectos de recepción de notificaciones, las Partes han designado los domicilios indicados al principio, y las direcciones de correo electrónico que se indican a continuación siempre que quede constancia de su recepción por algún medio.

- La Arrendadora en la dirección de correo electrónico: hola@cotown.com 

- La Arrendataria en la dirección de correo electrónico: {{Customer_email}}

16.2.- Las Partes podrán variar las direcciones que figuran en el apartado anterior, comunicándolo a la otra Parte por escrito, en la forma indicada en el apartado inmediatamente anterior.

## 17.- DERECHO APLICABLE, IDIOMA Y JURISDICCIÓN COMPETENTE 

17.1.- Derecho aplicable 

Este Contrato de arrendamiento por temporada se regirá por la voluntad de las partes, en su defecto, por lo dispuesto en los artículos 1.546 y siguientes del Código Civil y, en especial, por lo previsto en el artículo 20. Uno. 23º. b) de la Ley 37/1992, de 28 de diciembre del Impuesto sobre el Valor Añadido en cuanto a la exención de pago del I.VA.

17.2.- Idioma

El presente Contrato de arrendamiento se redacta en idioma español. Los documentos que tengan que ser traducidos a un idioma distinto del español serán abonados por la parte que lo solicite.

17.3.- Jurisdicción

Para resolver cualquier interpretación o disputa derivada del presente Contrato de arrendamiento, las partes se someterán a la jurisdicción de los juzgados y tribunales de la ciudad de Barcelona con renuncia a su propio fuero si fuese el caso.

Y, habiendo leído y comprendido la totalidad del presente Contrato de arrendamiento, lo firman en prueba de aceptación y conformidad, por duplicado ejemplar y a un solo efecto, en el lugar y la fecha indicados en el encabezado.

| | |
|:-|:-|
|**El Arrendador**|**El Arrendatario**|
{%-for s in Rooms[0].Owner_signers-%}
| | |
|![firma]({{Server}}/signature/{{s.Owner_signer}})| |
|Fdo: {{s.Owner_signer_name}}|{%if loop.index==1%}Fdo: {%if Customer_gender=='H'%}D.{%elif Customer_gender=='M'%}Dª.{%else%}D./Dª.{%endif%} {{Customer_name}}{%endif%}|
{%-endfor-%}