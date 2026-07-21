# ###################################################
# CRM
# ---------------------------------------------------
# Envía las reservas encoladas en Booking.Booking_lead
# a Pipedrive (persona + lead + negocio)
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
import json

# Cotown includes
from library.services.pipedrive import add_info, DEFAULTS_BOOKING

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Constants
# ###################################################

# Número máximo de reintentos por reserva
MAX_ATTEMPTS = 5

# Marca (Auxiliar.Segment del edificio) -> opción 'brand'/'web' de Pipedrive.
# Si el nombre del segmento ya coincide con la opción, no hace falta entrada aquí.
BRANDS = {
}

# Booking.Booking_channel -> opción 'channel' de Pipedrive (Marketplace | Directo)
CHANNELS = {
}

# Booking.Booking_referral -> opción 'subchannel' de Pipedrive
# (RRSS | Web | Mail | WhatsApp | Ofi | Teléfono | Referral)
SUBCHANNELS = {
}


# ###################################################
# Reservas pendientes de enviar al CRM
# ###################################################

SQL_PENDING = '''
  SELECT
    bl.id                                             AS "Row_id",
    bl."Booking_id",
    bl."Event",
    b."Company",
    b."Comments",
    b."Reason_id",
    TO_CHAR(b."Request_date", 'YYYY-MM-DD')           AS "Request_date",
    TO_CHAR(b."Date_from", 'YYYY-MM-DD')              AS "Date_from",
    TO_CHAR(b."Date_to", 'YYYY-MM-DD')                AS "Date_to",
    COALESCE(b."Rent", 0) + COALESCE(b."Services", 0) AS "Budget",
    c."Name",
    c."Email",
    c."Phones",
    c."Lang",
    c."Gender_id",
    TO_CHAR(c."Birth_date", 'YYYY-MM-DD')             AS "Birth_date",
    co."Name"                                         AS "Nationality",
    bu."Code"                                         AS "Building",
    se."Name"                                         AS "Brand",
    l."Name"                                          AS "City",
    COALESCE(rpt."Code", rft."Code")                  AS "Place_type",
    bc."Name"                                         AS "Channel",
    br."Name"                                         AS "Subchannel"
  FROM "Booking"."Booking_lead" bl
    INNER JOIN "Booking"."Booking" b   ON b.id  = bl."Booking_id"
    INNER JOIN "Customer"."Customer" c ON c.id  = b."Customer_id"
    LEFT JOIN "Building"."Building" bu ON bu.id = b."Building_id"
    LEFT JOIN "Auxiliar"."Segment" se  ON se.id = bu."Segment_id"
    LEFT JOIN "Geo"."District" d       ON d.id  = bu."District_id"
    LEFT JOIN "Geo"."Location" l       ON l.id  = d."Location_id"
    LEFT JOIN "Geo"."Country" co       ON co.id = c."Nationality_id"
    LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = b."Place_type_id"
    LEFT JOIN "Resource"."Resource_flat_type" rft  ON rft.id = b."Flat_type_id"
    LEFT JOIN "Booking"."Booking_channel" bc  ON bc.id = b."Booking_channel_id"
    LEFT JOIN "Booking"."Booking_referral" br ON br.id = b."Booking_referral_id"
  WHERE bl."Sent_at" IS NULL
    AND bl."Attempts" < %s
  ORDER BY bl.id
'''

SQL_SENT = '''
  UPDATE "Booking"."Booking_lead"
  SET "Sent_at"   = NOW(),
      "Attempts"  = "Attempts" + 1,
      "Error"     = NULL,
      "Person_id" = %s,
      "Lead_id"   = %s,
      "Deal_id"   = %s,
      "Payload"   = %s
  WHERE id = %s
'''

SQL_ERROR = '''
  UPDATE "Booking"."Booking_lead"
  SET "Attempts" = "Attempts" + 1,
      "Error"    = %s
  WHERE id = %s
'''


def q_pending_leads(dbClient, con):

  cur = dbClient.execute(con, SQL_PENDING, (MAX_ATTEMPTS,))
  leads = [dict(row) for row in cur.fetchall()]
  cur.close()
  return leads


# ###################################################
# Datos de la reserva -> datos de Pipedrive
# ###################################################

def prepare(lead):

  # Nombre de pila y apellidos
  name = (lead['Name'] or '').strip()
  first_name, _, last_name = name.partition(' ')

  return {
    'first_name':  first_name,
    'last_name':   last_name,
    'email':       lead['Email'],
    'phone':       lead['Phones'] or '',
    'birth_date':  lead['Birth_date'],
    'nationality': lead['Nationality'] or '',
    'gender':      str(lead['Gender_id']) if lead['Gender_id'] else '',
    'language':    lead['Lang'],
    'comments':    lead['Comments'] or '',

    'type':        'B2B' if lead['Company'] else 'B2C',
    'channel':     CHANNELS.get(lead['Channel'], lead['Channel']),
    'subchannel':  SUBCHANNELS.get(lead['Subchannel'], lead['Subchannel']),
    'brand':       BRANDS.get(lead['Brand'], lead['Brand']),
    'web':         BRANDS.get(lead['Brand'], lead['Brand']),
    'reason':      str(lead['Reason_id']) if lead['Reason_id'] else None,

    'city':        lead['City'],
    'building':    lead['Building'],
    'place_type':  lead['Place_type'],
    'date_from':   lead['Date_from'],
    'date_to':     lead['Date_to'],
    'budget-max':  int(lead['Budget']) if lead['Budget'] else None,

    'created_date': lead['Request_date'],
  }


# ###################################################
# Do one lead
# ###################################################

def do_crm(dbClient, con, lead):

  # Debug
  logger.debug(lead)

  # Datos para Pipedrive
  data = prepare(lead)

  # Sin email no hay persona que crear ni con la que deduplicar
  if not data['email']:
    dbClient.execute(con, SQL_ERROR, ('El cliente no tiene email', lead['Row_id']))
    con.commit()
    logger.error(f"CRM: la reserva {lead['Booking_id']} no tiene email")
    return 0

  # ¡¡¡ Envía a Pipedrive (y correo de notificación) !!!
  try:
    ids = add_info(data, defaults=DEFAULTS_BOOKING)

  # Error: se reintentará en la siguiente pasada del batch
  except Exception as error:
    dbClient.execute(con, SQL_ERROR, (str(error)[:1000], lead['Row_id']))
    con.commit()
    logger.error(f"CRM: error enviando la reserva {lead['Booking_id']}: {error}")
    return 0

  # Entornos sin envío al CRM
  if not ids:
    logger.info(f"CRM desactivado (CRMSEND=0), reserva {lead['Booking_id']} no enviada")
    return 0

  # Marca como enviada
  dbClient.execute(con, SQL_SENT, (
    ids['person_id'],
    str(ids['lead_id']),
    ids['deal_id'],
    json.dumps(data, default=str),
    lead['Row_id']
  ))
  con.commit()
  logger.info(f"CRM: reserva {lead['Booking_id']} enviada, person={ids['person_id']} deal={ids['deal_id']}")
  return 1
