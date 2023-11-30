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
def case_create():
    """This is a mini documenation for the command"""
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
            interest_type = click.prompt('Enter interest type (contractual or statutory)', type=str,
                                     default='contractual', show_default=True)
            while interest_type.lower() not in ('contractual', 'statutory'):
                click.echo("Interest type can only be 'contractual' or 'statutory'.")
                interest_type = click.prompt('Enter interest type (contractual or statutory)', type=str,
                                         default='contractual', show_default=True)
            contractualinterest = None  # Initialize contractualinterest variable

            if interest_type.lower() == 'contractual':
                while True:
                    contractualinterest = click.prompt('Enter contractual interest (between 0 and 1)', type=float)
                    if 0 <= contractualinterest <= 1:
                        break
                    else:
                        click.echo("Contractual interest should be between 0 and 1.")
            has_judgment = click.confirm('Is there a judgment for this liability?')
            if has_judgment:
                while True:
                    judgment_date = click.prompt('Enter judgment date (YYYY-MM-DD)', type=str)
                    try:
                        judgment_date = dt.strptime(judgment_date, '%Y-%m-%d').date()
                        break
                    except ValueError:
                        click.echo("Invalid date format. Please use YYYY-MM-DD format.")            
            cursor.execute("INSERT INTO ACCOUNTING (caseID, type, incurredDate, amount, description, interestType, interest,judgmentDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (case_id, 'liability', incurred_date, amount, description, interest_type, contractualinterest, judgment_date if has_judgment else None))
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
def case_remove(case_number, remove_clients, remove_liabilities):
    """This is a mini documenation for the command"""
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





@cli.command()
@click.option('--list', is_flag=True, default=False, help='List orphaned entries without deletion')
@click.option('--show-attributes', is_flag=True, default=False, help='Show attributes of orphaned entries')
@click.option('--remove', is_flag=True, default=False, help='Remove orphaned entries')
def orphaned_entries(list, show_attributes,remove):
    """This is a mini documenation for the command"""
    try:
        if list:
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



        if remove:
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


@cli.command()
@click.option('--case-number', prompt='Enter case number to update', help='Case number to update')
def case_update(case_number):
    try:
        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (case_number,))
        case_id = cursor.fetchone()

        if case_id:
            case_id = case_id[0]

            new_case_number = click.prompt('Enter new case number (2 letters, 8-10 characters)', type=str)
            if not (len(new_case_number) >= 8 and len(new_case_number) <= 10 and new_case_number[:2].isalpha()):
                click.echo("Case number must begin with 2 letters and have 8-10 characters.")
                return

            current_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE CASES SET caseNumber = %s, updateDate = %s WHERE caseID = %s",
                           (new_case_number, current_date, case_id))
            conn.commit()
            click.echo(f"Case '{case_number}' updated to '{new_case_number}' with update date {current_date}.")
        else:
            click.echo(f"Case '{case_number}' not found.")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()

@cli.command()
@click.option('--case-number', prompt='Enter partial case number to search', help='Partial case number to search')
@click.option('--start-date', help='Start date (YYYY-MM-DD) to filter cases')
@click.option('--end-date', help='End date (YYYY-MM-DD) to filter cases')
def case_search(case_number, start_date, end_date):
    try:
        query = "SELECT * FROM CASES WHERE caseNumber LIKE %s"
        params = ('%' + case_number + '%',)

        if start_date and end_date:
            start_datetime = dt.strptime(start_date, '%Y-%m-%d')
            end_datetime = dt.strptime(end_date, '%Y-%m-%d')
            query += " AND createDate BETWEEN %s AND %s"
            params += (start_datetime, end_datetime)

        cursor.execute(query, params)
        cases = cursor.fetchall()

        if cases:
            click.echo("Matching cases:")
            for case in cases:
                # Display the case details, modify this part based on your table structure
                click.echo(f"Case Number: {case[1]}")  # Assuming caseNumber is at index 1
                click.echo(f"Create Date: {case[2]}")  # Assuming createDate is at index 2
                click.echo(f"Update Date: {case[3]}")  # Assuming updateDate is at index 3
                # Add other attributes as needed
        else:
            click.echo(f"No matching cases found.")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()

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