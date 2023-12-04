
@cli.command()
@click.option('--case-number', prompt='Enter case number', help='Case number to manage party information')
@click.option('--add', is_flag=True, default=False, help='Add party information by Case Number')
@click.option('--remove', is_flag=True, default=False, help='Remove party information by Case Number')
@click.option('--view', is_flag=True, default=False, help='View party information by Case Number')
def parties(case_number, add, remove, view):
    '''This is a mini documenation for the command'''
    try:
        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (case_number,))
        case_id = cursor.fetchone()

        if case_id:
            case_id = case_id[0]

            if add:
                first_name = click.prompt('Enter user first name', type=str)
                last_name = click.prompt('Enter user last name', type=str)
                user_type = click.prompt('Enter user type (defendant/plaintiff)', type=str,
                                         default='defendant', show_default=True)
                while user_type.lower() not in ['defendant', 'plaintiff']:
                    click.echo("Invalid user type! Please enter 'defendant' or 'plaintiff'.")
                    user_type = click.prompt('Enter user type (defendant/plaintiff)', type=str,
                                             default='defendant', show_default=True)
                current_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute("INSERT INTO CLIENTS (firstName, lastName, type, caseID, updateDate) VALUES (%s, %s, %s, %s, %s)",
                               (first_name, last_name, user_type, case_id, current_date))
                conn.commit()

                click.echo(f"User '{first_name} {last_name}' added to case '{case_number}'.")

            if remove:
                cursor.execute("SELECT firstName, lastName, type FROM CLIENTS WHERE caseID = %s", (case_id,))
                users = cursor.fetchall()
                if not users:
                    click.echo(f"No users found for case '{case_number}'.")
                else:
                    click.echo(f"Users associated with case '{case_number}':")
                    for index, user in enumerate(users, start=1):
                        click.echo(f"{index}. {user[0]} {user[1]} ({user[2]})")

                    user_choice = click.prompt('Enter the number of the user to remove', type=int)
                    if 1 <= user_choice <= len(users):
                        user_to_remove = users[user_choice - 1]
                        cursor.execute("DELETE FROM CLIENTS WHERE firstName = %s AND lastName = %s AND type = %s AND caseID = %s",
                                       (user_to_remove[0], user_to_remove[1], user_to_remove[2], case_id))
                        conn.commit()
                        click.echo(f"Removing user: {user_to_remove[0]} {user_to_remove[1]} ({user_to_remove[2]})")
                    else:
                        click.echo("Invalid user choice.")

            if view:
                cursor.execute("SELECT firstName, lastName, type FROM CLIENTS WHERE caseID = %s", (case_id,))
                users = cursor.fetchall()
                if not users:
                    click.echo(f"No users found for case '{case_number}'.")
                else:
                    click.echo(f"Users associated with case '{case_number}':")
                    for index, user in enumerate(users, start=1):
                        click.echo(f"{index}. {user[0]} {user[1]} ({user[2]})")
            
        else:
            click.echo(f"Case '{case_number}' not found.")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()
