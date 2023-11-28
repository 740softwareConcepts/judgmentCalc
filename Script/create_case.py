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
