SELECT_ADMINS_QUERY = "SELECT * FROM admins WHERE login = ? AND password = ?"
SELECT_SUPERADMINS_QUERY = "SELECT * FROM super_admins WHERE login = ? AND password = ?"


SELECT_ADMIN_BY_LOGIN_QUERY = "SELECT * FROM admins WHERE login=?"
SELECT_BALANCE_BY_LOGIN_QUERY = "SELECT balance FROM admins WHERE login=?"


###########INSERT########################
INSERT_ADMIN_QUERY = """
INSERT INTO admins (login, password, balance) 
VALUES (?, ?, ?)
"""

INSERT_LOT_QUERY = """
INSERT INTO "lots" (admin_id, start_price, seller_link, geolocation, description, start_time, end_time)
VALUES ((SELECT id FROM admins WHERE login = ?), ?, ?, ?, ?, ?, ?)
"""


BUF_INSERT_LOT_QUERY= """
INSERT INTO "buf_lots" (admin_id, start_price, seller_link, geolocation, description, start_time, end_time)
VALUES ((SELECT id FROM admins WHERE login = ?), ?, ?, ?, ?, ?, ?)
"""

INSERT_IMAGE_QUERY = 'INSERT INTO images (lot_id, image_url) VALUES (?, ?)'
#################################################

