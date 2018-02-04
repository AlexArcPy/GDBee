'''Configuration parameters to start application with'''

# define if application starts with a tab created with the geodatabase
# and query executed with the result table drawn
# set to False when running unit tests
dev_mode = False
test_mode = False

project_name = 'GDBee'
not_connected_to_gdb_message = 'Not connected to any geodatabase...'

sql_dialects_names = ['SQLite', 'OGRSQL'] # SQLite is used by default
