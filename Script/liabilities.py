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
