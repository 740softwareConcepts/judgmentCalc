@cli.command()
@click.option('--casenumber', prompt='Enter case number', help='Case number to calculate interest')
def calculate_interest2(casenumber):
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
                    click.echo(f"{index}. Incurred Date: {liability[2]} | Amount: {liability[3]} | Description: {liability[4]} | Interest Type: {liability[6]} | Judgment Date: {liability[7]}")
                
                liability_choice = click.prompt('Enter the number of the liability to calculate interest', type=int)
                selected_liability = liabilities[liability_choice - 1] if 1 <= liability_choice <= len(liabilities) else None
                
                if selected_liability:
                    # Define start date and end date for interest calculation
                    start_date = selected_liability[2]
                    end_date = dt.today().date()

                    # Use default start date and prompt for statutory date if interest type is statutory
                    if selected_liability[6] == 'statutory':
                        statutory_date_input = click.prompt('Enter statutory date for interest calculation (YYYY-MM-DD)', default=start_date, type=str)
                        statutory_date = dt.strptime(statutory_date_input, '%Y-%m-%d').date()
                        if statutory_date < start_date:
                            click.echo("Statutory date cannot be before the incurred date.")
                            return
                        start_date = statutory_date

                    # Use judgment date if available for contractual interest before the judgment date
                    if selected_liability[6] == 'contractual' and selected_liability[7]:
                        end_date = selected_liability[7]

                    # Calculate interest based on logic
                    click.echo(f"Calculating interest for Liability ID: {selected_liability[0]} from {start_date} to {end_date}...")

                    # Fetch interest rates within the specified interval from the INTEREST table
                    cursor.execute("SELECT date, rate FROM INTEREST WHERE date BETWEEN %s AND %s", (start_date, end_date))
                    interest_rates = cursor.fetchall()
                    
                    # Perform interest calculation based on fetched rates
                    total_interest = decimal.Decimal('0.0')
                    prev_date = start_date
                    for rate_date, rate in interest_rates:
                        if rate_date > start_date:
                            days_diff = (rate_date - prev_date).days
                            rate_decimal = decimal.Decimal(str(rate)) / 365  # Convert rate to Decimal and divide by 365 for daily interest
                            interest_amount = selected_liability[3] * rate_decimal * days_diff
                            total_interest += interest_amount
                            prev_date = rate_date
                    
                    # Calculate interest for the remaining days till the end date
                    days_diff = (end_date - prev_date).days
                    rate_decimal = decimal.Decimal(str(interest_rates[-1][1])) / 365  # Convert rate to Decimal and divide by 365 for daily interest
                    interest_amount = selected_liability[3] * rate_decimal * days_diff
                    total_interest += interest_amount

                    click.echo(f"Total interest calculated: {total_interest}")

                    # Fetch involved parties from CLIENTS table
                    cursor.execute("SELECT * FROM CLIENTS WHERE caseID = %s", (case_id,))
                    involved_parties = cursor.fetchall()

                    # Display report with involved parties, liability details, and total interest
                    click.echo("\nReport:")
                    for party in involved_parties:
                        click.echo(f"Involved Party: {party[1]} {party[2]} | Type: {party[3]}")

                    click.echo(f"Liability ID: {selected_liability[0]} | Principal Amount: {selected_liability[3]} | Period: {start_date} to {end_date} | Total Interest: {total_interest}")

                else:
                    click.echo("Invalid liability choice.")

        else:
            click.echo(f"Case '{casenumber}' not found.")
    
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")