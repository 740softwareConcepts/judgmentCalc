
@cli.command()
@click.option('--search-firstname', help='Search users by first name')
@click.option('--search-lastname', help='Search users by last name')
def party_search(search_firstname, search_lastname):
    '''Search clients by first or last name'''
    try:
        if search_firstname and search_lastname:
            cursor.execute("SELECT * FROM CLIENTS WHERE firstName LIKE %s AND lastName LIKE %s",
                           (f'%{search_firstname}%', f'%{search_lastname}%'))
        elif search_firstname:
            cursor.execute("SELECT * FROM CLIENTS WHERE firstName LIKE %s", (f'%{search_firstname}%',))
        elif search_lastname:
            cursor.execute("SELECT * FROM CLIENTS WHERE lastName LIKE %s", (f'%{search_lastname}%',))
        else:
            click.echo("Please provide at least one search parameter.")
            return

        clients = cursor.fetchall()
        if not clients:
            click.echo("No clients found matching the search criteria.")
        else:
            for client in clients:
                case_id = client[4]  # Assuming the caseID is at index 3 in the result tuple
                cursor.execute("SELECT caseNumber FROM CASES WHERE caseID = %s", (case_id,))
                case_number = cursor.fetchone()
                case_number = case_number[0] if case_number else 'Case number not found'
                click.echo(f"Client: {client[1]} {client[2]} | Case Number: {case_number}")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()        