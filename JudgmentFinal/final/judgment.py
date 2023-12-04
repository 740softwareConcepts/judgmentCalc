import click
import mysql.connector
from datetime import datetime as dt
from datetime import timedelta
import decimal
import matplotlib.pyplot as plt


# Connect to MySQL
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
    """This command creates a new case."""
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
    """This command removes a case."""
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
    '''This command manages party information by case number'''
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
                        #add break line
                        click.echo("--------------------------------------------------")
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
    """this command finds orphaned entries in the CLIENTS and ACCOUNTING tables"""
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
    '''This command updates case by case number'''
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
    '''Search cases by case number and/or date range'''
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
                click.echo("--------------------------------------------------")
                # Display the case details
                click.echo(f"CASE NUMBER: {case[1]}")  
                click.echo(f"caseID {case[0]}" )  
                click.echo(f"Create Date: {case[2]}")  
                click.echo(f"Update Date: {case[3]}")  
                #BREAK LINE


             
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
                case_id = client[4] 
                cursor.execute("SELECT caseNumber FROM CASES WHERE caseID = %s", (case_id,))
                case_number = cursor.fetchone()
                case_number = case_number[0] if case_number else 'Case number not found'
                #add break line
                click.echo("--------------------------------------------------")
                click.echo(f"Client: {client[1]} {client[2]} | Case Number: {case_number}")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()        


@cli.command()
@click.option('--add', is_flag=True, default=False, help='Add liabilities by case number')
@click.option('--remove', is_flag=True, default=False, help='Remove liabilities by case number')
@click.option('--view', is_flag=True, default=False, help='View liabilities by case number')
@click.option('--judgment-date', is_flag=True, default=False, help='Update judgment date for existing liability')
@click.option('--case-number', help='Specify case number')
def liabilities(add, remove, view, case_number, judgment_date):
    '''Manage liabilities by case number'''
    try:
        case_number = click.prompt('Enter case number (2 letters, 8-10 characters)', type=str)
        if not (len(case_number) >= 8 and len(case_number) <= 10 and case_number[:2].isalpha()):
            click.echo("Invalid case number. It should start with 2 letters and have 8-10 characters.")
            return

        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (case_number,))
        case_id = cursor.fetchone()

        if case_id:
            case_id = case_id[0]

            if add:
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

                  

            elif remove:
                # Remove liabilities associated with the case
                cursor.execute("SELECT * FROM ACCOUNTING WHERE caseID = %s", (case_id,))
                liabilities = cursor.fetchall()
                if not liabilities:
                    click.echo(f"No liabilities found for case '{case_number}'.")
                else:
                    click.echo(f"Liabilities associated with case '{case_number}':")
                    for index, liability in enumerate(liabilities, start=1):
                        click.echo(f"{index}. {liability[0]} - {liability[2]}, {liability[3]}, {liability[4]},{liability[5]}")
                    liability_choice = click.prompt('Enter the number of the liability to remove', type=int)
                    if 1 <= liability_choice <= len(liabilities):
                        liability_to_remove = liabilities[liability_choice - 1]
                        cursor.execute("DELETE FROM ACCOUNTING WHERE accountingID = %s AND caseID = %s",
                                       (liability_to_remove[0], case_id))
                        conn.commit()
                        click.echo(f"Removing liability: {liability_to_remove[0]} - {liability_to_remove[2]} - {liability_to_remove[3]} - {liability_to_remove[4]} - {liability_to_remove[5]}")
                    else:
                        click.echo("Invalid liability choice.")
            elif view:
                # View liabilities associated with the case
                cursor.execute("SELECT * FROM ACCOUNTING WHERE caseID = %s", (case_id,))
                liabilities = cursor.fetchall()
                if not liabilities:
                    click.echo("No liabilities found for this case.")
                else:
                    click.echo(f"Liabilities associated with case '{case_number}':")
                    #add break line
                    click.echo("-------------------------------------------------------------------------------------------------------------------------------------------------------------------")
                    # Display attribute titles
                    attributes = [desc[0] for desc in cursor.description]
                    click.echo(attributes)
                    # Display liabilities
                    for liability in liabilities:
                        click.echo(liability)
            elif judgment_date:
                # Update judgment date for existing liability
                cursor.execute("SELECT * FROM ACCOUNTING WHERE caseID = %s", (case_id,))
                liabilities = cursor.fetchall()
                if not liabilities:
                    click.echo("No liabilities found for this case.")
                else:
                    click.echo(f"Liabilities associated with case '{case_number}':")
                    for index, liability in enumerate(liabilities, start=1):
                        click.echo(f"{index}. {liability[0]} - {liability[2]}, {liability[3]}, {liability[4]},{liability[5]}")
                    
                    liability_choice = click.prompt('Enter the number of the liability to update judgment date', type=int)
                    if 1 <= liability_choice <= len(liabilities):
                        liability_to_update = liabilities[liability_choice - 1]
                        new_judgment_date = click.prompt('Enter new judgment date (YYYY-MM-DD)', type=str)
                        try:
                            new_judgment_date = dt.strptime(new_judgment_date, '%Y-%m-%d').date()
                            cursor.execute("UPDATE ACCOUNTING SET judgmentDate = %s WHERE accountingID = %s",
                                           (new_judgment_date, liability_to_update[0]))
                            conn.commit()
                            click.echo(f"Updated judgment date for liability: {liability_to_update[0]}")
                        except ValueError:
                            click.echo("Invalid date format. Please use YYYY-MM-DD format.")
                    else:
                        click.echo("Invalid liability choice.")
            else:
                click.echo("Please specify an action: add, remove, or view liabilities.")

        else:
            click.echo(f"Case '{case_number}' not found.")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()        







        
@cli.command()
@click.option('--casenumber', prompt='Enter case number', help='Case number to calculate interest')
@click.option('--graphics', is_flag=True, help='Enable pie chart visualization')
def calculate_interest(casenumber, graphics):
    '''Calculate interest for a liability'''

    try:
        # Retrieve case ID based on the provided case number
        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (casenumber,))
        case_id = cursor.fetchone()

        if case_id:
            case_id = case_id[0]

            # Fetch liabilities related to the given case number
            cursor.execute("SELECT * FROM ACCOUNTING WHERE caseID = %s", (case_id,))
            liabilities = cursor.fetchall()

            if not liabilities:
                click.echo(f"No liabilities found for case '{casenumber}'.")
            else:
                click.echo(f"Liabilities associated with case '{casenumber}':")
                for index, liability in enumerate(liabilities, start=1):
                    click.echo(f"{index}. Incurred Date: {liability[3]} | Amount: {liability[4]} | Description: {liability[5]} | Interest Type: {liability[6]} | Judgment Date: {liability[8]}")
                
                liability_choice = click.prompt('Enter the number of the liability to calculate interest', type=int)
                selected_liability = liabilities[liability_choice - 1] if 1 <= liability_choice <= len(liabilities) else None
                
                if selected_liability:
                    # Define start date and end date for interest calculation
                    start_date = selected_liability[3]
                    

                    # Use default start date and prompt for statutory date if interest type is statutory
                    if selected_liability[6] == 'statutory':
                        statutory_date_input = click.prompt('Enter statutory date for interest calculation (YYYY-MM-DD)', default=start_date, type=str)
                        statutory_date_end_input = click.prompt('Enter end date of term (YYYY-MM-DD)', default=dt.today().strftime('%Y-%m-%d'), type=str)
                        statutory_date = dt.strptime(statutory_date_input, '%Y-%m-%d').date()
                        if statutory_date < start_date:
                            click.echo("Statutory date cannot be before the incurred date.")
                            return
                        start_date = statutory_date
                        end_date = statutory_date_end_input
                            # Fetch interest rates within the specified interval from the INTEREST table
                        cursor.execute("SELECT date, interest FROM INTEREST WHERE date BETWEEN %s AND %s", (start_date, end_date))
                        interest_rates = cursor.fetchall()
                                        
                        # Perform interest calculation based on fetched rates
                        total_interest = decimal.Decimal('0.0')
                        prev_date = start_date
                        for rate_date, rate in interest_rates:
                            if rate_date > start_date:
                                days_diff = (rate_date - prev_date).days
                                rate_decimal = decimal.Decimal(str(rate)) / 365  # Convert rate to Decimal
                                interest_amount = selected_liability[4] * rate_decimal * days_diff
                                total_interest += interest_amount
                                prev_date = rate_date
                                        

                    elif selected_liability[6] == 'contractual' and selected_liability[8]:
                        accounting_interest = decimal.Decimal(str(selected_liability[7]))

                        # Define start date and end date for interest calculation
                        contractual_date_input = click.prompt('Enter contractual start date for interest calculation (YYYY-MM-DD)', default=start_date, type=str)
                        contractual_date_end_input = click.prompt('Enter end date of term (YYYY-MM-DD)', default=dt.today().strftime('%Y-%m-%d'), type=str)

                        # Validate date inputs
                        start_date = dt.strptime(contractual_date_input, '%Y-%m-%d').date()
                        end_date = dt.strptime(contractual_date_end_input, '%Y-%m-%d').date()

                        if start_date > end_date:
                            click.echo("Contractual date cannot be after the end date.")
                            return

                        # Calculate interest based on accounting interest before judgment date
                        total_interest = decimal.Decimal('0.0')
                        prev_date = start_date

                        # If judgment date exists, split the interest calculation
                        if selected_liability[8] >= end_date:
                            accounting_interest = decimal.Decimal(str(selected_liability[7]))
                            # Calculate interest based on accounting interest
                    
                        
                            days_diff = (end_date - start_date).days

                            interest_rate = accounting_interest / 365
                            interest_amount = selected_liability[4] * interest_rate * days_diff
                            total_interest += interest_amount

                            click.echo(f"Total interest calculated: {total_interest}")
                        else:
                    
                            prev_date = start_date

                            # If judgment date exists, split the interest calculation
                            
                            judgment_date = selected_liability[8]
                            if start_date < judgment_date:
                                days_diff = (judgment_date - prev_date).days
                                interest_rate = accounting_interest / 365
                                interest_amount = selected_liability[4] * interest_rate * days_diff
                                total_interest += interest_amount
                                prev_date = judgment_date

                            # Calculate interest based on statutory rates after judgment date
                            days_diff = (end_date - prev_date).days
                            cursor.execute("SELECT date, interest FROM INTEREST WHERE date BETWEEN %s AND %s", (prev_date, end_date))
                            interest_rates_after = cursor.fetchall()

                            for rate_date, rate in interest_rates_after:
                                days_diff = (rate_date - prev_date).days
                                rate_decimal = decimal.Decimal(str(rate)) / 365  # Convert rate to Decimal
                                interest_amount = selected_liability[4] * rate_decimal * days_diff
                                total_interest += interest_amount
                                prev_date = rate_date


                    

                    elif selected_liability[6] == 'contractual':
                        accounting_interest = decimal.Decimal(str(selected_liability[7]))

                        # Define start date and end date for interest calculation
                        contractual_date_input = click.prompt('Enter contractual start date for interest calculation (YYYY-MM-DD)', default=start_date, type=str)
                        contractual_date_end_input = click.prompt('Enter end date of term (YYYY-MM-DD)', default=dt.today().strftime('%Y-%m-%d'), type=str)
                        
                        # Validate date inputs
                        start_date = dt.strptime(contractual_date_input, '%Y-%m-%d').date()
                        end_date = dt.strptime(contractual_date_end_input, '%Y-%m-%d').date()
                        if start_date > end_date:
                            click.echo("Contractual date cannot be after the end date.")
                            return   

                        # Calculate interest based on accounting interest
                        total_interest = decimal.Decimal('0.0')
                        prev_date = start_date
                        days_diff = (end_date - start_date).days

                        interest_rate = accounting_interest / 365
                        interest_amount = selected_liability[4] * interest_rate * days_diff
                        total_interest += interest_amount

                        


                    


                    
                    



                    # Fetch involved parties from CLIENTS table
                    cursor.execute("SELECT * FROM CLIENTS WHERE caseID = %s", (case_id,))
                    involved_parties = cursor.fetchall()

                    # Display report with involved parties, liability details, and total interest
                    click.echo("\nReport:")
                    #add break line
                    click.echo("-------------------------------------------------------------------------------------------------------------------------------------------------------------------")
                    for party in involved_parties:
                        click.echo(f"Involved Party: {party[1]} {party[2]} | Type: {party[3]}")

                    #add break line
                    click.echo("-------------------------------------------------------------------------------------------------------------------------------------------------------------------")
                    click.echo(f"Liability ID: {selected_liability[0]} | Principal Amount: {selected_liability[4]} | Period: {start_date} to {end_date} | Total Interest: {total_interest}")
                    click.echo(f"Total interest calculated: {total_interest}")
                    if graphics:
                    # Create a pie chart for total interest and principal amount
                        labels = ['Principal Amount', 'Total Interest']
                        amounts = [float(selected_liability[4]), float(total_interest)]
                        explode = (0, 0.1)  # "explode" the Total Interest slice

                       
                        plt.pie(amounts, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
                        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                        plt.title('Principal Amount vs Total Interest')
                        plt.show()
                        (plt.savefig('plot.png'))

                    else:
                        click.echo("Pie chart visualization not enabled.")
                                
                
                else:
                    click.echo("Invalid liability choice.")

        else:
            click.echo(f"Case '{casenumber}' not found.")
    
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")



@cli.command()
@click.option('--casenumber', prompt='Enter case number', help='Case number to generate interest report')
def generate_interest_report(casenumber):
    '''Generate interest report for a case'''

    try:
        # Retrieve case ID based on the provided case number
        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (casenumber,))
        case_id = cursor.fetchone()

        if case_id:
            case_id = case_id[0]

            # Fetch all involved parties related to the given case number
            cursor.execute("SELECT * FROM CLIENTS WHERE caseID = %s", (case_id,))
            parties = cursor.fetchall()

            # Fetch liabilities related to the given case number
            cursor.execute("SELECT accountingID, incurredDate, amount, description, interest, judgmentDate, interestType FROM ACCOUNTING WHERE caseID = %s", (case_id,))
            liabilities = cursor.fetchall()

            if not liabilities:
                click.echo(f"No liabilities found for case '{casenumber}'.")
            else:
                click.echo(f"Generating interest report for case '{casenumber}'...")

                # Display involved parties
                click.echo("Involved Parties:")
                for party in parties:
                    click.echo(f"- {party[1]} {party[2]} | Type: {party[3]}")

                # Initialize variables for report
                report_data = []
                total_interest = decimal.Decimal('0.0')

                for index, liability in enumerate(liabilities, start=1):
                    report_entry = {
                        'Liability ID': liability[0],
                        'Incurred Date': liability[1],
                        'Principal Amount': liability[2],
                        'Cause of Action': liability[3],
                        'Segments': [],
                        'Subtotal Interest': decimal.Decimal('0.0')  # Subtotal interest for each liability
                    }

                    start_date = liability[1]
                    end_date = liability[5] if liability[5] else dt.today().date()
                    

                    if liability[6] == 'contractual' and liability[4] and liability[5]:
                        # Calculate contractual interest until judgmentDate
                        judgment_date = liability[5]
                        interest_amount = liability[2] * liability[4] * ((judgment_date - start_date).days) / 365
                        total_interest += interest_amount
                        report_entry['Segments'].append({
                            'Rate': liability[4],
                            'Start Date': start_date,
                            'End Date': judgment_date,
                            'Interest Amount': interest_amount
                        })

                        # Calculate statutory interest after judgmentDate
                        statutory_start_date = judgment_date
                        if statutory_start_date < end_date:
                            # Fetch interest rates from INTEREST table for statutory interest calculation
                            cursor.execute("SELECT date, interest FROM INTEREST WHERE date BETWEEN %s AND %s", (statutory_start_date, end_date))
                            interest_rates = cursor.fetchall()

                            prev_date = statutory_start_date
                            for rate_date, rate in interest_rates:
                                days_diff = (rate_date - prev_date).days
                                rate_decimal = decimal.Decimal(str(rate))
                                interest_amount = liability[2] * rate_decimal * days_diff
                                total_interest += interest_amount
                                report_entry['Segments'].append({
                                    'Rate': rate,
                                    'Start Date': prev_date,
                                    'End Date': rate_date,
                                    'Interest Amount': interest_amount
                                })
                                prev_date = rate_date

                            # Calculate interest for remaining days till end_date
                            days_diff = (end_date - prev_date).days
                            rate_decimal = decimal.Decimal(str(interest_rates[-1][1]))
                            interest_amount = liability[2] * rate_decimal * days_diff
                            total_interest += interest_amount
                            report_entry['Segments'].append({
                                'Rate': interest_rates[-1][1],
                                'Start Date': prev_date,
                                'End Date': end_date,
                                'Interest Amount': interest_amount
                            })

                    elif liability[6] == 'contractual' and liability[4] and not liability[5]:
                        # Handle case where judgmentDate is not provided (contractual interest without judgment)
                        interest_amount = liability[2] * liability[4] * ((end_date - start_date).days) / 365
                        total_interest += interest_amount
                        report_entry['Segments'].append({
                            'Rate': liability[4],
                            'Start Date': start_date,
                            'End Date': end_date,
                            'Interest Amount': interest_amount
                        })
                    else:
                        # Fetch interest rates within the specified interval from the INTEREST table
                        cursor.execute("SELECT date, interest FROM INTEREST WHERE date BETWEEN %s AND %s", (start_date, end_date))
                        interest_rates = cursor.fetchall()

                        prev_date = start_date
                        for rate_date, rate in interest_rates:
                            if rate_date > start_date:
                                days_diff = (rate_date - prev_date).days
                                rate_decimal = decimal.Decimal(str(rate))/100  # Convert rate to Decimal
                                interest_amount = liability[2] * rate_decimal * days_diff
                                total_interest += interest_amount
                                report_entry['Segments'].append({
                                    'Rate': rate,
                                    'Start Date': prev_date,
                                    'End Date': rate_date,
                                    'Interest Amount': interest_amount
                                })
                                prev_date = rate_date

                        # Calculate interest for the remaining days till the end date
                        days_diff = (end_date - prev_date).days
                        rate_decimal = decimal.Decimal(str(interest_rates[-1][1]))/100  # Convert rate to Decimal
                        interest_amount = liability[2] * rate_decimal * days_diff
                        total_interest += interest_amount
                        report_entry['Segments'].append({
                            'Rate': interest_rates[-1][1],
                            'Start Date': prev_date,
                            'End Date': end_date,
                            'Interest Amount': interest_amount
                        })
                    
                    report_data.append(report_entry)

                # Display the report
                click.echo("\nLiabilities with Interest Segments:")
                for entry in report_data:
                    click.echo(f"Liability ID: {entry['Liability ID']} | Incurred Date: {entry['Incurred Date']} | Principal Amount: {entry['Principal Amount']} | Cause of Action: {entry['Cause of Action']}")
                    for segment in entry['Segments']:
                        click.echo(f"   - Rate: {segment['Rate']} | Start Date: {segment['Start Date']} | End Date: {segment['End Date']} | Interest Amount: {segment['Interest Amount']}")

                # Display total interest calculated for the case
                click.echo(f"\nTotal Interest for Case '{casenumber}': {total_interest}")

        else:
            click.echo(f"Case '{casenumber}' not found.")
    
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")

