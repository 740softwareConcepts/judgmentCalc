




def user(action):  
    """Here you can add remove or update a user"""  
    if action == 'add':
        name = click.prompt('Plese enter the name of the user :')
        last_name = click.prompt('Please enter the last name of the user: ')
        dob= click.prompt('Please enter the date of birth of the user (YYYY-MM-DD): ')
        create_date = dt.datetime.now().strftime('%Y-%m-%d')
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Clients (Name, LastName, DOB, CreateDate) VALUES (%s, %s, %s, %s)",
            (name, last_name, dob, create_date)
        )
        connection.commit()
        click.echo("Client added successfully!")
    elif action == 'remove':
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Clients WHERE ClientID = %s", (client_id,))
        connection.commit()
        click.echo(f"Client with ID {client_id} removed successfully!")
    elif action == 'update':
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE Clients SET Name = %s, LastName = %s, DOB = %s, CreateDate = %s WHERE ClientID = %s",
            (name, last_name, dob, create_date, client_id)
        )
        connection.commit()
        click.echo(f"Client with ID {client_id} updated successfully!")



def user2(action, name, last_name, dob, create_date, client_id):
    if action == 'add':
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Clients (Name, LastName, DOB, CreateDate) VALUES (%s, %s, %s, %s)",
            (name, last_name, dob, create_date)
        )
        connection.commit()
        click.echo("Client added successfully!")
    elif action == 'remove':
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Clients WHERE ClientID = %s", (client_id,))
        connection.commit()
        click.echo(f"Client with ID {client_id} removed successfully!")
    elif action == 'update':
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE Clients SET Name = %s, LastName = %s, DOB = %s, CreateDate = %s WHERE ClientID = %s",
            (name, last_name, dob, create_date, client_id)
        )
        connection.commit()
        click.echo(f"Client with ID {client_id} updated successfully!")
