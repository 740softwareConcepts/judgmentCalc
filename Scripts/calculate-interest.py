        
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
                                click.echo(f"Interest amount: {interest_amount}")
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

                        click.echo(f"Total interest calculated: {total_interest}")


                    


                    
                    



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

