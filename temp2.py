
import mysql.connector
from datetime import datetime as dt
import matplotlib.pyplot as plt

# Connect to MySQL
conn = mysql.connector.connect(
    host="database-1.ctnfprzjtuyt.us-east-1.rds.amazonaws.com",
    user="admin",
    password="Dnnbmstn1jrg",
    database="DataWarehouse"
)
cursor = conn.cursor()

def case_create():
    case_number = input('Enter case number (2 letters, 8-10 characters): ')
    if not (len(case_number) >= 8 and len(case_number) <= 10 and case_number[:2].isalpha()):
        print("Case number must begin with 2 letters and have 8-10 characters.")
        return
    cursor.execute("SELECT caseNumber FROM CASES WHERE caseNumber = %s", (case_number,))
    existing_case = cursor.fetchone()
    if existing_case:
        print(f"Case '{case_number}' already exists.")
        return
    current_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO CASES (caseNumber, createDate, updateDate) VALUES (%s, %s, %s)",
                   (case_number, current_date, current_date))
    conn.commit()
    print(f"Case '{case_number}' created.")
    cursor.execute("SELECT LAST_INSERT_ID()")
    case_id = cursor.fetchone()[0]
    add_party_info = input('Would you like to add party information? (yes/no): ').lower() == 'yes'
    if add_party_info:
        while True:
            first_name = input('Enter first name: ')
            last_name = input('Enter last name: ')
            client_type = input('Enter type (defendant or plaintiff): ')
            if client_type.lower() not in ('defendant', 'plaintiff'):
                print("Type can only be 'defendant' or 'plaintiff'.")
                continue
            current_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO CLIENTS (firstName, lastName, type, caseID, createDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s)",
                           (first_name, last_name, client_type, case_id, current_date, current_date))
            conn.commit()
            print(f"{client_type.capitalize()} '{first_name} {last_name}' added to the case.")
            add_more = input('Add another party? (yes/no): ').lower() == 'yes'
            if not add_more:
                break
    add_liability = input('Would you like to add a liability associated with this case? (yes/no): ').lower() == 'yes'
    if add_liability:
        while True:
            incurred_date = input('Enter incurred date (YYYY-MM-DD): ')
            try:
                dt.strptime(incurred_date, '%Y-%m-%d')
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD format.")
                continue
            amount = float(input('Enter amount: '))
            description = input('Enter description: ')
            interest_type = input('Enter interest type (contractual or statutory): ').lower()
            while interest_type not in ('contractual', 'statutory'):
                print("Interest type can only be 'contractual' or 'statutory'.")
                interest_type = input('Enter interest type (contractual or statutory): ').lower()
            contractualinterest = None
            if interest_type == 'contractual':
                while True:
                    contractualinterest = float(input('Enter contractual interest (between 0 and 1): '))
                    if 0 <= contractualinterest <= 1:
                        break
                    else:
                        print("Contractual interest should be between 0 and 1.")
            has_judgment = input('Is there a judgment for this liability? (yes/no): ').lower() == 'yes'
            if has_judgment:
                while True:
                    judgment_date = input('Enter judgment date (YYYY-MM-DD): ')
                    try:
                        judgment_date = dt.strptime(judgment_date, '%Y-%m-%d').date()
                        break
                    except ValueError:
                        print("Invalid date format. Please use YYYY-MM-DD format.")
            cursor.execute("INSERT INTO ACCOUNTING (caseID, type, incurredDate, amount, description, interestType, interest,judgmentDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (case_id, 'liability', incurred_date, amount, description, interest_type, contractualinterest, judgment_date if has_judgment else None))
            conn.commit()
            print("Liability added to the case.")
            add_another_liability = input('Add another liability? (yes/no): ').lower() == 'yes'
            if not add_another_liability:
                break

def calculate_interest(casenumber, graphics):
    try:
        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (casenumber,))
        case_id = cursor.fetchone()

        if case_id:
            case_id = case_id[0]
            cursor.execute("SELECT * FROM ACCOUNTING WHERE caseID = %s", (case_id,))
            liabilities = cursor.fetchall()

            if not liabilities:
                print(f"No liabilities found for case '{casenumber}'.")
            else:
                print(f"Liabilities associated with case '{casenumber}':")
                for index, liability in enumerate(liabilities, start=1):
                    print(f"{index}. Incurred Date: {liability[3]} | Amount: {liability[4]} | Description: {liability[5]} | Interest Type: {liability[6]} | Judgment Date: {liability[8]}")
                liability_choice = int(input('Enter the number of the liability to calculate interest: '))
                selected_liability = liabilities[liability_choice - 1] if 1 <= liability_choice <= len(liabilities) else None
                if selected_liability:
                    start_date = selected_liability[3]

                    if selected_liability[6] == 'statutory':
                        statutory_date_input = input('Enter statutory date for interest calculation (YYYY-MM-DD): ')
                        statutory_date_end_input = input('Enter end date of term (YYYY-MM-DD): ')
                        statutory_date = dt.strptime(statutory_date_input, '%Y-%m-%d').date()
                        if statutory_date < start_date:
                            print("Statutory date cannot be before the incurred date.")
                            return
                        start_date = statutory_date
                        end_date = dt.strptime(statutory_date_end_input, '%Y-%m-%d').date()
                        cursor.execute("SELECT date, interest FROM INTEREST WHERE date BETWEEN %s AND %s", (start_date, end_date))
                        interest_rates = cursor.fetchall()
                        total_interest = 0.0
                        prev_date = start_date
                        for rate_date, rate in interest_rates:
                            if rate_date > start_date:
                                days_diff = (rate_date - prev_date).days
                                rate_decimal = rate / 365
                                interest_amount = selected_liability[4] * rate_decimal * days_diff
                                total_interest += interest_amount
                                prev_date = rate_date

                    elif selected_liability[6] == 'contractual' and selected_liability[8]:
                        accounting_interest = selected_liability[7]
                        contractual_date_input = input('Enter contractual start date for interest calculation (YYYY-MM-DD): ')
                        contractual_date_end_input = input('Enter end date of term (YYYY-MM-DD): ')
                        start_date = dt.strptime(contractual_date_input, '%Y-%m-%d').date()
                        end_date = dt.strptime(contractual_date_end_input, '%Y-%m-%d').date()
                        if start_date > end_date:
                            print("Contractual date cannot be after the end date.")
                            return
                        total_interest = 0.0
                        prev_date = start_date
                        if selected_liability[8] >= end_date:
                            days_diff = (end_date - start_date).days
                            interest_rate = accounting_interest / 365
                            interest_amount = selected_liability[4] * interest_rate * days_diff
                            total_interest += interest_amount
                            print(f"Total interest calculated: {total_interest}")
                        else:
                            prev_date = start_date
                            judgment_date = selected_liability[8]
                            if start_date < judgment_date:
                                days_diff = (judgment_date - prev_date).days
                                interest_rate = accounting_interest / 365
                                interest_amount = selected_liability[4] * interest_rate * days_diff
                                total_interest += interest_amount
                                prev_date = judgment_date
                            days_diff = (end_date - prev_date).days
                            cursor.execute("SELECT date, interest FROM INTEREST WHERE date BETWEEN %s AND %s", (prev_date, end_date))
                            interest_rates_after = cursor.fetchall()
                            for rate_date, rate in interest_rates_after:
                                days_diff = (rate_date - prev_date).days
                                rate_decimal = rate / 365
                                interest_amount = selected_liability[4] * rate_decimal * days_diff
                                print(f"Interest amount: {interest_amount}")
                                total_interest += interest_amount
                                prev_date = rate_date

                    elif selected_liability[6] == 'contractual':
                        accounting_interest = selected_liability[7]
                        contractual_date_input = input('Enter contractual start date for interest calculation (YYYY-MM-DD): ')
                        contractual_date_end_input = input('Enter end date of term (YYYY-MM-DD): ')
                        start_date = dt.strptime(contractual_date_input, '%Y-%m-%d').date()
                        end_date = dt.strptime(contractual_date_end_input, '%Y-%m-%d').date()
                        if start_date > end_date:
                            print("Contractual date cannot be after the end date.")
                            return
                        total_interest = 0.0
                        prev_date = start_date
                        days_diff = (end_date - start_date).days
                        interest_rate = accounting_interest / 365
                        interest_amount = selected_liability[4] * interest_rate * days_diff
                        total_interest += interest_amount
                        print(f"Total interest calculated: {total_interest}")

                    cursor.execute("SELECT * FROM CLIENTS WHERE caseID = %s", (case_id,))
                    involved_parties = cursor.fetchall()

                    print("\nReport:")
                    print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------")
                    for party in involved_parties:
                        print(f"Involved Party: {party[1]} {party[2]} | Type: {party[3]}")

                    print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------")
                    print(f"Liability ID: {selected_liability[0]} | Principal Amount: {selected_liability[4]} | Period: {start_date} to {end_date} | Total Interest: {total_interest}")
                    print(f"Total interest calculated: {total_interest}")
                    if graphics:
                        labels = ['Principal Amount', 'Total Interest']
                        amounts = [float(selected_liability[4]), float(total_interest)]
                        explode = (0, 0.1)
                        plt.pie(amounts, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
                        plt.axis('equal')
                        plt.title('Principal Amount vs Total Interest')
                        plt.show()
                        plt.savefig('plot.png')
                    else:
                        print("Pie chart visualization not enabled.")

                else:
                    print("Invalid liability choice.")
        else:
            print(f"Case '{casenumber}' not found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def case_update(case_number):
    try:
        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (case_number,))
        case_id = cursor.fetchone()

        if case_id:
            case_id = case_id[0]
            new_case_number = input('Enter new case number (2 letters, 8-10 characters): ')
            if not (len(new_case_number) >= 8 and len(new_case_number) <= 10 and new_case_number[:2].isalpha()):
                print("Case number must begin with 2 letters and have 8-10 characters.")
                return
            current_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE CASES SET caseNumber = %s, updateDate = %s WHERE caseID = %s",
               (new_case_number, current_date, case_id))
            conn.commit()
            print(f"Case '{case_number}' updated to '{new_case_number}' with update date {current_date}.")
        else:
            print(f"Case '{case_number}' not found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def case_remove(case_number, remove_clients, remove_liabilities):
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (case_number,))
        case_id = cursor.fetchone()
        if case_id:
            case_id = case_id[0]
            if remove_clients:
                cursor.execute("DELETE FROM CLIENTS WHERE caseID = %s", (case_id,))
                conn.commit()
                print(f"All clients associated with case '{case_number}' removed.")
            if remove_liabilities:
                cursor.execute("DELETE FROM ACCOUNTING WHERE caseID = %s", (case_id,))
                conn.commit()
                print(f"All liabilities associated with case '{case_number}' removed.")
            cursor.execute("DELETE FROM CASES WHERE caseID = %s", (case_id,))
            conn.commit()
            print(f"Case '{case_number}' removed.")
        else:
            print(f"Case '{case_number}' not found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        conn.close()

def case_search(case_number, start_date, end_date):
    try:
        query = "SELECT * FROM CASES WHERE caseNumber LIKE %s"
        params = ('%' + case_number + '%',)

        if start_date and end_date:
            query += " AND createDate BETWEEN %s AND %s"
            params += (start_date, end_date)
        elif start_date:
            query += " AND createDate >= %s"
            params += (start_date,)
        elif end_date:
            query += " AND createDate <= %s"
            params += (end_date,)

        cursor.execute(query, params)
        cases = cursor.fetchall()

        if cases:
            print("Matching cases found:")
            for case in cases:
                print(f"Case ID: {case[0]} | Case Number: {case[1]} | Create Date: {case[2]} | Update Date: {case[3]}")
        else:
            print("No matching cases found.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
       
# ... (Your existing code)

def parties(case_number, add, remove, view):
    try:
        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (case_number,))
        case_id = cursor.fetchone()

        if case_id:
            case_id = case_id[0]

            if add:
                first_name = input('Enter user first name: ')
                last_name = input('Enter user last name: ')
                user_type = input('Enter user type (defendant/plaintiff): ').lower()
                while user_type not in ['defendant', 'plaintiff']:
                    print("Invalid user type! Please enter 'defendant' or 'plaintiff'.")
                    user_type = input('Enter user type (defendant/plaintiff): ').lower()
                current_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')

                cursor.execute("INSERT INTO CLIENTS (firstName, lastName, type, caseID, updateDate) VALUES (%s, %s, %s, %s, %s)",
                               (first_name, last_name, user_type, case_id, current_date))
                conn.commit()

                print(f"User '{first_name} {last_name}' added to case '{case_number}'.")

            if remove:
                cursor.execute("SELECT firstName, lastName, type FROM CLIENTS WHERE caseID = %s", (case_id,))
                users = cursor.fetchall()
                if not users:
                    print(f"No users found for case '{case_number}'.")
                else:
                    print(f"Users associated with case '{case_number}':")
                    for index, user in enumerate(users, start=1):
                        print(f"{index}. {user[0]} {user[1]} ({user[2]})")

                    user_choice = int(input('Enter the number of the user to remove: '))
                    if 1 <= user_choice <= len(users):
                        user_to_remove = users[user_choice - 1]
                        cursor.execute("DELETE FROM CLIENTS WHERE firstName = %s AND lastName = %s AND type = %s AND caseID = %s",
                                       (user_to_remove[0], user_to_remove[1], user_to_remove[2], case_id))
                        conn.commit()
                        print(f"Removing user: {user_to_remove[0]} {user_to_remove[1]} ({user_to_remove[2]})")
                    else:
                        print("Invalid user choice.")

            if view:
                cursor.execute("SELECT firstName, lastName, type FROM CLIENTS WHERE caseID = %s", (case_id,))
                users = cursor.fetchall()
                if not users:
                    print(f"No users found for case '{case_number}'.")
                else:
                    print(f"Users associated with case '{case_number}':")
                    for index, user in enumerate(users, start=1):
                        print(f"{index}. {user[0]} {user[1]} ({user[2]})")

        else:
            print(f"Case '{case_number}' not found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()

def party_search(search_firstname, search_lastname):
    try:
        if search_firstname and search_lastname:
            cursor.execute("SELECT * FROM CLIENTS WHERE firstName LIKE %s AND lastName LIKE %s",
                           (f'%{search_firstname}%', f'%{search_lastname}%'))
        elif search_firstname:
            cursor.execute("SELECT * FROM CLIENTS WHERE firstName LIKE %s", (f'%{search_firstname}%',))
        elif search_lastname:
            cursor.execute("SELECT * FROM CLIENTS WHERE lastName LIKE %s", (f'%{search_lastname}%',))
        else:
            print("Please provide at least one search parameter.")
            return

        clients = cursor.fetchall()
        if not clients:
            print("No clients found matching the search criteria.")
        else:
            for client in clients:
                case_id = client[4]
                cursor.execute("SELECT caseNumber FROM CASES WHERE caseID = %s", (case_id,))
                case_number = cursor.fetchone()
                case_number = case_number[0] if case_number else 'Case number not found'
                print(f"Client: {client[1]} {client[2]} | Case Number: {case_number}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()
       
def orphaned_entries(list_option, show_attributes, remove_option):
    try:
        if list_option or show_attributes or remove_option:
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
                print("No orphaned entries found in CLIENTS and ACCOUNTING tables.")
            else:
                print("Orphaned entries found:")
                if orphaned_clients:
                    print("Orphaned entries in CLIENTS table:")
                    for entry in orphaned_clients:
                        print(entry)

                if orphaned_accounting:
                    print("Orphaned entries in ACCOUNTING table:")
                    for entry in orphaned_accounting:
                        print(entry)

            if show_attributes:
                print("\nAttributes of orphaned entries:")
                if orphaned_clients:
                    print("Attributes of orphaned entries in CLIENTS table:")
                    for entry in orphaned_clients:
                        print(f"CLIENTS entry: {entry}")

                if orphaned_accounting:
                    print("Attributes of orphaned entries in ACCOUNTING table:")
                    for entry in orphaned_accounting:
                        print(f"ACCOUNTING entry: {entry}")

            if remove_option:
                remove_orphaned_clients = remove_orphaned_accounting = False

                if orphaned_clients:
                    remove_orphaned_clients = input('Do you want to remove orphaned CLIENTS entries? (yes/no): ').lower() == 'yes'
                if orphaned_accounting:
                    remove_orphaned_accounting = input('Do you want to remove orphaned ACCOUNTING entries? (yes/no): ').lower() == 'yes'

                if remove_orphaned_clients or remove_orphaned_accounting:
                    cursor.execute("SET FOREIGN_KEY_CHECKS=0")

                    if remove_orphaned_clients:
                        for entry in orphaned_clients:
                            cursor.execute("DELETE FROM CLIENTS WHERE caseID = %s", (entry[0],))
                        print("Orphaned CLIENTS entries deleted.")

                    if remove_orphaned_accounting:
                        for entry in orphaned_accounting:
                            cursor.execute("DELETE FROM ACCOUNTING WHERE caseID = %s", (entry[0],))
                        print("Orphaned ACCOUNTING entries deleted.")

                    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                    conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

def main():
    while True:
        print("\Case Management System:")
        print("1. Create a new case")
        print("2. Search for a case")
        print("3. Update a case")
        print("4. Remove a case")
        print("5. Calculate interest for a case")
        print("6. Manage parties for a case")
        print("7. Search for parties")
        print("8. Check for orphaned entries")
        print("9. Quit")

        choice = input("Enter your choice (1-9): ")

        if choice == "1":
            case_create()
        elif choice == "2":
            case_number = input("Enter case number to search: ")
            start_date = input("Enter start date (YYYY-MM-DD) for search (optional): ")
            end_date = input("Enter end date (YYYY-MM-DD) for search (optional): ")
            case_search(case_number, start_date, end_date)
        elif choice == "3":
            case_number = input("Enter case number to update: ")
            case_update(case_number)
        elif choice == "4":
            case_number = input("Enter case number to remove: ")
            remove_clients = input("Remove associated clients? (yes/no): ").lower() == "yes"
            remove_liabilities = input("Remove associated liabilities? (yes/no): ").lower() == "yes"
            case_remove(case_number, remove_clients, remove_liabilities)
        elif choice == "5":
            case_number = input("Enter case number to calculate interest: ")
            graphics = input("Enable graphics for interest calculation? (yes/no): ").lower() == "yes"
            calculate_interest(case_number, graphics)
        elif choice == "6":
            case_number = input("Enter case number to manage parties: ")
            add = input("Add parties? (yes/no): ").lower() == "yes"
            remove = input("Remove parties? (yes/no): ").lower() == "yes"
            view = input("View parties? (yes/no): ").lower() == "yes"
            parties(case_number, add, remove, view)
        elif choice == "7":
            search_firstname = input("Enter first name for party search (optional): ")
            search_lastname = input("Enter last name for party search (optional): ")
            party_search(search_firstname, search_lastname)
        elif choice == "8":
            list_orphaned = input("List orphaned entries? (yes/no): ").lower() == "yes"
            show_attributes = input("Show attributes of orphaned entries? (yes/no): ").lower() == "yes"
            remove_orphaned = input("Remove orphaned entries? (yes/no): ").lower() == "yes"
            orphaned_entries(list_orphaned, show_attributes, remove_orphaned)
        elif choice == "9":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

if __name__ == "__main__":
    main()

