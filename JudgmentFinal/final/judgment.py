import click
import mysql.connector
from datetime import datetime as dt

# Connect to MySQL (adjust the parameters accordingly)
conn = mysql.connector.connect(
    host="database-1.ctnfprzjtuyt.us-east-1.rds.amazonaws.com",
    user="admin",
    password="Dnnbmstn1jrg",
    database="DataWarehouse"
)
cursor = conn.cursor()


@click.group()
def cli():
    """This is a 2 paragrah description of the command line tool."""
    pass 


@cli.command()
@click.option('--string', default='World', help='Tell me who to greet.')
@click.option('--repeat', default=1, help='How many times to greet.')
@click.argument('out', type=click.File('w'), default='-', required=False)
 
def say(string,repeat, out):
    """This is an exmaple command I built with the help of the quickstart guide
        This command greets you"""
    click.echo('Hello {}!'.format(string))
    name = input('Please tell me yousgsr name: ')
    for x in range(repeat):
        click.echo('Hello {}!'.format(name), file=out)
        #this file will open lazy by default, meaning it will not open until you write to it    
        #an error will mean the file will not be closed or modified
        click.echo(out)


@cli.command()
def create_case():
    case_number = click.prompt('Enter case number (2 letters, 8-10 characters)', type=str)
    if not (len(case_number) >= 8 and len(case_number) <= 10 and case_number[:2].isalpha()):
        click.echo("Case number must begin with 2 letters and have 8-10 characters.")
        return

    cursor.execute("SELECT caseNumber FROM CASES WHERE caseNumber = %s", (case_number,))
    existing_case = cursor.fetchone()
    if existing_case:
        click.echo(f"Case '{case_number}' already exists.")
        return

    # Add a record to the CASES table
    current_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO CASES (caseNumber, createDate, updateDate) VALUES (%s, %s, %s)",
                   (case_number, current_date, current_date))
    conn.commit()
    click.echo(f"Case '{case_number}' created.")

    # Get the last inserted caseID
    .0
    cursor.execute("SELECT LAST_INSERT_ID()")
    case_id = cursor.fetchone()[0]

    # Ask to add party information
    add_party_info = click.confirm('Would you like to add party information?')
    if add_party_info:
        while True:
            first_name = click.prompt('Enter first name', type=str)
            last_name = click.prompt('Enter last name', type=str)
            client_type = click.prompt('Enter type (defendant or plaintiff)', type=str,
                                       default='defendant', show_default=True)
            if client_type.lower() not in ('defendant', 'plaintiff'):
                click.echo("Type can only be 'defendant' or 'plaintiff'.")
                continue

            current_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO CLIENTS (firstName, lastName, type, caseID, createDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s)",
                           (first_name, last_name, client_type, case_id, current_date, current_date))
            conn.commit()
            click.echo(f"{client_type.capitalize()} '{first_name} {last_name}' added to the case.")

            add_more = click.confirm('Add another party?')
            if not add_more:
                break

    # Ask if they want to add a liability associated with the case
    add_liability = click.confirm('Would you like to add a liability associated with this case?')
    if add_liability:
        while True:
            while True:
                incurred_date = click.prompt('Enter incurred date (YYYY-MM-DD)', type=str)
                try:
                    dt.strptime(incurred_date, '%Y-%m-%d')
                except ValueError:
                    click.echo("Invalid date format. Please use YYYY-MM-DD format.")
                    continue
                break

            amount = click.prompt('Enter amount', type=float)
            description = click.prompt('Enter description', type=str)

            cursor.execute("INSERT INTO ACCOUNTING (caseID, type, incurredDate, amount, description) VALUES (%s, %s, %s, %s, %s)",
                           (case_id, 'liability', incurred_date, amount, description))
            conn.commit()
            click.echo("Liability added to the case.")

            add_another_liability = click.confirm('Add another liability?')
            if not add_another_liability:
                break

    # Close the connection
    conn.close()

    
@cli.command()
@click.option('--case-number', prompt='Enter case number', help='Case number to remove')
@click.confirmation_option(prompt='Are you sure you want to remove this case?')
@click.option('--remove-clients', is_flag=True, default=False, help='Remove associated clients')
@click.option('--remove-liabilities', is_flag=True, default=False, help='Remove associated liabilities')
def remove_case(case_number, remove_clients, remove_liabilities):
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")  # Disable foreign key checks

        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (case_number,))
        case_id = cursor.fetchone()

        if case_id:
            case_id = case_id[0]

            if remove_clients:
                cursor.execute("DELETE FROM CLIENTS WHERE caseID = %s", (case_id,))
                conn.commit()
                click.echo(f"All clients associated with case '{case_number}' removed.")

            if remove_liabilities:
                cursor.execute("DELETE FROM ACCOUNTING WHERE caseID = %s", (case_id,))
                conn.commit()
                click.echo(f"All liabilities associated with case '{case_number}' removed.")

            cursor.execute("DELETE FROM CASES WHERE caseID = %s", (case_id,))
            conn.commit()
            click.echo(f"Case '{case_number}' removed.")
        else:
            click.echo(f"Case '{case_number}' not found.")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")  # Re-enable foreign key checks
        conn.close()




@cli.command()
@click.option('--case-identifier', prompt='Enter case identifier', help='Case number or case ID to manage users')
@click.option('--add-user', is_flag=True, default=False, help='Add user information')
@click.option('--remove-user', is_flag=True, default=False, help='Remove user information')
@click.option('--view-users', is_flag=True, default=False, help='View users information')
def manage_users(case_identifier, add_user, remove_user, view_users):
    try:
        # Check if the provided identifier is a case number or a case ID
        if case_identifier.isdigit():  # If it's a number, consider it as a caseID
            case_id = int(case_identifier)
        else:  # Assume it's a case number
            cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (case_identifier,))
            case_id = cursor.fetchone()
            if case_id:
                case_id = case_id[0]

        if case_id:
            if add_user:
                # Code for adding user information to the CLIENTS table
                pass
            elif remove_user:
                # Code for removing user information from the CLIENTS table
                pass
            elif view_users:
                cursor.execute("SELECT firstName, lastName, type FROM CLIENTS WHERE caseID = %s", (case_id,))
                users = cursor.fetchall()
                if not users:
                    click.echo(f"No users found for case '{case_identifier}'.")
                else:
                    click.echo(f"Users associated with case '{case_identifier}':")
                    for index, user in enumerate(users, start=1):
                        click.echo(f"{index}. {user[0]} {user[1]} ({user[2]})")

        else:
            click.echo(f"Case '{case_identifier}' not found.")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()




@cli.command()
@click.option('--list-orphaned', is_flag=True, default=False, help='List orphaned entries without deletion')
@click.option('--show-attributes', is_flag=True, default=False, help='Show attributes of orphaned entries')
@click.option('--remove-orphaned', is_flag=True, default=False, help='Remove orphaned entries')
def remove_orphaned_entries(list_orphaned, show_attributes,remove_orphaned):
    try:
        if list_orphaned:
            cursor.execute("""
                SELECT c.* 
                FROM CLIENTS c
                LEFT JOIN CASES cs ON c.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_clients = cursor.fetchall()

            cursor.execute("""
                SELECT a.* 
                FROM ACCOUNTING a
                LEFT JOIN CASES cs ON a.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_accounting = cursor.fetchall()

            if not orphaned_clients and not orphaned_accounting:
                click.echo("No orphaned entries found in CLIENTS and ACCOUNTING tables.")
            else:
                click.echo("Orphaned entries found:")
                if orphaned_clients:
                    click.echo("Orphaned entries in CLIENTS table:")
                    for entry in orphaned_clients:
                        click.echo(entry)

                if orphaned_accounting:
                    click.echo("Orphaned entries in ACCOUNTING table:")
                    for entry in orphaned_accounting:
                        click.echo(entry)
        
        if show_attributes:
            cursor.execute("""
                SELECT c.* 
                FROM CLIENTS c
                LEFT JOIN CASES cs ON c.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_clients = cursor.fetchall()

            cursor.execute("""
                SELECT a.* 
                FROM ACCOUNTING a
                LEFT JOIN CASES cs ON a.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_accounting = cursor.fetchall()

            if not orphaned_clients and not orphaned_accounting:
                click.echo("No orphaned entries found in CLIENTS and ACCOUNTING tables.")
            else:
                click.echo("Orphaned entries and their attributes:")
                if orphaned_clients:
                    click.echo("Orphaned entries in CLIENTS table:")
                    for entry in orphaned_clients:
                        click.echo(f"CLIENTS entry: {entry}")

                if orphaned_accounting:
                    click.echo("Orphaned entries in ACCOUNTING table:")
                    for entry in orphaned_accounting:
                        click.echo(f"ACCOUNTING entry: {entry}")
            


        if remove_orphaned:
            cursor.execute("""
                SELECT c.caseID 
                FROM CLIENTS c
                LEFT JOIN CASES cs ON c.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_clients = cursor.fetchall()

            cursor.execute("""
                SELECT a.caseID 
                FROM ACCOUNTING a
                LEFT JOIN CASES cs ON a.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_accounting = cursor.fetchall()

            if not orphaned_clients and not orphaned_accounting:
                click.echo("No orphaned entries found in CLIENTS and ACCOUNTING tables.")
            else:
                click.echo("Orphaned entries found:")
                if orphaned_clients:
                    click.echo("Orphaned entries in CLIENTS table:")
                    for entry in orphaned_clients:
                        click.echo(f"CLIENTS entry with caseID: {entry[0]}")
                    if click.confirm('Do you want to remove orphaned CLIENTS entries?', default=True):
                        for entry in orphaned_clients:
                            cursor.execute("DELETE FROM CLIENTS WHERE caseID = %s", (entry[0],))
                        conn.commit()
                        click.echo("Orphaned CLIENTS entries deleted.")

                if orphaned_accounting:
                    click.echo("Orphaned entries in ACCOUNTING table:")
                    for entry in orphaned_accounting:
                        click.echo(f"ACCOUNTING entry with caseID: {entry[0]}")
                    if click.confirm('Do you want to remove orphaned ACCOUNTING entries?', default=True):
                        for entry in orphaned_accounting:
                            cursor.execute("DELETE FROM ACCOUNTING WHERE caseID = %s", (entry[0],))
                        conn.commit()
                        click.echo("Orphaned ACCOUNTING entries deleted.")

    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()