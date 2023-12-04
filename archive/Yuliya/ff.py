

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
                            cursor.execute("SELECT date, rate FROM INTEREST WHERE date BETWEEN %s AND %s", (statutory_start_date, end_date))
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
                        cursor.execute("SELECT date, rate FROM INTEREST WHERE date BETWEEN %s AND %s", (start_date, end_date))
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



