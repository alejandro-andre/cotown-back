# #####################################
# Imports
# #####################################

from sshtunnel import SSHTunnelForwarder
import psycopg2
import psycopg2.extras

# Logging
import logging
logger = logging.getLogger('COTOWN')


# #####################################
# Database class
# #####################################

class DBClient:

  # Init
  def __init__(self, host, dbname, user, password, sshuser=None, sshpassword=None, sshprivatekey=None, schema='public'):

    self.host = host
    self.dbname = dbname
    self.user = user
    self.password = password
    self.sshuser = sshuser
    self.sshpassword = sshpassword
    self.sshprivatekey = sshprivatekey
    self.schema = schema

    self.con = None
    self.cur = None
    self.sel = None
    self.tunnel = None
   

  # Is closed?
  def closed(self):

    if self.con != None:
      return self.con.closed
    return True


  # Connect DB
  def connect(self):

    # Check if connected
    if not self.closed():
      return

    # Open SSH tunnel
    if self.sshuser is not None:
      if self.sshprivatekey is not None:
        self.tunnel = SSHTunnelForwarder(
          (self.host, 22),
          ssh_username=self.sshuser,
          ssh_pkey=self.sshprivatekey,
          remote_bind_address=('127.0.0.1', 5432)
        )
      else:
        self.tunnel = SSHTunnelForwarder(
          (self.host, 22),
          ssh_username=self.sshuser,
          ssh_password=self.sshpassword,
          remote_bind_address=('127.0.0.1', 5432)
        )
      self.tunnel.start()
 
    # Connect to DB
    self.con = psycopg2.connect(
      host="localhost",
      port=self.tunnel.local_bind_port,
      dbname=self.dbname,
      user=self.user,
      password=self.password
    )
    self.con.set_session(True)
    cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.close()


  # Autocommit
  def autocommit(self, value=True):

    self.con.commit()
    self.con.set_session(autocommit=value)


  # Disconnet DB
  def disconnect(self):

    if not self.closed():

      # Commit
      self.con.commit()

      # Close cursors
      if self.cur != None: self.cur.close()
      if self.sel != None: self.sel.close()

      # Close connection
      self.con.close()

      # Close tunnel
      self.tunnel.stop()
      self.tunnel.close()

    self.con = None
    self.tunnel = None


  # Execute SQL command
  def execute(self, sql, args=None):

    self.cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    self.cur.execute(sql, args)


  # Execute SQL command
  def executemany(self, sql, args=None):

    self.cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    self.cur.executemany(sql, args)


  # Select SQL
  def select(self, sql, args=None):

    self.sel = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    self.sel.execute(sql, args)


  # Fetch
  def fetch(self):

    return self.sel.fetchone()


  # Fetch all
  def fetchall(self):

    return self.sel.fetchall()


  # Fetch returning
  def returning(self):

    return self.cur.fetchone()


  # Commit
  def commit(self):

    self.con.commit()


  # Rollback
  def rollback(self):

    self.con.rollback()


  # Create large object
  def object(self, data):

    obj = self.con.lobject()
    obj.write(data)
    return obj.oid