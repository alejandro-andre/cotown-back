# #####################################
# Imports
# #####################################

from sshtunnel import SSHTunnelForwarder
import psycopg2
import psycopg2.pool
import psycopg2.extras

# #####################################
# Database class
# #####################################

class DBClient:

  # Init
  def __init__(self, host, port, dbname, user, password, sshuser=None, sshpassword=None, sshprivatekey=None, schema='public', readonly=False ):

    self.host = host
    self.port = port
    self.dbname = dbname
    self.user = user
    self.password = password
    self.sshuser = sshuser
    self.sshpassword = sshpassword
    self.sshprivatekey = sshprivatekey
    self.schema = schema
    self.readonly = readonly

    self.tunnel = None
    self.pool = None
    self.autocommit = False

    
  # Is closed?
  def closed(self):

    return self.pool == None


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
      self.port = self.tunnel.local_bind_port
      self.host='localhost'

    # Connect to DB using pool
    self.pool = psycopg2.pool.SimpleConnectionPool(
      1, 
      20, 
      host=self.host,
      port=self.port,
      dbname=self.dbname, 
      user=self.user, 
      password=self.password
    )
    

  # Disconnet DB
  def disconnect(self):

    if not self.closed():

      # Close connection
      self.pool.closeall()

      # Close tunnel
      if self.tunnel:
        self.tunnel.stop()
        self.tunnel.close()

    self.pool = None
    self.tunnel = None


  # Get a connection from the pool
  def getconn(self):

    con = self.pool.getconn()
    con.set_session(autocommit=self.autocommit, readonly=self.readonly)
    return con


  # Free pool connection
  def putconn(self, con):

    con.commit()
    self.pool.putconn(con)


  # Execute SQL command
  def execute(self, con, sql, args=None):

    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql, args)
    return cur


  # Execute SQL many command
  def executemany(self, con, sql, args=None):

    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.executemany(sql, args)
    return cur


  # Copy from
  def copy_from(self, con, data, schema, table, columns, null, sep):

    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f'SET search_path = {schema}, public')
    cur.copy_from(data, table, null=null, columns=columns, sep=sep)
    cur.close()


  # Create large object
  def object(self, con, data):

    obj = con.lobject()
    obj.write(data)
    return obj.oid