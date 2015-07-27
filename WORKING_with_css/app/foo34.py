import psycopg2
import psycopg2.extras
def doThis():
	conn = psycopg2.connect("dbname=tweet user=jinnyhyunjikim")
	cur = conn.cursor()	
	psycopg2.extras.register_hstore(conn)
	# statement = "insert into question (question_id, subject, question location) values (1000, 'subject a ', 'question text a', {'this':'a', 'that':'b',});"
	
	values = "(1000, 'subject a ', 'question text a', %s)"
	statement = "insert into question (question_id, subject, question, location) values %s; " %(values) 
	hstore = {'this':'a', 'that':'bbb',}
	print statement
	cur.execute(statement, [hstore])

	conn.commit()
	cur.close()
	conn.close()

doThis()